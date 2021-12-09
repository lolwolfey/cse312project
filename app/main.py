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

main = Blueprint('main',__name__)

onlineusers = []

@main.route("/home")
@login_required
def home():
    #html templates to render
    usertext = ""
    if onlineusers:
        for user in onlineusers:
            usertext += "<li id='user'" + onlineusers.index(user) + ">" + user + "</li><input type='text' id='myMessage'" + onlineusers.index(user) + "><button id='sendbutton" + onlineusers.index(user) + "'>send</button>"
    else:
        usertext = "There are no online users"
    return render_template('index.html', onlineuserslist = usertext)

@socketio.on('connection')
@login_required
def connect(methods = ['GET', 'POST']):
    print("response")
    join_room(current_user.username)
    if not (current_user.username in onlineusers):
        onlineusers.append(current_user.username)
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
def direct(comment, nethods = ['GET','POST']):
    print("message to blank sent")
    socketio.emit('Direct',str(comment), to=current_user.username)
