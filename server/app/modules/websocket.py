import asyncio
import datetime
import logging
from enum import Enum
from typing import Any, Optional, Union

import orjson
import tornado.ioloop
import tornado.websocket
from cerberus import Validator

# websocket opcodes:
# dispatch: dispatched events like new messages
# heartbeat: periodically sent message to confirm connection is alive
# heartbeat_ack: confirmation that heartbeat was recieved
# identify: information sent about who is connecting
# hello: initial info sent to the client that includes heartbeat interval


class WebsocketOpcode(Enum):
    DISPATCH = 0
    HEARTBEAT = 1
    HEARTBEAT_ACK = 2
    IDENTIFY = 3
    HELLO = 4


class WebsocketError:
    INVALID_OPCODE: int = 4000
    INVALID_DATA: int = 4001
    INVALID_TOKEN: int = 4002
    ALREADY_IDENTIFIED: int = 4003


identify_schema = {
    'token': {'type': 'string'},
}

identify_schema = Validator(identify_schema)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    HEARTBEAT_INTERVAL = 60000  # 60 seconds. hardcoded for now.

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.heartbeat_event = asyncio.Event()
        self.last_heartbeat_ack = datetime.datetime.utcnow()
        self.sleep_interval = (self.HEARTBEAT_INTERVAL * 1.25) / 1000
        self.event_queue = asyncio.Queue()
        self.identified: bool = False
        self.user_id = None  # type: ignore
        self.increment: int = 0

        self.heartbeat_task: asyncio.Task
        self.dispatch_task: asyncio.Task

    def write_message(self, message: Union[bytes, str, dict[str, Any]], binary: bool = False):
        if isinstance(message, dict):
            message = orjson.dumps(message)
        super().write_message(message, binary)

    def send_message(self, opcode: WebsocketOpcode, data: Optional[dict[str, Any]] = None, *, event_name: str = None, increment: int = None):
        message = {
            'opcode': opcode.value,
            'data': data,
            'event_name': event_name,
            'increment': increment,
        }
        self.write_message(message)

    def open(self):
        data = {'heartbeat_interval': self.HEARTBEAT_INTERVAL}
        self.send_message(WebsocketOpcode.HELLO, data)

    def on_identify(self, data: dict[str, str]):
        if self.identified:
            self.close(WebsocketError.ALREADY_IDENTIFIED, 'Already identified.')
            return

        token: str = data['token']

        try:
            self.user_id = self.application.tokens.validate_token(token)
        except Exception:
            self.close(WebsocketError.INVALID_TOKEN, 'Token is invalid.')
            return

        self.application.websocket_connections[self.user_id].append(self)
        self.identified = True

        self.dispatch_task = asyncio.create_task(self.dispatch_loop())
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

        logging.info(f'User {self.user_id} connected and identified.')

    def on_heartbeat(self, data=None):
        self.heartbeat_event.set()
        self.last_heartbeat_ack = datetime.datetime.utcnow()
        self.send_message(opcode=WebsocketOpcode.HEARTBEAT_ACK)

    OPCODE_MAPPING = {
        WebsocketOpcode.IDENTIFY: on_identify,
        WebsocketOpcode.HEARTBEAT: on_heartbeat,
    }

    def on_message(self, message: str):
        try:
            data = orjson.loads(message)
        except orjson.JSONDecodeError:
            self.close(WebsocketError.INVALID_DATA, 'Invalid message recieved.')
            return

        try:
            opcode = WebsocketOpcode(data['opcode'])
        except ValueError:
            self.close(WebsocketError.INVALID_OPCODE, f'Invalid opcode recieved ({data["opcode"]}).')
            return

        method = self.OPCODE_MAPPING[opcode]
        method(self, data.get('data'))

    def on_close(self):
        if not self.identified:
            return

        logging.info(f'Closing websocket connection with user {self.user_id}')

        self.heartbeat_task.cancel()
        self.dispatch_task.cancel()

        user_connections: list = self.application.websocket_connections[self.user_id]
        user_connections.pop(user_connections.index(self))
        if not user_connections:
            self.application.websocket_connections.pop(self.user_id)

    async def heartbeat_loop(self):
        delta = datetime.timedelta(seconds=self.sleep_interval)

        while True:
            await self.heartbeat_event.wait()
            await asyncio.sleep(self.sleep_interval)
            self.heartbeat_event.clear()

            behind = self.last_heartbeat_ack < datetime.datetime.utcnow() - delta

            if behind:
                self.close()
                return

    async def dispatch_loop(self):
        while True:
            event, data = await self.event_queue.get()
            self.send_message(WebsocketOpcode.DISPATCH, data, event_name=event, increment=self.increment)
            self.increment += 1

    def check_origin(self, origin):
        return True


def setup(app: Application):
    return (f'/api/v{app.version}/websocket/connect', WebSocketHandler)
