from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

import orjson
import tornado.log
import tornado.web

from app.utils.errors import InvalidMethod, JsonError

from .database import Database

if TYPE_CHECKING:
    from app.app import Application

    err = tuple[int, str]

GET_T = TypeVar('GET_T')
POST_T = TypeVar('POST_T')


class RequestHandler(tornado.web.RequestHandler, Generic[GET_T, POST_T]):
    VALIDATED_METHODS = ('GET', 'POST')

    application: Application
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
            reason: dict[str, Any] = {'code': kwargs.pop('code'), 'message': kwargs.pop('message')}
        except KeyError:
            reason = {'code': 500, 'message': 'Internal Server Error.'}

        self.set_status(status_code)
        self.finish(reason)

    AUTH_HEADER_REGEX = re.compile(r'(?:Bearer )(.+)')

    async def prepare(self):
        if self.require_token and self.request.method != 'OPTIONS':
            # authorization
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
        self.set_header(
            'Access-Control-Allow-Methods', ', '.join(map(str.upper, self.SUPPORTED_METHODS))
        )

    def options(self, *_):
        self.set_status(204)
        self.finish()

    def _unimplemented_method(self, *args, **kwargs):
        raise InvalidMethod

    head = _unimplemented_method
    get = _unimplemented_method
    post = _unimplemented_method
    delete = _unimplemented_method
    patch = _unimplemented_method
    put = _unimplemented_method

    def _handle_request_exception(self, e: BaseException) -> None:
        # adapted from
        # https://github.com/tornadoweb/tornado/blob/711868dddb279b50ff59a324768f968f60046f7d/tornado/web.py#L1751-L1771
        # for custom error handling

        if isinstance(e, tornado.web.Finish):
            # Not an error; just finish the request without logging.
            if not self._finished:
                self.finish(*e.args)
            return
        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            # An error here should still get a best-effort send_error()
            # to avoid leaking the connection.
            tornado.log.app_log.error("Error in exception logger", exc_info=True)
        if self._finished:
            # Extra errors after the request has been finished should
            # be logged, but there is no reason to continue to try and
            # send a response.
            return
        if isinstance(e, tornado.web.HTTPError):
            self.send_error(e.status_code, exc_info=sys.exc_info())
        elif isinstance(e, JsonError):
            # more refined error control
            self.send_error(status_code=e.status_code, code=e.status_code, message=e.message, exc_info=sys.exc_info())
        else:
            self.send_error(500, exc_info=sys.exc_info())
