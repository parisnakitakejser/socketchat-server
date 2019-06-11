from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-seceret'
socketio = SocketIO(app)


messeges = [{
    'color': '#abc',
    'user': 'User 1',
    'msg': 'Hello world, welcom to CocketChat'
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

@socketio.on('connect')
def client_connect():
    print('client connected')
    emit('MESSAGE', messeges)

@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)