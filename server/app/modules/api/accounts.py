from __future__ import annotations

from typing import TYPE_CHECKING

from app.utils.database import DatabaseError
from app.utils.handler import RequestHandler
from app.utils.spec import spec

if TYPE_CHECKING:
    from app.app import Application


class Accounts(RequestHandler, require_token=False):
    @spec(
        {
            'username': {'type': 'string', 'maxlength': 60},
            'name': {'type': 'string', 'maxlength': 60, 'required': True},
            'password': {'type': 'string', 'required': True},
            'email': {'type': 'string', 'required': True},
        }
    )
    async def post(self):
        body = self.body

        id = self.tokens.create_id()
        try:
            record = await self.database.create_account(
                body.get('username'), body['name'], body['password'], body['email'], id
            )
        except DatabaseError:
            self.error((400, 'That username is already taken.'))
            return

        user = {
            'id': record['id'],
            'username': body.get('username'),
            'name': body['name'],
        }

        self.application.user_cache[record['id']] = user

        token = self.tokens.create_token(record['id'])
        self.finish({'token': token})

    @spec(
        {
            'email': {'type': 'string'},
        },
        require_all=True,
    )
    async def get(self):
        query = 'SELECT 1 FROM accounts WHERE email=$1;'

        async with self.database.acquire() as conn:
            exists = await conn.fetchval(query, self.get_argument('email'))

        if not exists:
            return self.error((404, 'An account with that email does not exist.'), 404)

        self.finish()


def setup(app: Application):
    return (f'/api/v{app.version}/accounts', Accounts)
