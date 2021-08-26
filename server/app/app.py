import asyncio
import importlib
import logging
import os.path
import typing
from collections import defaultdict
from typing import Any, Protocol, runtime_checkable

import tornado.web
from rich.logging import RichHandler
from tornado.platform.asyncio import BaseAsyncIOLoop

from .modules.websocket import WebSocketHandler
from .utils.database import Database
from .utils.token import Tokens


logger: logging.Logger = logging.getLogger()
logger.addHandler(RichHandler())


MODULES_TO_LOAD: list[str] = [
    'landing',
    'links',
    'websocket',
    'api.accounts',
    'api.login',
    'api.links',
    'api.rooms.links',
    'api.rooms.messages',
    'api.rooms.rooms',
    'api.users.me',
    'api.websocket',
]

Route = tuple[str, tornado.web.RequestHandler]
Routes = typing.Union[Route, list[Route]]


@runtime_checkable
class ModuleProtocol(Protocol):
    @staticmethod
    def setup(app) -> Routes:
        ...


class NotFound(tornado.web.RequestHandler):
    def get(self, *_):
        self.set_status(404)
        self.finish('{"message": "404: Not found", "code": 0}')

    post = get
    delete = get
    patch = get
    put = get
    options = get
    head = get


class Application(tornado.web.Application):
    def __init__(self, config, database: Database):
        self.database = database
        self.config = config

        self.tokens = Tokens(**config['tokens'])

        self.version: int = config['api']['version']
        self.client_url: str = config['client']['url']

        settings: dict[str, Any] = dict(
            app_title=config['server']['title'],
            debug=config['server']['debug'],
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            default_handler_class=NotFound,
            autoreload=config['server']['autoreload']
        )

        routes: list[Any] = []

        for module_name in MODULES_TO_LOAD:
            module = importlib.import_module(f'app.modules.{module_name}')
            if not isinstance(module, ModuleProtocol):
                raise TypeError('Modules must have a `setup` function.')

            routes_to_add = module.setup(self)

            if isinstance(routes_to_add, list):
                routes.extend(routes_to_add)
            else:
                routes.append(routes_to_add)

        # user_id: connection
        self.websocket_connections: defaultdict[str, list[WebSocketHandler]] = defaultdict(list)
        # room_id: info
        self.room_cache: defaultdict[str, list[str]] = defaultdict(list)
        # user_id: info
        self.user_cache: dict[str, dict[str, Any]] = {}
        self.room_member_cache: dict[str, dict[str, Any]] = {}

        super().__init__(routes, default_host=config['server']['host'], **settings)

    @classmethod
    def run(cls, config: typing.MutableMapping[str, Any]):
        """Starts the server."""
        logger.setLevel(logging.INFO)

        BaseAsyncIOLoop.current().make_current()
        loop = asyncio.get_event_loop()

        logging.info('Connecting to database...')
        database = loop.run_until_complete(Database.connect(config['database']))
        self = cls(config, database)

        loop.run_until_complete(self.prepare())

        self.listen(config['server']['port'], config['server']['host'])
        logging.info(f'Listening at http://{config["server"]["host"] or "localhost"}:{config["server"]["port"]}')
        logging.info('Ready to go.')
        BaseAsyncIOLoop.current().start()

    def get_link_url(self, id: str):
        """Gets the full URL for a short link."""
        default = f'http://{self.config["server"]["host"] or "localhost"}:{self.config["server"]["port"]}'
        base_url = self.config['links']['base_url'] or default
        return base_url + id

    def dispatch(self, event: str, data: dict[str, Any], *, room_id: str):
        """Dispatches an event to all connected users in a room."""
        for user_id in self.room_cache[room_id]:
            self.send_event(user_id, event, data)

    def send_event(self, user_id: str, event: str, data: dict[str, Any]):
        """Sends an event to a user if they are connected."""
        try:
            connections = self.websocket_connections[user_id]
        except KeyError:
            return  # user is not connected

        logging.info(f'Sending event {event} to user id {user_id}.')

        for websocket in connections:
            websocket.event_queue.put_nowait((event, data))

    async def fill_cache(self):
        """Fills the user, room, and room member cache."""

        query = """SELECT id, username, name, room_id, room_members.permission_level
                   FROM room_members
                   INNER JOIN users ON room_members.user_id = users.id;
                """

        async with self.database.acquire() as conn:
            records = await conn.fetch(query)
            users = await conn.fetch('SELECT id, username, name FROM users;')

        for record in records:
            user = {
                'id': record['id'],
                'username': record['username'],
                'name': record['name']
            }

            member = {
                'id': record['id'],
                'user': user,
                'room_id': record['room_id'],
                'permission_level': record['permission_level']
            }

            self.user_cache[record['id']] = user
            self.room_member_cache[record['id']] = member
            self.room_cache[record['room_id']].append(record['id'])

        for record in users:
            if self.user_cache.get(record['id']):
                return

            user = {
                'id': record['id'],
                'username': record['username'],
                'name': record['name']
            }

            self.user_cache[record['id']] = user

    async def prepare(self):
        """Prepares the server to start.

        Runs any tasks that need to be run before the server is started.
        """
        await self.fill_cache()
