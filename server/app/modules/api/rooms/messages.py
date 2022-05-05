from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.utils.handler import RequestHandler
from app.utils.spec import spec

if TYPE_CHECKING:
    from app import Application


class Messages(RequestHandler):
    @spec({
        'content': {'type': 'string', 'maxlength': 4096},
    })
    async def post(self, room_id: str):
        if not self.application.room_cache.get(room_id):
            return self.error((404, 'Room not found.'), 404)

        # raise 404 if user isn't in room
        if self.user_id not in self.application.room_cache[room_id]:
            return self.error((404, 'Room not found.'), 404)

        id = self.tokens.create_id()
        content: Optional[str] = self.body.get('content')

        author = self.application.user_cache[self.user_id]
        message_type = 0  # regular user message

        query = """INSERT INTO messages (id, content, room_id, author_id, type)
                   VALUES ($1, $2, $3, $4, $5);
                """
        async with self.database.acquire() as conn:
            await conn.execute(query, id, content, room_id, self.user_id, message_type)

        message = {
            'id': id,
            'content': content,
            'room_id': room_id,
            'author': author,
            'type': message_type
        }
        self.application.dispatch('MESSAGE', message, room_id=room_id)

        self.finish({'id': id})


class MessagesID(RequestHandler):
    async def get(self, room_id: str, message_id: str):
        if not self.application.room_cache.get(room_id):
            return self.error((404, 'Room not found.'), 404)

        # raise 404 if user isn't in room
        if self.user_id not in self.application.room_cache[room_id]:
            return self.error((404, 'Room not found.'), 404)

        query = """SELECT content, author_id, type
                   FROM messages
                   WHERE room_id=$1 AND id=$2;
                """

        async with self.database.acquire() as conn:
            record = await conn.fetchrow(query, room_id, message_id)

        if not record:
            return self.error((404, 'Message not found.'), 404)

        author = self.application.user_cache[record['author_id']]

        message = {
            'id': message_id,
            'content': record['content'],
            'room_id': room_id,
            'author': author,
            'type': record['type']
        }

        self.finish(message)


def setup(app: Application):
    return [
        (f'/api/v{app.version}/rooms/(.+)/messages', Messages),
        (f'/api/v{app.version}/rooms/(.+)/messages/(.+)', MessagesID)
        ]
