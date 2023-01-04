from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

from app.utils.database import DatabaseError
from app.utils.decorators import with_body
from app.utils.errors import InvalidBody, JsonError
from app.utils.handler import RequestHandler

if TYPE_CHECKING:
    from app.app import Application


class PostBody(TypedDict):
    username: NotRequired[str]
    name: str
    password: str
    email: str


class GetBody(TypedDict):
    email: str


class Accounts(RequestHandler, require_token=False):
    @with_body(PostBody)
    async def post(self):
        body = self.body

        if max(map(len, (body.get('username', ''), body['name']))) > 60:
            raise InvalidBody

        if '@' not in body['email']:
            raise JsonError(400, 'Invalid email')

        id = self.tokens.create_id()
        try:
            record = await self.database.create_account(
                body.get('username'), body['name'], body['password'], body['email'], id
            )
        except DatabaseError:
            raise JsonError(400, 'Username is taken')

        user = {
            'id': record['id'],
            'username': body.get('username'),
            'name': body['name'],
        }

        self.application.user_cache[record['id']] = user

        token = self.tokens.create_token(record['id'])
        self.finish({'token': token})

    @with_body(GetBody)
    async def get(self):
        query = 'SELECT 1 FROM accounts WHERE email=$1;'

        async with self.database.acquire() as conn:
            exists = await conn.fetchval(query, self.get_argument('email'))

        if not exists:
            raise JsonError(404, 'An account with that email does not exist')

        self.finish()


def setup(app: Application):
    return (f'/accounts', Accounts)
