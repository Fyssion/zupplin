from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app import Application


class Websocket(RequestHandler):
    ...


def setup(app: Application):
    return (f'/api/v{app.version}/websocket', Websocket)
