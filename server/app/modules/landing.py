from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    ...


class LandingHandler(BaseHandler):
    async def get(self):
        self.render("landing.html")


class AboutHandler(BaseHandler):
    async def get(self):
        self.render("about.html")


def setup(app):
    return [
        (r"/", LandingHandler),
        (r"/about", AboutHandler)
    ]
