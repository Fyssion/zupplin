from __future__ import annotations

import contextlib
import datetime
from enum import Enum
from typing import Any, Optional

import argon2
import asyncpg
import orjson

from .errors import AppError


class DatabaseError(AppError):
    ...


class PermissionLevel(Enum):
    user = 0
    admin = 1


DROP_TABLES = """
DROP TABLE users;
DROP TABLE user_settings;
DROP TABLE rooms;
DROP TABLE room_members;
DROP TABLE messages;
DROP TABLE links;
"""


class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.hasher = argon2.PasswordHasher()
        self.setup_completed: bool | None = None

    @staticmethod
    async def connection_init(connection: asyncpg.Connection) -> asyncpg.Connection:
        await connection.set_type_codec(
            'json', encoder=orjson.dumps, decoder=orjson.loads, schema='pg_catalog'
        )
        return connection

    @classmethod
    async def connect(cls, config: dict[str, Any]):
        pool = await asyncpg.create_pool(config['uri'], init=cls.connection_init)
        assert pool

        with open('schema.sql', 'r') as f:
            await pool.execute(f.read())

        self = cls(pool)

        if await pool.fetchval('SELECT 1 FROM users LIMIT 1;'):
            self.setup_completed = True
        else:
            self.setup_completed = False

        return self

    @contextlib.asynccontextmanager
    async def acquire(self, *, timeout: float | None = None):
        conn: asyncpg.Connection = await self.pool.acquire(timeout=timeout)
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    async def create_account(
        self, username: str | None, name: str, password: str, email: str, id: str
    ) -> dict[str, Any]:
        hashed_pw: str = self.hasher.hash(password)
        permission_level = (
            PermissionLevel.user if self.setup_completed else PermissionLevel.admin
        ).value

        query = """INSERT INTO users (id, username, name, hashed_password, email, permission_level)
                   VALUES ($1, $2, $3, $4, $5, $6)
                """

        async with self.acquire() as conn:
            try:
                await conn.execute(query, id, username, name, hashed_pw, email, permission_level)
            except asyncpg.UniqueViolationError:  # type: ignore
                raise DatabaseError('That username is already taken.')

        return {'id': id, 'username': username, 'name': name, 'email': email}

    async def rehash_password(self, id: str, password: str):
        hashed_password = self.hasher.hash(password)

        query = """UPDATE users
                   SET hashed_password=$1
                   WHERE id=$2;
                """
        async with self.acquire() as conn:
            await conn.execute(query, hashed_password, id)

    async def get_account(self, email: str, password: str) -> dict[str, str]:
        query = """SELECT id, username, name, hashed_password
                   FROM users
                   WHERE email=$1;
                """

        async with self.acquire() as conn:
            record = await conn.fetchrow(query, email)

        if not record:
            raise DatabaseError

        try:
            self.hasher.verify(record['hashed_password'], password)
        except argon2.exceptions.VerifyMismatchError:
            raise DatabaseError

        if self.hasher.check_needs_rehash(record['hashed_password']):
            await self.rehash_password(record['id'], password)

        return record

    async def get_room(self, room_id: str, *, with_last_message: bool = False) -> dict[str, Any]:
        if with_last_message:
            query = """SELECT id, name, description, owner_id, type, last_message.*
                       FROM rooms
                       LEFT JOIN (
                            SELECT messages.id as message_id, content as message_content,
                                room_id as message_room_id,
                                users.name as message_author_name,
                                author_id as message_author_id,
                                users.username as message_author_username
                            FROM messages
                            INNER JOIN users ON users.id = author_id
                            ORDER BY messages.created_at DESC
                            LIMIT 1
                       ) last_message ON last_message.message_room_id = rooms.id
                       WHERE id=$1;
                    """
        else:
            query = """SELECT id, name, description, owner_id, type
                       FROM rooms
                       WHERE id=$1;
                    """

        async with self.acquire() as conn:
            record = await conn.fetchrow(query, room_id)

        if not record:
            raise DatabaseError

        return record

    async def get_link(self, link_id: str) -> dict[str, Any]:
        query = """SELECT id, type, entity_id, uses, public, user_id,
                          max_uses, expires_at, created_at
                   FROM links
                   WHERE id=$1;
                """

        async with self.acquire() as conn:
            record = await conn.fetchrow(query, link_id)

            if not record:
                raise DatabaseError

            async def delete_link():
                await conn.execute('DELETE FROM links WHERE id=$1', link_id)

            if record['expires_at'] and record['expires_at'] < datetime.datetime.utcnow():
                await delete_link()
                raise DatabaseError

            if record['max_uses'] and record['uses'] >= record['max_uses']:
                await delete_link()
                raise DatabaseError

        return record
