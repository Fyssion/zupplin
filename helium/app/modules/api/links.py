from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.database import DatabaseError
from app.utils.errors import NotFound
from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app.app import Application


class LinkType:
    ROOM: int = 0
    USER: int = 1


class Links(RequestHandler):
    async def join_room(self, link):
        update_link = """UPDATE links
                        SET uses = uses + 1
                        WHERE id=$1;
                      """

        insert_member = """INSERT INTO room_members (user_id, room_id, permission_level)
                           VALUES ($1, $2, $3);
                        """

        async with self.database.acquire() as conn:
            await conn.execute(update_link, link['id'])
            await conn.execute(insert_member, self.user_id, link['entity_id'], 0)

        record = await self.database.get_room(link['entity_id'], with_last_message=True)

        if record['message_id']:
            message_author = {
                'id': record['message_author_id'],
                'name': record['message_author_name'],
                'username': record['message_author_username'],
            }

            last_message = {
                'id': record['message_id'],
                'content': record['message_content'],
                'room_id': record['message_room_id'],
                'author': message_author,
            }

        else:
            last_message = None

        room = {
            'id': record['id'],
            'name': record['name'],
            'description': record['description'],
            'owner_id': record['owner_id'],
            'type': record['type'],
            'me': {'permission_level': 0},
            'last_message': last_message,
        }
        self.application.send_event(self.user_id, 'ROOM_JOIN', room)

        self.application.room_cache[link['entity_id']].append(self.user_id)

        self.finish(room)

    async def post(self, link_id: str):
        try:
            link = await self.database.get_link(link_id)
        except DatabaseError:
            raise NotFound

        if link['type'] == 0:
            await self.join_room(link)

        else:
            self.send_error(500)

    async def get(self, link_id: str):
        try:
            link_record = await self.database.get_link(link_id)
        except DatabaseError:
            raise NotFound

        entity = None

        if link_record['type'] == 0:
            room_record = await self.database.get_room(link_record['entity_id'])
            entity = {
                'id': room_record['id'],
                'name': room_record['name'],
                'description': room_record['description'],
            }

        else:
            return self.send_error(500)

        link = {'type': link_record['type'], 'entity': entity}

        self.finish(link)


def setup(app: Application):
    return (f'/links/(.+)', Links)
