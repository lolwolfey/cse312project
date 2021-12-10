from flask import *
from flask import current_app
#from . import db
from flask_login import login_user, login_required, logout_user, current_user
#from .models import User
import sys
#import psycopg2
import os
from .database_handler import init, signup_user, user_login, saveImageDB, id_by_username, User#delete when merging
from pymongo import MongoClient, mongo_client
from app import *
import bcrypt
import random
import string




auth = Blueprint('auth', __name__)

imgcount = 0
userid = 0
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@auth.route("/")
def initialize():
    return redirect(url_for('auth.login'))


@auth.route("/login", methods =['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        xsrfTokenSent = request.form["xsrf_token"]
        if xsrfTokenSent != auth.xsrfToken: 
            print(f"{xsrfTokenSent} = {auth.xsrfToken}")
            print("test")
            return render_template("Error.html")
        print(f"USERNAME: {username} PASSWORD: {password}")
        user = User(None,username,password)
        if user.login(username, password):
            login_user(user, remember=True)
            print(f"SUCCESFULLY LOGGED IN!")
            #sendid = id_by_username(username)
            print(f"SEND THIS ID: {current_user.username}")
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.', 'error')

    auth.xsrfToken = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
    #test = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
   # print(test)
    print("why is this not working")
    print(f"xsrf: {auth.xsrfToken}")
    return render_template("Login.html",xsrf=auth.xsrfToken)

@auth.route("/signup", methods=['POST','GET'])
def handle_form():
    global imgcount
    if request.method == 'POST':
        print(f"REQUEST.FORM = {request.form}")
        xsrfTokenSent = request.form["xsrf_token"]
        if(xsrfTokenSent != auth.xsrfToken):
            print(f"{xsrfTokenSent} = {auth.xsrfToken}")
            print("test")
            return render_template("Error.html")
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        print(f"EMAIL: {email}, PASSWORD: {password1}, CONFIRM PASS: {password2}")
        #if 'file' not in request.files:
        #    flash('No file part', 'error')
        #    return redirect(request.url)
        file = request.files['upload']
        if password1 == password2 == "":
            flash('Invalid password entered')
        if password1 == password2:
            valid, error = password_requirements(password1)
            print(f"VALID: {valid}, ERROR: {error}")
            if valid == True:
                if(email_requirements(email) == True):
                    if signup_user(email, username, password1,file,imgcount) == True:
                        imgcount+=1
                        flash('Account created', 'info')
                        return redirect(url_for('auth.login'))
                    elif signup_user(email, username, password1,file,imgcount) == False:
                        flash('That username/email address is already attached to an account or image you uploaded is not of type .png, .jpg, .jpeg', 'error')
                else:
                     flash('Email entered is invalid, try again.', 'error')
            else:
                for err in error:
                    flash(err, 'error')
        elif password1 != password2:
            flash('Passwords do not match.', 'error')
    auth.xsrfToken = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
    print(auth.xsrfToken)
    print("Test")
    return render_template("Signup.html",xsrf=auth.xsrfToken)         


@auth.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
# The following Password requirements must be met:
# At least 8 characters long.
# 3 upper case letters.
# 3 lower case letters.
# 1 number.
# Returns a boolean valid parameter and a array of erros.
def password_requirements(password):
    count = 0
    upper_case = 0
    lower_case = 0
    number = 0
    valid = True
    error = []

    for char in password:
        count += 1
        if char.isupper():
            upper_case += 1
        elif char.islower():
            lower_case += 1
        elif char.isdigit():
            number += 1
    
    if count < 8:
        valid = False
        error.append('Must be at least 8 characters long.')
    if upper_case < 3:
        valid = False
        error.append('Must contain at least 3 capital letters.')
    if lower_case < 3:
        valid = False
        error.append('Must contain at least 3 lower case letters. ')
    if number < 1:
        valid = False
        error.append('Must contain at least 1 number.')

    if not valid:
        error.insert(0,'Invalid Password:')
    
    return valid, error

def email_requirements(email):
    if '@' in email and '.com' in email:
        return True
    else:
        return False



@auth.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

