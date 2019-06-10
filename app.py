from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'very-seceret'
socketio = SocketIO(app)


# Flask or Socket.IO transport layer can be added here!

@socketio.on('connect')
def client_connect():
    print('client connected')

@socketio.on('disconnect')
def client_disconnect():
    print('client disconnect')


if __name__ == '__main__':
    app.debug = True
    socketio.run(app, port=2345)