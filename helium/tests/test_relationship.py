import pytest
import pytest_asyncio

from app.modules.api.relationships import RelationshipType


@pytest_asyncio.fixture(scope='module')
async def create_relationship(app, make_request):
    relationships: list[tuple[str, str]] = []

    async def _create_relationship(type: int, user_id: str, recipient_id: str):
        relationships.append((user_id, recipient_id))

        token = app.tokens.create_token(user_id)

        body = {'recipient_id': recipient_id, 'type': type}
        return await make_request(
            'relationships',
            'POST',
            body=body,
            token=token,
        )

    yield _create_relationship

    for user_id, recipient_id in relationships:
        token = app.tokens.create_token(user_id)

        await make_request(
            f'relationships/{recipient_id}',
            'DELETE',
            token=token,
        )


class TestFriendRequestSuccess:
    @pytest_asyncio.fixture(scope='class', autouse=True)
    async def response(self, create_user, create_relationship):
        user1 = await create_user(None, name='.', password='.', email='test@email.com')
        user2 = await create_user(None, name='.', password='.', email='test2@email.com')

        return await create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])

    def test_response(self, response):
        assert response.code == 200

    def test_cache(self, app):
        assert len(app.relationship_cache) == 1

    @pytest.mark.asyncio
    async def test_database(self, database):
        query = 'SELECT 1 FROM relationships;'
        records = await database.pool.fetch(query)
        assert len(records) == 1


class TestFriendAcceptSuccess:
    @pytest_asyncio.fixture(scope='class', autouse=True)
    async def response(self, create_user, create_relationship):
        user1 = await create_user(None, name='.', password='.', email='1@email.com')
        user2 = await create_user(None, name='.', password='.', email='2@email.com')

        await create_relationship(RelationshipType.FRIEND, user2['id'], user1['id'])
        return await create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])

    def test_response(self, response):
        assert response.code == 200

    def test_cache(self, app):
        assert len(app.relationship_cache) == 3

    @pytest.mark.asyncio
    async def test_database(self, database):
        query = 'SELECT 1 FROM relationships;'
        records = await database.pool.fetch(query)
        assert len(records) == 3


async def prepare_already_friended(create_user, create_relationship):
    user1 = await create_user(None, name='.', password='.', email='1@a.b')
    user2 = await create_user(None, name='.', password='.', email='2@a.b')

    await create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])
    await create_relationship(RelationshipType.FRIEND, user2['id'], user1['id'])

    return create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])


async def prepare_already_requested(create_user, create_relationship):
    user1 = await create_user(None, name='.', password='.', email='3@a.b')
    user2 = await create_user(None, name='.', password='.', email='4@a.b')

    await create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])

    return create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])


async def prepare_outgoing_block(create_user, create_relationship):
    user1 = await create_user(None, name='.', password='.', email='5@a.b')
    user2 = await create_user(None, name='.', password='.', email='6@a.b')

    await create_relationship(RelationshipType.BLOCK, user1['id'], user2['id'])

    return create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])


async def prepare_incoming_block(create_user, create_relationship):
    user1 = await create_user(None, name='.', password='.', email='7@a.b')
    user2 = await create_user(None, name='.', password='.', email='8@a.b')

    await create_relationship(RelationshipType.BLOCK, user2['id'], user1['id'])

    return create_relationship(RelationshipType.FRIEND, user1['id'], user2['id'])


class TestFriendFailure:
    @pytest_asyncio.fixture(scope='class', autouse=True, params=(
        prepare_already_friended,
        prepare_already_requested,
        prepare_outgoing_block,
        prepare_incoming_block,
    ))
    async def response(self, request, create_user, create_relationship):
        prepared_coro = await request.param(create_user, create_relationship)
        return await prepared_coro

    def test_response(self, response):
        assert response.code == 400
