from app.utils.handler import RequestHandler


class Websocket(RequestHandler):
    ...


def setup(app):
    return (f'/api/v{app.version}/websocket', Websocket)
