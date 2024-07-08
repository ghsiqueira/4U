from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from pymongo import MongoClient
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

# conexão com o MongoDB
client = MongoClient(Config.MONGO_URI)
db = client['revista_online']
users_collection = db['users']
pdfs_collection = db['pdfs']

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from routes import *

if __name__ == '__main__':
    socketio.run(app, debug=True)
