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


class TestRelationshipFriendRequestSuccess:
    @pytest_asyncio.fixture(scope='class', autouse=True)
    async def response(self, create_user, create_relationship):
        user1 = await create_user(None, name='.', password='.', email='test@email.com')
        user2 = await create_user(None, name='.', password='.', email='test2@email.com')

        return await create_relationship(RelationshipType.friend, user1['id'], user2['id'])

    def test_response(self, response):
        assert response.code == 200

    def test_cache(self, app):
        assert len(app.relationship_cache) == 1

    @pytest.mark.asyncio
    async def test_database(self, database):
        query = 'SELECT 1 FROM relationships;'
        records = await database.pool.fetch(query)
        assert len(records) == 1
