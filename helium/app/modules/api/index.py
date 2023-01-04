from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app.app import Application


class Index(RequestHandler, require_token=False):
    async def get(self):
        self.finish({'version': self.application.version})


def setup(app: Application):
    return (f'/', Index)
