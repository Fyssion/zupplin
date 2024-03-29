from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, Optional, TypedDict

from app.utils.decorators import with_body
from app.utils.errors import InvalidBody, NotFound
from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app.app import Application


class PostBody(TypedDict):
    name: str
    description: NotRequired[str]


class Rooms(RequestHandler):
    @with_body(PostBody)
    async def post(self):
        if len(self.body['name']) > 128 or len(self.body.get('description', '')) > 1024:
            raise InvalidBody

        id = self.tokens.create_id()
        name: str = self.body['name']
        description: Optional[str] = self.body.get('description')

        room_type = 0  # regular group room

        insert_room = """INSERT INTO rooms (id, name, description, owner_id, type)
                         VALUES ($1, $2, $3, $4, $5);
                      """

        insert_member = """INSERT INTO room_members (user_id, room_id, permission_level)
                           VALUES ($1, $2, $3);
                        """
        async with self.database.acquire() as conn:
            await conn.execute(insert_room, id, name, description, self.user_id, room_type)
            await conn.execute(insert_member, self.user_id, id, 0)

        room = {
            'id': id,
            'name': name,
            'description': description,
            'owner_id': self.user_id,
            'type': room_type,
        }
        self.application.send_event(self.user_id, 'ROOM_JOIN', room)

        self.application.room_cache[id].append(self.user_id)

        self.finish({'id': id})


class RoomsID(RequestHandler):
    async def get(self, room_id: str):
        if not self.application.room_cache.get(room_id):
            raise NotFound

        # raise 404 if user isn't in room
        if self.user_id not in self.application.room_cache[room_id]:
            raise NotFound

        record = await self.database.get_room(room_id)

        room = {
            'id': room_id,
            'name': record['name'],
            'description': record['description'],
            'owner_id': record['owner_id'],
        }

        self.finish(room)


def setup(app: Application):
    return [(f'/rooms', Rooms), (f'/rooms/(.+)', RoomsID)]
