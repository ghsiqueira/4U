from flask import Flask
from pymongo import MongoClient
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['UPLOAD_FOLDER_COVER'] = 'static/uploads/cover/'

# Configurando a conexão com o MongoDB
client = MongoClient("mongodb+srv://gbr:ghsiqueira@revista.ljczyc6.mongodb.net/?retryWrites=true&w=majority&appName=revista")
db = client['revista_online']
users_collection = db['users']
pdfs_collection = db['pdfs']

# Configurando Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from routes import *

if __name__ == '__main__':
    socketio.run(app, debug=True)
