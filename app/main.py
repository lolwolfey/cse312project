from typing import AsyncContextManager
from flask import Flask, render_template, request, redirect, url_for
from flask.blueprints import Blueprint
from flask_login.utils import login_required
import requests
from pymongo import MongoClient, mongo_client
import os
from flask import session, current_app, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from .database_handler import init, update_user_id, User, saveImageDB #delete when merging?
from flask_login import current_user
from . import socketio
from app import database_handler
import requests


main = Blueprint('main',__name__)

onlineusers = []
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
imagecount = 0
imageNames = []
def allowed_file(filename):
    print(f"ALLOWED EXTENSION: {filename.rsplit('.', 1)[1].lower()}")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/home", methods =['POST', 'GET'])
@login_required
def home():
    global imagecount
    if request.method == 'POST':
        fileflag = 0
        file = request.files['upload']
        if file and allowed_file(file.filename):
            print("FILENAME ALLOWED")
                #filename = secure_filename(file.filename)
            filename = f"file0{str(imagecount)}.jpg"
            imagecount = imagecount + 1
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) #/static/uploads/filename
            print('upload_image filename: ' + os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            saveImageDB(os.path.join(current_app.config['UPLOAD_FOLDER'], filename),current_user.username)
            imageNames.append(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            print(f"TEMPLATE IMAGE NAME FILE {imageNames[0]}")
            return render_template('index.html',filename=filename, len = len(onlineusers), onlineuserslist=onlineusers)
            #image uploaded success
        else:
            flash('Allowed image types are -> png, jpg, jpeg','error')
            fileflag = 1
        

    #html templates to render
    if not (current_user.username in onlineusers):
        onlineusers.append(current_user.username)
    return render_template('index.html', len = len(onlineusers), onlineuserslist = onlineusers)


@main.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

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