from flask import *
#from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
#from .models import User
import sys
#import psycopg2
import os
from .database_handler import init, signup_user, user_login, User#delete when merging
from pymongo import MongoClient, mongo_client
from werkzeug.utils import secure_filename
import string
import random

auth = Blueprint('auth', __name__)

imgcount = 0
xsrfToken = ""
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route("/")
def initialize():
    return redirect(url_for('auth.login'))


@auth.route("/login", methods =['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        xsrf = request.form['xsrf']
        print(f"xsrf: {xsrf}")



        print(f"USERNAME: {username} PASSWORD: {password}")
        user = User(None, username, password)
        if user.login(username, password):
            login_user(user, remember=True)
            print("SUCCESFULLY LOGGED IN!")
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.', 'error')
    xsrfToken = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
    print(xsrfToken)
    return render_template("Login.html")

@auth.route("/signup", methods=['POST','GET'])
def handle_form():
    if request.method == 'POST':
        print(f"REQUEST.FORM = {request.form}")
        username = request.form['username']
        email = request.form['email']
        password1 = request.form['password']
        xsrf = request.form['xsrf']
        print(f"xsrf: {xsrf}")  

        print(f"EMAIL: {email}, PASSWORD: {password1}")
        valid, error = password_requirements(password1)
        print(f"VALID: {valid}, ERROR: {error}")
        if valid == True:
            if(email_requirements(email) == True):
                if signup_user(email, username, password1) == True:
                    flash('Account created', 'info')
                    return redirect(url_for('auth.login'))
                elif signup_user(email, username, password1) == False:
                    flash('That username/email address is already attached to an account.', 'error')
            else:
                for err in error:
                    flash(err, 'error')
        else:
            flash('Passwords do not match.', 'error')
        
        # if 'file' not in request.files:
        #     flash('No file part', 'error')
        #     return redirect(request.url)
        file = request.files['upload']
        if file.filename == '':
            flash('No image selected for uploading','error')
        #return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = "file0"+str(imgcount)+".jpg"
            print(f"app.config upload folder; {app.config['UPLOAD_FOLDER']}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below','info')
        #return render_template('Signup.html', filename=filename)
        else:
            flash('Allowed image types are -> png, jpg, jpeg','error')
    #global xsrfToken
    xsrfToken = str(''.join(random.choices(string.ascii_letters + string.digits , k = 27)))
    print(xsrfToken)
    return render_template("Signup.html",xsrf = xsrfToken)

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

