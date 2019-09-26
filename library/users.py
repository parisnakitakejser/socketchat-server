import time

from library import messages


def connect(conn=None, room=None, request=None):
    guest_vistor_count = 0
    username = f'Guest #{guest_vistor_count + 1}'

    conn['online-users'].update_one({
        'user_id': request.sid,
    }, {
        '$set': {
            'user_name': username,
            'user_rank': 'guest',
            'room': room,
            'connected_at': time.time(),
            'disconnected_at': None,
            'last_active_at': time.time(),
            'last_messages_at': None
        }
    }, upsert=True)

    messages.insert(
        conn=conn,
        user='system',
        user_id=request.sid,
        user_room=room,
        type='system',
        color='yellow',
        msg=username + ' has connected to this chat room'
    )

    return get_single_user_data(conn=conn, user_id=request.sid)


def disconnect(conn=None, room=None, request=None):
    user_data = get_single_user_data(conn=conn, user_id=request.sid)

    conn['online-users'].update_one({
        'user_id': request.sid,
    }, {
        '$set': {
            'disconnected_at': time.time(),
        }
    })

    messages.insert(
        conn=conn,
        user='system',
        user_id=request.sid,
        user_room=room,
        type='system',
        color='pink',
        msg=user_data['user_name'] + ' has disconnected from the chat room'
    )


def get_single_user_data(conn=None, user_id=None):
    user_data = conn['online-users'].find_one({
        'user_id': user_id
    })

    return user_data


def get_room_users(conn=None, room=None):
    room_data = conn['online-users'].find({
        'room': room,
        'disconnected_at': None
    })

    return room_data


def get_room_users_count(conn=None, room=None):
    count_online_users = conn['online-users'].count_documents({
        'room': room,
        'disconnected_at': None
    })

    return count_online_users


def change_room(conn=None, request=None, leave_room=None, go_to_room=None, username=None):
    conn['online-users'].update_one({
        'user_id': request.sid,
    }, {
        '$set': {
            'room': go_to_room,
        }
    })

    messages.insert(
        conn=conn,
        user='system',
        user_id=request.sid,
        user_room=leave_room,
        type='system',
        color='red',
        msg=f'{username} has left the room'
    )

    messages.insert(
        conn=conn,
        user='system',
        user_id=request.sid,
        user_room=go_to_room,
        type='system',
        color='green',
        msg=f'{username} has join the room'
    )

