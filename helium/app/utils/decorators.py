from __future__ import annotations

import functools
from typing import Callable, Type, TypeVar, TypedDict

import orjson

from .errors import InvalidBody, JsonError
from .handler import RequestHandler
from .validate import validate

T = TypeVar('T')


def with_body(td: Type[TypedDict]) -> Callable[[Callable[..., T | None]], Callable[..., T | None]]:
    """Decorator that validates a request body against a TypedDict"""

    def predicate(func: Callable[..., T | None]) -> Callable[..., T | None]:
        @functools.wraps(func)
        def wrapper(self: RequestHandler, *args, **kwargs) -> T | None:
            raw_body: bytes = self.request.body

            if not raw_body:
                raise JsonError(400, 'Missing body')

            body = orjson.loads(raw_body)

            if not validate(td, body):
                raise InvalidBody

            self.body = body
            return func(self, *args, **kwargs)

        return wrapper

    return predicate
