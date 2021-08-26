import re
from typing import Any, Union

import orjson
import tornado.web

from .database import Database

err = tuple[int, str]


class HTTPError:
    NOT_FOUND: err = (404, 'Not Found')
    INVALID_METHOD: err = (405, 'Method Not Allowed')
    UNATHORIZED: err = (401, 'Unauthorized')


class RequestHandler(tornado.web.RequestHandler):
    user_id: str
    body: dict[str, Any]

    def __init_subclass__(cls, require_token: bool = True) -> None:
        super().__init_subclass__()
        cls.require_token = require_token  # type: ignore

    def initialize(self):
        self.user_id = None  # type: ignore

    @property
    def database(self) -> Database:
        return self.application.database

    @property
    def tokens(self):
        return self.application.tokens

    def write(self, chunk: Union[str, bytes, dict]) -> None:
        if isinstance(chunk, dict):
            self.set_header('Content-Type', 'application/json')
            chunk = orjson.dumps(chunk)

        return super().write(chunk)

    def write_error(self, status_code: int, **kwargs):
        try:
            reason: dict[str, Any] = {
                'code': kwargs.pop('code'),
                'message': kwargs.pop('message')
            }
            if kwargs:
                reason['errors'] = kwargs

        except KeyError:
            reason = {'code': 0, 'message': 'Internal Server Error.'}

        self.set_status(status_code)
        self.finish(reason)

    def error(self, code: tuple[int, str], status_code: int = 400, **kwargs):
        self.send_error(status_code=status_code, code=code[0], message=code[1], **kwargs)

    AUTH_HEADER_REGEX = re.compile(r'(?:Bearer )(.+)')

    async def prepare(self):
        if self.require_token and self.request.method != "OPTIONS":
            auth_header = self.request.headers.get('Authorization')

            if not auth_header:
                self.send_error(401, code=0, message='Authorization header missing.')
                return

            match = self.AUTH_HEADER_REGEX.match(auth_header)

            if not match:
                self.send_error(401, code=0, message='Invalid Authorization header.')
                return

            try:
                self.user_id = self.tokens.validate_token(match.groups()[0])
            except Exception:
                self.write_error(401, code=0, message='Invalid token.')
                return

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', ', '.join(map(str.upper, self.SUPPORTED_METHODS)))

    def options(self, *_):
        self.set_status(204)
        self.finish()

    def _unimplemented_method(self, *args, **kwargs):
        self.error(HTTPError.INVALID_METHOD, 405)

    head = _unimplemented_method
    get = _unimplemented_method
    post = _unimplemented_method
    delete = _unimplemented_method
    patch = _unimplemented_method
    put = _unimplemented_method
