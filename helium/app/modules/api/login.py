from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from app.utils.database import DatabaseError
from app.utils.decorators import with_body
from app.utils.errors import Unauthorized
from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app.app import Application


class PostBody(TypedDict):
    email: str
    password: str


class Login(RequestHandler, require_token=False):
    @with_body(PostBody)
    async def post(self):
        body = self.body
        try:
            result = await self.database.get_account(body['email'], body['password'])
        except DatabaseError:
            raise Unauthorized(message='Invalid credentials')

        token = self.tokens.create_token(result['id'])
        self.finish({'token': token})


def setup(app: Application):
    return [(f'/login', Login)]
