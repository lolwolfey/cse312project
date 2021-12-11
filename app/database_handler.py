import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pymongo import MongoClient, mongo_client
import pymongo


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
    def update_one(collection,query,newvalues):
        print(f"FINDING {collection} using {query}")
        return DB.DATABASE[collection].update_one(query,newvalues)

    @staticmethod
    def find_one(collection, query):
        print(f"FINDING {collection} using {query}")
        print(f"{DB.DATABASE[collection].find_one()}")
        #print("findONE",DB.DATABASE[collection].find())
        users = None
        x = DB.DATABASE[collection]
        for i in x.find():
            if query in i.values():
                print(query)
                print(i)
                users = i
        print("Current_user",users)
        return users
    

class User(UserMixin):
    user_id = user_ID
    username = None
    hashedPassword = None
    authenticated = False

    def __init__(self, user_id, username, password):
        print("INITIALIZING USER")
        if user_id == None:
            print("userid = None")
            user = get_user_by_username(username)
            print(user)
            if user:
                if check_password_hash(user["password"], password):
                    self.username = user["username"]
                    self.hashedPassword = user["password"]
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
            self.hashedPassword = user["password"]
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
    row = DB.find_one("userDetails",username)
    
    if row == None:
        return False
    db_password = row["password"]
    if not check_password_hash(db_password, password):
        return False
    return True
    
def signup_user(email,username,password):
    global user_ID
    if (DB.find_one("userDetails",email) != None) or (DB.find_one("userDetails",username) != None):
        print("SIGNUP FAILED")
        return False
    if (DB.find_one("userDetails",email)==None) and (DB.find_one("userDetails",username) == None):
        hashedPassword = generate_password_hash(password, method='sha256')
        userDetails = {"user_ID": user_ID,"email": email, "username": username, "password": hashedPassword}
        user_ID = user_ID + 1
        print("USER_ID_USER",user_ID)
        DB.insert("userDetails",userDetails)
        DB.find_one("userDetails",email)
        print("SIGNUP SUCCESS")
        return True #signup pass
    return False #signup failed

def get_user_by_username(username):
    row = DB.find_one("userDetails",username)
    return row

def get_user_by_id(id):
    row = DB.find_one("userDetails",id)
    if row == None:
        return False
    return row

def update_user_id(oldusername, newusername):
    DB.update_one("userDetails", {"username":oldusername}, {"$set":{"username":newusername}})

def saveImageDB(filename,username):
    DB.insert("imageCollection",{username: filename})