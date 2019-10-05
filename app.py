from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from bson.json_util import dumps

import time
import datetime

import library
from library import messages
from library import users
from library import rooms

config = library.init_config()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
app.config['SECRET_KEY'] = config['flask']['secret_key']
socketio = SocketIO(app)

# Flask or Socket.IO transport layer can be added here!
@app.route('/ping')
def ping_service():
    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)

    if users.update_idle_time(conn=mongodb_conn, request=request):
        response_data = {
            'status': 'OK',
            'code': 200
        }
    else:
        response_data = {
            'status': 'ERROR',
            'code': 404
        }

    mongodb_client.close()

    return jsonify(response_data)


@socketio.on('connect')
def client_connect():
    print('client connected')

    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
    data_rooms = rooms.get_all(conn=mongodb_conn)
    default_room = data_rooms['default']

    user_data = users.connect(conn=mongodb_conn, room=default_room, request=request)

    join_room(default_room)

    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=default_room)), json=False, broadcast=True, room=default_room)

    emit('USER_DATA', dumps(user_data))
    emit('USER_ONLINE_PUBLIC_DATA', dumps(users.get_room_users(conn=mongodb_conn, room=default_room)), json=False, broadcast=True, room=default_room)
    emit('GET_ROOMS', dumps(data_rooms['data']), json=False, broadcast=True, room=default_room)
    mongodb_client.close()


@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')
    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)

    user_data = users.get_single_user_data(conn=mongodb_conn, user_id=request.sid)
    users.disconnect(conn=mongodb_conn, room=user_data['room'], request=request)

    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=user_data['room'])), json=False, broadcast=True, room=user_data['room'])
    mongodb_client.close()

    emit('USER_ONLINE_PUBLIC_DATA', dumps(users.get_room_users(conn=mongodb_conn, room=user_data['room'])), json=False, broadcast=True, room=user_data['room'])


@socketio.on('SEND_MESSAGE')
def client_send_message(data):
    if data['msg'].strip() != '':
        mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
        user_data = users.get_single_user_data(conn=mongodb_conn, user_id=request.sid)
        room = user_data['room']

        print('client send message')

        messages.insert(
            conn=mongodb_conn,
            user_id=request.sid,
            user_room=room,
            color=data['color'],
            msg=data['msg']
        )

        emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=room)), json=False, broadcast=True, room=room)
        mongodb_client.close()
    else:
        print('empty message, its not sending back')


@socketio.on('join')
def client_join_room(data):
    mongodb_conn, mongodb_client = library.init_mongodb_conn(config)
    user_data = users.get_single_user_data(conn=mongodb_conn, user_id=request.sid)
    username = user_data['user_name']

    leave_room = user_data['room']
    go_to_room = data['room']

    join_room(go_to_room)

    users.change_room(
        conn=mongodb_conn,
        request=request,
        leave_room=leave_room,
        go_to_room=go_to_room,
        username=username
    )

    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=leave_room)), json=False, broadcast=True, room=leave_room)
    emit('USER_ONLINE_PUBLIC_DATA', dumps(users.get_room_users(conn=mongodb_conn, room=leave_room)), json=False, broadcast=True, room=leave_room)

    emit('MESSAGE', dumps(messages.get(conn=mongodb_conn, room=go_to_room)), json=False, broadcast=True, room=go_to_room)
    emit('USER_ONLINE_PUBLIC_DATA', dumps(users.get_room_users(conn=mongodb_conn, room=go_to_room)), json=False, broadcast=True, room=go_to_room)

    data_rooms = rooms.get_all(conn=mongodb_conn)
    emit('GET_ROOMS', dumps(data_rooms['data']), json=False, broadcast=True, room=leave_room)
    emit('GET_ROOMS', dumps(data_rooms['data']), json=False, broadcast=True, room=go_to_room)

    mongodb_client.close()


@socketio.on('leave')
def client_leave_room(data):
    pass


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)