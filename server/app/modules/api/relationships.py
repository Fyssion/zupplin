from __future__ import annotations

from typing import TYPE_CHECKING, Union

from app.utils.handler import HTTPError, RequestHandler
from app.utils.spec import spec

if TYPE_CHECKING:
    from app.app import Application


class RelationshipType:
    friend = 0
    block = 1


async def delete_relationship(handler: Union[Relationships, RelationshipsID], recipient_id: str):
    query = """DELETE FROM relationships
                   WHERE user_id=$1 AND recipient_id=$2
                   RETURNING type;
                """

    async with handler.database.acquire() as conn:
        relationship_type = await conn.fetchval(query, handler.user_id, recipient_id)

        # we only need to handle the relationship if it was a friendship.
        # TODO: add relationship cache and remove this note

        if relationship_type in (None, RelationshipType.friend):
            # relationship was either a friend removal where both relationships exist,
            # friend request rejection where only the recipient-user relationship exists,
            # or friend request cancellation where only the user-recipient relationship exists.

            # remove the other relationship (may not exist)
            await conn.execute(query, recipient_id, handler.user_id)

            data = {'user_id': handler.user_id}
            handler.application.send_event(recipient_id, 'RELATIONSHIP_REMOVE', data)

            data = {'user_id': recipient_id}
            handler.application.send_event(handler.user_id, 'RELATIONSHIP_REMOVE', data)

    # deal with the cache
    cache = handler.application.relationship_cache

    if relationship_type is not None:
        cache[handler.user_id].remove((relationship_type, handler.user_id))

    if relationship_type in (None, RelationshipType.friend) and handler.application.get_relationship(recipient_id, handler.user_id):
        cache[recipient_id].remove((RelationshipType.friend, handler.user_id))


class Relationships(RequestHandler):
    async def insert_relationship(self, type: int, recipient_id: str):
        sql = "INSERT INTO relationships (type, user_id, recipient_id) VALUES ($1, $2, $3);"

        async with self.database.acquire() as conn:
                await conn.execute(sql, type, self.user_id, recipient_id)

    async def friend(self):
        recipient_id = self.body['recipient_id']

        outgoing = self.application.get_relationship(self.user_id, recipient_id)
        if outgoing:
            self.error(HTTPError.BAD_REQUEST, 400, message='You have an existing relationship with this user.')
            return

        relationship = self.application.get_relationship(recipient_id, self.user_id)
        if not relationship:
            # no friend request from recipient and user is not blocked,
            # so this API request will send a new friend request

            # TODO: confirm they share a room

            await self.insert_relationship(RelationshipType.friend, recipient_id)
            self.application.relationship_cache[self.user_id].append((RelationshipType.friend, recipient_id))

            user = self.application.user_cache[self.user_id]
            data = {'user': user}
            self.application.send_event(recipient_id, 'RELATIONSHIP_CREATE', data)

            self.finish({'user_id': recipient_id})
        else:
            # at this point, the user is either blocked or is accepting a friend request from the recipient
            if relationship['type'] is RelationshipType.block:
                self.error((400, 'Could not send friend request'))
            else:
                # accept the friend request
                await self.insert_relationship(RelationshipType.friend, recipient_id)
                self.application.relationship_cache[self.user_id].append((RelationshipType.friend, recipient_id))

                user = self.application.user_cache[self.user_id]
                data = {'user': user}
                self.application.send_event(recipient_id, 'RELATIONSHIP_CREATE', data)

                recipient = self.application.user_cache[recipient_id]
                data = {'user': recipient}
                self.application.send_event(self.user_id, 'RELATIONSHIP_CREATE', data)

                self.finish(data)

    async def block(self):
        recipient_id = self.body['recipient_id']

        outgoing = self.application.get_relationship(self.user_id, recipient_id)
        if outgoing:
            if outgoing['type'] is RelationshipType.block:
                self.error(HTTPError.BAD_REQUEST, 400, message='You have already blocked this user.')
                return
            else:
                await delete_relationship(self, recipient_id)  # remove friendship

        await self.insert_relationship(RelationshipType.block, recipient_id)
        self.application.relationship_cache[self.user_id].append((RelationshipType.block, recipient_id))

        self.finish()

    @spec(
        {
            'type': {'type': 'integer', 'allowed': [0, 1]},
            'recipient_id': {'type': 'string'},
        },
        require_all=True,
    )
    async def post(self):
        if self.body['type'] is RelationshipType.friend:
            await self.friend()
        else:
            await self.block()


class RelationshipsID(RequestHandler):
    async def get(self, recipient_id: str):
        pass

    async def delete(self, recipient_id: str):
        await delete_relationship(self, recipient_id)
        self.finish()


def setup(app: Application):
    return [
        (f'/api/v{app.version}/relationships', Relationships),
        (f'/api/v{app.version}/relationships/(.+)', RelationshipsID),
    ]
