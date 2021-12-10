from logging import DEBUG
from flask import Flask, request
from flask.templating import render_template
from flask_login import LoginManager
import os

import socketio
from .database_handler import User,init
#from app.database_handler import DB
import app.database_handler
from flask_socketio import SocketIO

UPLOAD_FOLDER = 'app/static/uploads/'
Chat_Upload_Folder = 'app/static/Chat/'

debug = True
socketio = SocketIO()

def create_app():
    app=Flask(__name__)   

    database_handler.DB.init()
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['Chat_Upload_Folder'] = Chat_Upload_Folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SECRET_KEY'] = b'\nI\x18]\xc3\x96m*@\xbffG\xf5a.X'

    app.config.update(
        DEBUG = True,
        
        #email settings
    )


    # Initialize the ;login manager for Flask_login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # initialize database mongodb
    #init(mongo)

    # Initializes a user based on their user_id. This is used in Flask_login to store the current_user variable.
    @login_manager.user_loader
    def load_user(user_id):
        user = User(user_id, None, None)
        return user

    # Bluprints allow us to control the content users have access to. By creating a separate blueprint 
    # for authorization, we can remember which users are logged in and which are not.
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    socketio.init_app(app)

    return app
