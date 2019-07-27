from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from bson.json_util import dumps

import time
import datetime

import library
from library import messages

config = library.init_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config['flask']['secret_key']
socketio = SocketIO(app)


messeges = {
    'lobby': [],
    'members': []
}

# Flask or Socket.IO transport layer can be added here!

users_online = {}
guest_vistor_count = 0

@socketio.on('connect')
def client_connect():
    global guest_vistor_count

    print('client connected')

    room = 'lobby'

    users_online[request.sid] = {
        'username': f'Guest #{guest_vistor_count+1}',
        'rank': 'guest',
        'connected_time': time.time(),
        'room': room
    }
    guest_vistor_count += 1
    join_room(room)

    print(f'online users count: {len(users_online)}')
    print(users_online)

    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
    messages.insert(
        conn=mongodb_conn,
        user='system',
        user_id=request.sid,
        user_room=room,
        color='yellow',
        msg=users_online[request.sid]['username'] +' has connected to this chat room'
    )
    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=room, limit=5)), json=False, broadcast=True, room=room)
    mongodb_client.close()

    emit('USER_DATA', users_online[request.sid])
    emit('USER_ONLINE_PUBLIC_DATA', users_online)


@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')
    room = users_online[request.sid]['room']

    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
    messages.insert(
        conn=mongodb_conn,
        user='system',
        user_id=request.sid,
        user_room=room,
        color='pink',
        msg=users_online[request.sid]['username'] + ' has disconnected from the chat room'
    )
    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=room, limit=5)), json=False, broadcast=True, room=room)
    mongodb_client.close()

    emit('MESSAGE', messeges[room], broadcast=True, room=room)
    emit('USER_ONLINE_PUBLIC_DATA', users_online)

    del users_online[request.sid]


@socketio.on('SEND_MESSAGE')
def client_send_message(data):
    if data['msg'].strip() != '':
        mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
        room = users_online[request.sid]['room']

        print('client send message')

        messages.insert(
            conn=mongodb_conn,
            user_id=users_online[request.sid]['username'],
            user_room=room,
            color=data['color'],
            msg=data['msg']
        )

        emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=room, limit=5)), json=False, broadcast=True, room=room)
        mongodb_client.close()
    else:
        print('empty message, its not sending back')


@socketio.on('join')
def client_join_room(data):
    username = users_online[request.sid]['username']

    leave_room = users_online[request.sid]['room']
    go_to_room = data['room']

    join_room(go_to_room)
    users_online[request.sid]['room'] = go_to_room

    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)

    messages.insert(
        conn=mongodb_conn,
        user='system',
        user_id=request.sid,
        user_room=leave_room,
        color='red',
        msg=username +' has left the room'
    )

    messages.insert(
        conn=mongodb_conn,
        user='system',
        user_id=request.sid,
        user_room=go_to_room,
        color='green',
        msg=username +' has join the room'
    )

    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=leave_room, limit=5)), json=False, broadcast=True, room=leave_room)
    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=go_to_room, limit=5)), json=False, broadcast=True, room=go_to_room)
    mongodb_client.close()


@socketio.on('leave')
def client_join_room(data):
    pass


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)