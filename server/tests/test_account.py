import pytest
import pytest_asyncio
from typing import Optional


@pytest_asyncio.fixture(scope='module')
async def create_account(app, make_request):
    emails: list[str] = []

    async def _create_account(name: str, password: str, email: str, username: Optional[str] = None):
        emails.append(email)

        body = {'name': name, 'password': password, 'email': email}
        if username:
            body['username'] = username
        return await make_request(
            'accounts',
            'POST',
            body=body,
        )

    yield _create_account

    SQL = 'DELETE FROM users WHERE email=$1 RETURNING id;'

    async with app.database.acquire() as conn:
        for email in emails:
            id = await conn.fetchval(SQL, email)

            if id:
                app.user_cache.pop(id)


class TestAccountCreationSuccess:
    @pytest_asyncio.fixture(scope='class', autouse=True)
    async def response(self, create_account):
        return await create_account(
            name='.',
            password='.',
            email='test@email.com',
        )

    def test_response(self, response):
        assert response.code == 200

    def test_cache(self, app):
        assert len(app.user_cache) == 1

    @pytest.mark.asyncio
    async def test_database(self, database):
        query = 'SELECT id FROM users;'
        records = await database.pool.fetch(query)
        assert len(records) == 1


class TestAccountCreationFailure:
    @pytest_asyncio.fixture(scope='class', autouse=True, params=(
        (
            {'name': '.', 'password': '.', 'email': 'invalid_email'},
        ),
        (
            {'name': '.', 'password': '.', 'email': 'duplicate@email.com'},
            {'name': '.', 'password': '.', 'email': 'duplicate@email.com'},
        ),
        (
            {'name': '.', 'password': '.', 'email': '1@1.com', 'username': 'duplicate'},
            {'name': '.', 'password': '.', 'email': '2@2.com', 'username': 'duplicate'},
        )
    ), ids=('bad email', 'duplicate email', 'duplicate username'))
    async def response(self, request, create_account):
        resp = None

        for account in request.param:
            resp = await create_account(**account)

            if resp.code != 200:
                return resp

        return resp

    def test_response(self, response):
        assert response.code == 400
