from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-seceret'
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

    messeges[room].append({
        'color': 'yellow',
        'user': 'System',
        'msg': users_online[request.sid]['username'] +' has connected to this chat room'
    })

    emit('MESSAGE', messeges[room], broadcast=True, room=room)
    emit('USER_DATA', users_online[request.sid])
    emit('USER_ONLINE_PUBLIC_DATA', users_online)


@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')
    room = users_online[request.sid]['room']
    messeges[room].append({
        'color': 'pink',
        'user': 'System',
        'msg': users_online[request.sid]['username'] + ' has disconnected from the chat room'
    })

    emit('MESSAGE', messeges[room], broadcast=True, room=room)
    emit('USER_ONLINE_PUBLIC_DATA', users_online)

    del users_online[request.sid]


@socketio.on('SEND_MESSAGE')
def client_send_message(data):
    if data['msg'].strip() != '':
        room = users_online[request.sid]['room']

        print('client send message')

        if len(messeges) >= 5:
            print('pop the old messagt from the messagt queue')
            messeges.pop(0)

        messeges[room].append({
            'color': data['color'],
            'user': users_online[request.sid]['username'],
            'msg': data['msg']
        })

        emit('MESSAGE', messeges[room], broadcast=True, room=room)
    else:
        print('empty message, its not sending back')


@socketio.on('join')
def client_join_room(data):
    username = users_online[request.sid]['username']

    leave_room = users_online[request.sid]['room']
    go_to_room = data['room']

    join_room(go_to_room)
    users_online[request.sid]['room'] = go_to_room

    messeges[leave_room].append({
        'color': 'red',
        'user': 'System',
        'msg': username +' has left the room'
    })

    messeges[go_to_room].append({
        'color': 'green',
        'user': 'System',
        'msg': username +' has join the room'
    })

    emit('MESSAGE', messeges[leave_room], broadcast=True, room=leave_room)
    emit('MESSAGE', messeges[go_to_room], broadcast=True, room=go_to_room)


@socketio.on('leave')
def client_join_room(data):
    pass


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)