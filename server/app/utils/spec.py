from __future__ import annotations

import functools

import orjson
from cerberus import Validator
from .handler import RequestHandler


# TODO: type-hint this
def spec(schema, *, allow_unknown: bool = False, require_all: bool = False):
    validator = Validator(schema, allow_unknown=allow_unknown, require_all=require_all)

    def predicate(func):

        @functools.wraps(func)
        def wrapper(self: RequestHandler, *args, **kwargs):
            raw_body: bytes = self.request.body

            if not raw_body:
                return self.error((0, 'Missing required key'))

            body = orjson.loads(raw_body)

            status: bool = validator.validate(body)  # type: ignore

            if not status:
                return self.error((0, 'Invalid'),  **validator.errors)  # type: ignore

            body = validator.normalized(body)  # type: ignore

            if not status:
                return self.error((0, 'Invalid'), **validator.errors)  # type: ignore

            self.body = body
            return func(self, *args, **kwargs)

        return wrapper
    return predicate
