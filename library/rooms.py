from library import users


def get_all(conn=None):
    rooms_data = conn['rooms'].find({
    })

    data = []
    default_room = None

    for room in rooms_data:
        room['online'] = users.get_room_users_count(conn=conn, room=str(room['_id']))

        data.append(room)

        if room['default']:
            default_room = str(room['_id'])

    return {
        'data': data,
        'default': default_room
    }
