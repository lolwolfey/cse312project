from typing import AsyncContextManager
from flask import Flask, render_template
from flask.blueprints import Blueprint
from flask_login.utils import login_required
import requests
from pymongo import MongoClient, mongo_client

from flask import session
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from . import socketio


main = Blueprint('main',__name__)


@main.route("/home")
@login_required
def home():
    print(f"CURRENT USER USERNAME: {current_user.username}")
    return render_template('index.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
    
# @socketio.event
# def connect():
#     if current_user.is_authenticated:
#         print("response")
#         join_room(current_user.username) #User
#         emit('my_response', {'data': 'Connected', 'count': current_user.username})
#     else:
#         return False # not logged in