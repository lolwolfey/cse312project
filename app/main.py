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
    return render_template('index.html', len = len(onlineusers), onlineuserslist = onlineusers)

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
def direct(comment, Methods = ['GET','POST']):
    print("message to blank sent")
    message = comment['myMessage']
    user = comment['usertomessage']
    result = str(user) + " has sent the message: " + str(message)
    socketio.emit('Direct',result, to=current_user.username)

@socketio.on('imageUpload')
@login_required
def updateLatestImage(image, Methods = ['GET','POST']):
    print(image)
    message = str(current_user.username) + " has uploaded the above image."
    socketio.emit('updatelatestimage', image)
    socketio.emit('updatelatestimageuser', message)
