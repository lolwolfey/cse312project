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
from flask_login import current_user, logout_user
from . import socketio
from app import database_handler,auth
import requests
from .auth import loggedInUsers
import random
import string

main = Blueprint('main',__name__)

#onlineusers = []
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
imagecount = 0
imageNames = []
global_filename = ""
userrn = ""

def allowed_file(filename):
    print(f"ALLOWED EXTENSION: {filename.rsplit('.', 1)[1].lower()}")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/home", methods =['POST', 'GET'])
@login_required
def home():
    global imagecount
    global userrn
    if request.method == 'POST':
        file = request.files['upload']
        xsrfToken = request.form['xsrf_token']
        if(xsrfToken != main.xsrfToken):
            render_template("Error.html")
        if file and allowed_file(file.filename):
            print(f"FILENAME ALLOWED {file.filename}")
            filename = f"file0{str(imagecount)}.jpg"
            imagecount = imagecount + 1
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename)) #/static/uploads/filename
            print('upload_image filename: ' + os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            saveImageDB(os.path.join(current_app.config['UPLOAD_FOLDER'], filename),current_user.username) #never used
            imageNames.append(filename)
            print(f"IMAGE NAMES {imageNames}")
            return render_template('index.html',filename=filename, len = len(loggedInUsers), onlineuserslist=loggedInUsers, uploaded=True,upvote=0)
            #image uploaded success
        else:
            flash('Allowed image types are -> png, jpg, jpeg','error') #add flash template in index.html file
        

    #html templates to render
    main.xsrfToken = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
    print(f"LOGGED IN USERS:{loggedInUsers}")
    print(f"CURRENT USER LOGGED IN: {current_user.username}")
    userrn = str(current_user.username)
    return render_template('index.html',len = len(loggedInUsers), onlineuserslist = loggedInUsers,lenimage=imagecount,xsrf=main.xsrfToken)


@main.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@main.route("/logout", methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    loggedInUsers.remove(userrn)
    print(f"AFTER LOGOUT: {loggedInUsers}")
    return redirect(url_for('auth.login'))


@socketio.on('connection')
@login_required
def connect(methods = ['GET', 'POST']):
    print("response")
    print(loggedInUsers)
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
    loggedInUsers[loggedInUsers.index(current_user.username)] = username
    current_user.username = username
    print(current_user.username)
    print("Recieved socket request, changing username to: " + str(username))
    print("current username is now changed to: " + current_user.username)
    #should just reload template with new username so no need to socket emit again
    
    return render_template('index.html', len = len(loggedInUsers), onlineuserslist = loggedInUsers, username=current_user.username)

@socketio.on('upvote')
@login_required
def upvote(upvotes, methods = ['GET','POST']):
    print("upvote request recieved")
    print(f"UPVOTES: {upvotes}")
    result = int(upvotes) + 1
    print(f"RESULT: {str(result)}")
    socketio.emit('upvote_received', result)