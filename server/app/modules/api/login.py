from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.database import DatabaseError
from app.utils.handler import RequestHandler
from app.utils.spec import spec

if TYPE_CHECKING:
    from app import Application


class Login(RequestHandler, require_token=False):
    @spec({
        'email': {'type': 'string'},
        'password': {'type': 'string'},
    })
    async def post(self):
        body = self.body
        try:
            result = await self.database.get_account(body['email'], body['password'])
        except DatabaseError:
            self.error((401, 'The username and/or password are incorrect.'), 401)
            return

        token = self.tokens.create_token(result['id'])
        self.finish({'token': token})


def setup(app: Application):
    return [(f'/api/v{app.version}/login', Login)]
