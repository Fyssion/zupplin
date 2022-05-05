from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.utils.handler import RequestHandler  # , HTTPError
from app.utils.spec import spec

if TYPE_CHECKING:
    from app.app import Application


class Links(RequestHandler):
    @spec(
        {
            'max_age': {
                'type': 'number',
                'default': 86400,
                'max': 604800,
                'min': 0,
                'required': False,
            },
            'max_uses': {'type': 'number', 'default': 0, 'min': 0, 'max': 100, 'required': False},
        }
    )
    async def post(self, room_id: str):
        async with self.database.acquire() as conn:
            id = None
            already_exists: int | None = None

            # I'm unsure how I should handle potential duplicate links.
            # This is an easy solution I thought of, but it's probably not the best.
            for tries in range(20):
                id = self.tokens.create_link_id()
                already_exists = await conn.fetchval('SELECT 1 FROM links WHERE id=$1', id)

                if not already_exists:
                    break

            if already_exists or not id:
                return self.send_error(500)  # hopefully this will never happen

            if self.body['max_age']:
                expires_at = datetime.datetime.utcnow() + datetime.timedelta(
                    seconds=self.body['max_age']
                )
            else:
                expires_at = None

            link_type = 0  # room link

            link = {
                'id': id,
                'type': link_type,
                'entity_id': room_id,
                'user_id': self.user_id,
                'expires_at': expires_at,
            }

            query = """INSERT INTO links (id, type, entity_id, user_id, expires_at)
                    VALUES ($1, $2, $3, $4, $5);
                    """

            await conn.execute(query, *link.values())

        link['public'] = False
        link['uses'] = 0
        link['url'] = self.application.get_link_url(id)

        # self.application.send_event(self.user_id, 'ROOM_JOIN', room)

        self.finish(link)


def setup(app: Application):
    return (f'/api/v{app.version}/rooms/(.+)/links', Links)
