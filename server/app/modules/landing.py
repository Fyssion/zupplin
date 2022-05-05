from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import Application


from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    application: Application


class LandingHandler(BaseHandler):
    async def get(self):
        self.render("landing.html")


class AboutHandler(BaseHandler):
    async def get(self):
        self.render("about.html")


def setup(app: Application):
    return [(r"/", LandingHandler), (r"/about", AboutHandler)]
