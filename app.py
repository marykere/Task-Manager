from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug import generate_password_hash

app = Flask(__name__)

if __name__=="__main__":
    app.run(debug=True)
@app.route('/')
def home():
    return "<h1>Homepage!</h1>"

@app.route('/about')
def about():
    return "<h1>About page!</h1>"

@app.route('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    hashed_password = generate_password_hash()


