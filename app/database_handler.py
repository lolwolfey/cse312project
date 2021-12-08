import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, mongo_client
import pymongo

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
    

class User:
    user_id = None
    email = None
    username = None
    hashedPassword = None
    authenticated = False

   # A user object can be made in 2 ways, username and password or user id. the other values should be none.
    def __init__(self, user_id, username, password):
        if user_id == None:
            user = get_user_by_username(username)
            if user:
                if check_password_hash(user["password"], password):
                    self.email = user["email"]
                    self.username = user["username"]
                    self.hashedPassword = user["password"]
                    self.user_id = user["_id"]
                    self.authenticated = True

        # Exccpets a unicode ID, must return None id an invalid Id is provided.
        elif username == None and password == None:
            try:
                user_id = int(user_id)
            except ValueError:
                return None
            user = get_user_by_id(user_id)
            if not user:
                return None
            self.email = user["email"]
            self.username = user["username"]
            self.hashedPassword = user["password"]
            self.user_id = user["_id"]
            self.authenticated = True

        else:
            return None

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
    db_password = row["password"]
    if not check_password_hash(db_password, password):
        return False
    return True
    
def signup_user(email,username,password):
    if (DB.find_one("userDetails",{"email": email}) != None) or (DB.find_one("userDetails",{"username":username}) != None):
        print("SIGNUP FAILED")
        return False
    if (DB.find_one("userDetails",{"email": email})==None) and (DB.find_one("userDetails",{"username":username}) == None):
        hashedPassword = generate_password_hash(password, method='sha256')
        userDetails = {"email": email, "username": username, "password": hashedPassword}
        DB.insert("userDetails",userDetails)
        DB.find_one("userDetails",{"email": email})
        print("SIGNUP SUCCESS")
        return True #signup pass
    return False #signup failed

def get_user_by_username(username):
    row = DB.find_one("userDetails",{"username": username})
    if row == None:
        return False
    return row

def get_user_by_id(id):
    row = DB.find_one("userDetails",{"_id": id})
    if row == None:
        return False
    return row
    