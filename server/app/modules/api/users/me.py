from app.utils.handler import RequestHandler
# from app.utils.spec import spec


class Me(RequestHandler):
    async def get(self):
        user_query = """SELECT id, username, name
                        FROM users
                        WHERE id=$1;
                     """
        rooms_query = """SELECT id, name, description, owner_id, type, permission_level,
                                last_message.*
                         FROM rooms
                         INNER JOIN room_members ON room_members.room_id = rooms.id
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
                         WHERE room_members.user_id = $1;
                      """

        async with self.database.acquire() as conn:
            user_record = await conn.fetchrow(user_query, self.user_id)
            room_records = await conn.fetch(rooms_query, self.user_id)

        if not user_record:
            # the sky has fallen
            return self.send_error(500)

        me = {
            'id': user_record['id'],
            'name': user_record['name'],
            'username': user_record['username'],
            'rooms': {}
        }

        for record in room_records:
            if record['message_id']:
                message_author = {
                    'id': record['message_author_id'],
                    'name': record['message_author_name'],
                    'username': record['message_author_username']
                }

                last_message = {
                    'id': record['message_id'],
                    'content': record['message_content'],
                    'room_id': record['message_room_id'],
                    'author': message_author
                }

            else:
                last_message = None

            room = {
                'id': record['id'],
                'name': record['name'],
                'description': record['description'],
                'owner_id': record['owner_id'],
                'type': record['type'],
                'me': {
                    'permission_level': record['permission_level']
                },
                'last_message': last_message
            }

            me['rooms'][record['id']] = room

        self.finish(me)


def setup(app):
    return (f'/api/v{app.version}/users/me', Me)
