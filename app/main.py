from typing import AsyncContextManager
from flask import Flask, render_template
from flask.blueprints import Blueprint
from flask_login.utils import login_required
import requests
from pymongo import MongoClient, mongo_client


main = Blueprint('main',__name__)


@main.route("/home")
@login_required
def home():
    return render_template('index.html')