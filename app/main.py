from typing import AsyncContextManager
from flask import Flask, render_template
from flask.blueprints import Blueprint
from flask_login.utils import login_required
import requests
from pymongo import MongoClient, mongo_client

from flask import session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from . import socketio
from .database_handler import User, id_by_username


main = Blueprint('main',__name__)

onlineusers = []

@main.route("/home")
@login_required
def home():
    print(f"user.user_id: {current_user.user_id}")
    print(f"user.username: {current_user.username}")
    if not (current_user.username in onlineusers):
        onlineusers.append(current_user.username)
    print(f"ONLINEUSERS: {onlineusers}")
    return render_template('index.html',len=len(onlineusers),onlineuserslist=onlineusers)

@socketio.on('connection')
def connect(methods = ['GET', 'POST']):
    print(f"response")
    join_room(current_user.username)
    print("user",current_user.username)
    print("room successfully joined")
    socketio.emit('response', "response")

@socketio.on('submission')
def submit(comment, methods = ['GET', 'POST']):
    print("response sent")
    socketio.emit('my_response', str(comment),broadcast=True)

@socketio.on('direct_message')
def direct(comment, methods = ['GET','POST']):
    print("message to blank sent")
    message = comment['message']
    user = comment['username']
    result = str(user) + " has sent the message: " + str(message)    
    #print(onlineusers)
    socketio.emit('Direct',result, to=user)
