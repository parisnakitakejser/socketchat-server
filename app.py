from flask import Flask, request
from flask_socketio import SocketIO, emit

import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-seceret'
socketio = SocketIO(app)


messeges = [{
    'color': '#abc',
    'user': 'User 1',
    'msg': 'Hello world, welcom to SocketChat'
}, {
    'color': '#cba',
    'user': 'User 2',
    'msg': 'Thanks for invete me!'
}, {
    'color': '#bac',
    'user': 'User 3',
    'msg': 'Somone want to chat?'
}]

# Flask or Socket.IO transport layer can be added here!

users_online = {}
guest_vistor_count = 0

@socketio.on('connect')
def client_connect():
    global guest_vistor_count

    print('client connected')

    users_online[request.sid] = {
        'username': f'Guest #{guest_vistor_count+1}',
        'rank': 'guest',
        'connected_time': time.time()
    }
    guest_vistor_count += 1

    print(f'online users count: {len(users_online)}')
    print(users_online)
    emit('MESSAGE', messeges)
    emit('USER_DATA', users_online[request.sid])


@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')
    del users_online[request.sid]


@socketio.on('SEND_MESSAGE')
def client_send_message(data):
    if data['msg'].strip() != '':
        print('client send message')

        if len(messeges) >= 5:
            print('pop the old messagt from the messagt queue')
            messeges.pop(0)

        messeges.append({
            'color': data['color'],
            'user': users_online[request.sid]['username'],
            'msg': data['msg']
        })

        emit('MESSAGE', messeges, broadcast=True)
    else:
        print('empty message, its not sending back')


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)