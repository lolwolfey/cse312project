from typing import AsyncContextManager
from flask import Flask, render_template
from flask.blueprints import Blueprint
from flask_login.utils import login_required
import requests
from pymongo import MongoClient, mongo_client

from flask import session
from flask_socketio import SocketIO, emit, join_room, leave_room
from .database_handler import init, update_user_id, User #delete when merging?
from flask_login import current_user
from . import socketio
from app import database_handler

main = Blueprint('main',__name__)

onlineusers = []

@main.route("/home")
@login_required
def home():
    #html templates to render
    if not (current_user.username in onlineusers):
        onlineusers.append(current_user.username)
    return render_template('index.html', len = len(onlineusers), onlineuserslist = onlineusers)

@socketio.on('connection')
@login_required
def connect(methods = ['GET', 'POST']):
    print("response")
    print(onlineusers)
    join_room(current_user.username)
    print("user",current_user.username)
    print("room successfully joined")
    socketio.emit('response', "response")

@socketio.on('submission')
@login_required
def submit(comment, methods = ['GET', 'POST']):
    print("response sent")
    socketio.emit('my_response', str(comment),broadcast=True)

@socketio.on('direct_message')
@login_required
def direct(comment, methods = ['GET','POST']):
    print("message to blank sent")
    message = comment['message']
    user = comment['username']
    result = str(user) + " has sent the message: " + str(message)
    socketio.emit('Direct',result, to=user)

@socketio.on('usernamechange')
@login_required
def change(username, methods = ['GET','POST']):
    database_handler.update_user_id(current_user.username,username)
    onlineusers[onlineusers.index(current_user.username)] = username
    current_user.username = username
    print(current_user.username)
    print("Recieved socket request, changing username to: " + str(username))
    print("current username is now changed to: " + current_user.username)
    #should just reload template with new username so no need to socket emit again
    
    return render_template('index.html', len = len(onlineusers), onlineuserslist = onlineusers, username=current_user.username)