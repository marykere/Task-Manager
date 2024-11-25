from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Task

app = Flask(__name__)

app.config['SECRET_KEY']=''

@app.route('/')
def home():
    return "<h1>Homepage!</h1>"

@app.route('/about')
def about():
    return "<h1>About page!</h1>"

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')
    
    # Check for duplicate user or email
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or Email already exists"}), 400

    # Validate all fields
    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check if passwords match
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    # Create and save the new user
    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401
    
    return jsonify({"message": "Logged in successfully"}), 200

@app.route('/create_task', methods=['POST'])
def create_task():
    title = request.json.get('title')
    description = request.json.get('description')
    user_id = request.json.get('user_id')
    
    task = Task(title=title, description=description, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/task', methods=['GET', 'POST'])
def create_and_retrieve_task():
    if request.method == 'GET':
        task_id = request.args.get('task_id')
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"message": "Task not found"}), 404
        return jsonify({"title": task.title, "description": task.description}), 200

    if request.method == 'POST':
        title = request.json.get('title')
        description = request.json.get('description')
        user_id = request.json.get('user_id')
        
        task = Task(title=title, description=description, user_id=user_id)
        db.session.add(task)
        db.session.commit()
        
        return jsonify({"message": "Task created successfully"}), 201



