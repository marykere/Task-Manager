from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import User, db, Task

app = Flask(__name__)

if __name__=="__main__":
    app.run(debug=True)
@app.route('/')
def home():
    return "<h1>Homepage!</h1>"

@app.route('/about')
def about():
    return "<h1>About page!</h1>"

@app.route('/register', methods =['POST'])
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    confirm_password = request.json['confirm_password']
    
    user = User(email=email, username=username)
    user.set_password(password)
    
    if user.query.filter_by(
        username=username).first() or User.query.filter_by(email=email):
        return jsonify({"message":"Username or Email already exists"}), 400
    
    if not username or email or password:
        return jsonify({"message":"All fields are required"}), 400
    
    if password!= confirm_password:
        return jsonify({"message":"Passwords do not match"}), 400
    
    db.session.add(user)
    db.session.commit(user)

    return jsonify ({"message":"User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"message":"Invalid email or password"}), 401
    
    return jsonify({"message":"Logged in successfully"}), 200

@app.route('/create_task', methods=['POST'])
def create_task():
    title = request.json['title']
    description = request.json['description']
    user_id = request.json['user_id']
    
    task = Task(title=title, description=description, user_id=user_id)
    
    db.session.add(task)
    db.session.commit(task)
    
    return jsonify({"message":"Task created succesfully"}), 201

@app.route('/task', methods=(['GET'], ['POST']))
def create_and_retrieve_task():
    if request.method==['GET']:
        task = User.query.get('task_id')
    if request.method==['POST']:
        id = request.json['id']
        title = request.json['title']
        description = request.json['description']
        user_id = request.json['user_id']
        
        task = Task(id=id, title=title, description=description, user_id=user_id)
        
        db.session.add(task)
        db.session.commit(task)
        
        return jsonify({"message":"Task created succesfully"}), 201


    


