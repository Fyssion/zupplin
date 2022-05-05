from __future__ import annotations

import urllib.parse
from typing import TYPE_CHECKING

from app.utils.database import DatabaseError

from .landing import BaseHandler

if TYPE_CHECKING:
    from app import Application


class LinkHandler(BaseHandler):
    async def get(self, link_id: str):
        try:
            link_record = await self.application.database.get_link(link_id)
        except DatabaseError:
            return self.send_error(404)

        entity = None

        if link_record['type'] == 0:
            room_record = await self.application.database.get_room(link_record['entity_id'])
            entity = {
                'id': room_record['id'],
                'name': room_record['name'],
                'description': room_record['description'],
            }

            link = {
                'id': link_id,
                'type': link_record['type'],
                'client_url': urllib.parse.urljoin(
                    self.application.client_url, f'?joinRoomCode={link_id}'
                ),
            }

        else:
            return self.send_error(500)

        self.render("link.html", link=link, entity=entity)


def setup(app: Application):
    return [
        (r"/l/(.+)", LinkHandler),
        (r"/link/(.+)", LinkHandler),
    ]
