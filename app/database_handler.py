import sys
import os
from flask_login import UserMixin
from pymongo import MongoClient, mongo_client
import pymongo
import bcrypt

user_ID = 1

class DB(object):
    URI = "mongo"

    @staticmethod
    def init():
        client = pymongo.MongoClient(DB.URI)
        DB.DATABASE = client['sample_app']
        print(f"DATABASE INITIALIZED in INIT")
        
    @staticmethod
    def insert(collection, data):
        print(f"INSERTING into {collection}: {data}")
        DB.DATABASE[collection].insert_one(data)

    @staticmethod
    def find_one(collection, query):
        print(f"FINDING {collection} using {query}")
        print(f"{DB.DATABASE[collection].find_one(query)}")
        return DB.DATABASE[collection].find_one(query)
    

class User(UserMixin):
    user_id = user_ID
    username = None
    #hashedPassword = None
    authenticated = False

    def __init__(self, user_id, username, password):
        print("INITIALIZING USER")
        if user_id == None:
            print("userid = None")
            user = get_user_by_username(username)
            print(user)
            if user:
                if checkPasswordHash(user["password"], password, user["salt"]):
                    self.username = user["username"]
                    #self.hashedPassword = user["password"]
                    self.user_id = user["user_ID"]
                    self.authenticated = True

        if self.username == None and password == None:
            print("userid!=None")
            print(f"userID: {self.user_id}")
            user = get_user_by_id(self.user_id)
            print(f"USER ROW:{user}")
            if not user:
                return None
            self.username = user["username"]
            #self.hashedPassword = user["password"]
            self.user_id = user["user_ID"]
            self.authenticated = True

        # else:
        #     return None

    def login(self, username, password):
        if user_login(username, password):
            self.authenticated = True
        return self.authenticated

    def is_authenticated(self):
        return self.authenticated

    # This is a required method for Flask_login functionality.
    # for now it always returns true, but if we add functionality to ban/suspend users would change this.
    def is_active(self):
        return True
    
    def get_username(self):
        return self.username
    
    # similar to is_active, required for Flask_login
    def is_anonymous(self):
        return False

    # returns unicode user_id
    def get_id(self):
        return str(self.user_id).encode()
        
def init(mongo):
    print(f"INITIALIZED DATABASE")
    

def user_login(username,password):
    row = DB.find_one("userDetails",{"username":username})
    if row == None:
        return False
    hashed = row["password"] #decoded form
    login_salt = str.encode(row["salt"])
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), login_salt)
    loginPass = hashedPassword.decode()
    print(f"LOGINPASS: {loginPass}, hashed: {hashed}")
    if loginPass == hashed:
        return True
    return False
    
def signup_user(email,username,password):
    global user_ID
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    if (DB.find_one("userDetails",{"email": email}) != None) or (DB.find_one("userDetails",{"username":username}) != None):
        print("SIGNUP FAILED")
        return False
    if (DB.find_one("userDetails",{"email": email})==None) and (DB.find_one("userDetails",{"username":username}) == None):
        #hashedPassword = generate_password_hash(password, method='sha256')
        userDetails = {"user_ID": user_ID,"email": email, "username": username, "password": hashed.decode(), "salt": salt.decode()}
        user_ID+=1
        DB.insert("userDetails",userDetails)
        DB.find_one("userDetails",{"email": email})
        print("SIGNUP SUCCESS")
        return True #signup pass
    return False #signup failed

def get_user_by_username(username):
    row = DB.find_one("userDetails",{"username": username})
    return row

def get_user_by_id(id):
    row = DB.find_one("userDetails",{"user_ID": id})
    if row == None:
        return False
    return row
    
def saveImageDB(filename,username):
    DB.insert("imageCollection",{username: filename})
    
def checkPasswordHash(dbPassword, checkPass, salt):
    hashedCheck = bcrypt.hashpw(checkPass.encode('utf-8'), salt)
    if(hashedCheck == dbPassword):
        return True
    return False
    