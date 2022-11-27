from __future__ import annotations

import asyncio
from typing import Any, Optional
from urllib import request

import orjson
import pytest
import pytest_asyncio
import toml
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from app.app import Application
from app.utils.database import DROP_TABLES, Database


@pytest.fixture(scope='package')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='package')
def config():
    with open('config.toml', 'r') as f:
        config = toml.load(f)

    return config


@pytest_asyncio.fixture(scope='package')
async def database(config):
    return await Database.connect(config['database'])


@pytest_asyncio.fixture(scope='package')
async def app(config, database):
    await database.pool.execute(DROP_TABLES)
    await database.create_tables()

    app = Application(config, database)
    await app.prepare()
    app.listen(app.config['server']['port'], app.config['server']['host'])

    return app


@pytest_asyncio.fixture(scope='module')
async def create_user(app):
    users = []

    async def _create_user(*args, **kwargs):
        id = app.tokens.create_id()
        users.append(id)

        kwargs['id'] = id
        record = await app.database.create_account(*args, **kwargs)

        user = {
            'id': id,
            'username': kwargs.get('username'),
            'name': kwargs['name'],
        }

        app.user_cache[record['id']] = user

        return user

    yield _create_user

    SQL = 'DELETE FROM users WHERE id=$1;'

    async with app.database.acquire() as conn:
        for user in users:
            await conn.execute(SQL, user)
            app.user_cache.pop(user)


@pytest.fixture(scope='module')
def http_client():
    return AsyncHTTPClient()


@pytest.fixture(scope='module')
def make_request(app, http_client):
    async def _make_request(url: str, method: str, *, body: Optional[dict[str, Any]] = None, token: Optional[str] = None, **kwargs):
        url = f"http://{app.config['server']['host']}:{app.config['server']['port']}/api/v{app.version}/{url}"
        raw_body = orjson.dumps(body) if body else None

        request = HTTPRequest(url, method, body=raw_body, **kwargs)
        request.headers['Content-Type'] = 'application/json'
        request.headers['Accept'] = 'application/json'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Accept-Encoding'] = 'gzip'

        if token:
            request.headers['Authorization'] = f'Bearer {token}'

        return await http_client.fetch(request, raise_error=False)

    return _make_request
