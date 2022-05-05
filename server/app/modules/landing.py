from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.app import Application
    from app.utils.database import Database


from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    application: Application

    @property
    def database(self) -> Database:
        return self.application.database


class LandingHandler(BaseHandler):
    async def get(self):
        self.render("landing.html")


class AboutHandler(BaseHandler):
    async def get(self):
        self.render("about.html")


def setup(app: Application):
    return [(r"/", LandingHandler), (r"/about", AboutHandler)]
