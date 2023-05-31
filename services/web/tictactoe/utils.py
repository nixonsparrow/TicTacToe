from flask_socketio import SocketIO

socketio = SocketIO(
    cors_allowed_origins=["localhost", "http://localhost:1337", "http://localhost:5000"]
)
