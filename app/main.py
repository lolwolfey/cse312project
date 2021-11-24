from flask import Flask, render_template
from flask.blueprints import Blueprint

main = Blueprint('main',__name__)

@main.route("/")
def home():
    return render_template('index.html')