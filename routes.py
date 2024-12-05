from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Task, Role
from functools import wraps
import jwt
from dotenv import load_dotenv
import os
from app import app

load_dotenv()
app.config['SECRET_KEY']= os.getenv('SECRET_KEY')

##adding user-specific permissions and features i.e. role-based access control
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message":"Token is missing"}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first_or_404()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token is expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated
@app.route('/')
def home():
    return "<h1>Homepage!</h1>" #to adjust

@app.route('/about')
def about():
    return "<h1>About page!</h1>" #to adjust

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

@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    # Get the page and per_page parameters from the query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Use SQLAlchemy's paginate method
    tasks_paginated = Task.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)

    # Prepare the paginated data
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "deadline": task.deadline,
        }
        for task in tasks_paginated.items
    ]

    # Create the response with pagination metadata
    response = {
        "tasks": tasks_data,
        "pagination": {
            "total": tasks_paginated.total,
            "pages": tasks_paginated.pages,
            "current_page": tasks_paginated.page,
            "per_page": tasks_paginated.per_page,
            "has_next": tasks_paginated.has_next,
            "has_prev": tasks_paginated.has_prev,

        },
    }

    return jsonify(response), 200

@app.route('/create_task', methods=['POST'])
@token_required
def create_task():
    title = request.json.get('title')
    description = request.json.get('description')
    deadline =request.json.get('deadline')
    user_id = request.json.get('user_id')
    priority = request.json.get('priority', 'medium')
    
    if priority not in dict(Task.PRIORITY_CHOICES ).keys():
        return jsonify({"message": "Invalid priority"}), 400
    
    task = Task(title=title, description=description, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    
    return jsonify({"message": "Task created successfully"}), 201

@app.route('/task/<int:id>/set_deadline', method=['PATCH'])
@token_required
def set_deadline(current_user, id):
    task=Task.query.filter_by(user_id=current_user.id, id=id).first_or_404()
    if not task:
        return jsonify({"message":"Task does not exist"}), 401
    
    task.title = request.json.get('title')
    task.deadline = request.json.get('deadline')
    
    db.session.commit()
    
    return jsonify({"message":"Task deadline successfully updated"}), 200

#to update new deadlines for a preset deadline task
    
@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    page = request.args.get('page', 1, type=int) #added pagination to the get_tasks function to avoid overcrowding
    per_page = request.args.get('per_page', 10, type=int)
    tasks_paginated = Task.query.filter_by(user_id=current_user.id).all().paginate(page = page, per_page=per_page, error_out=False)
    
    tasks_data = [{
        "id": task.id, 
        "title": task.title, 
        "description": task.description} for task in tasks_paginated.items]
    
    response = {
        "tasks": tasks_data,
        "pagination": {
            "total": tasks_paginated.total,
            "pages": tasks_paginated.pages,
            "current_page": tasks_paginated.page,
            "per_page": tasks_paginated.per_page,
            "has_next": tasks_paginated.has_next,
            "has_prev": tasks_paginated.has_prev
        }
    }
    return jsonify({"Tasks": tasks_data}), 200

@app.route('/task/<int:id>/update_task', methods=['PUT', 'DELETE']) #updating task name, description, deadlines, and delete functionality
@token_required
def update_task(current_user, task_id):
    task = Task.query.filter_by(id=task.id, user_id=current_user.id).first_or_404()
    if not task:
        return jsonify({"message":"Task does not exist"}), 401
    
    if request.method == 'PUT':
        task.title = request.json.get('title', task.title)
        task.description = request.json.get('description', task.description)
        task.deadline = request.json.get('deadline', task.deadline) #added an update deadline feature
        db.session.commit()
        
        return jsonify ({"message": "Task succcessfully updated!"}), 200
    
    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message":"Task successfully deleted!"}), 200
        
        

# @app.route('/task', methods=['GET', 'POST']) #should remove the GET method after adding user authentication
# def create_and_retrieve_task():
#     if request.method == 'GET':
#         task_id = request.args.get('task_id')
#         task = Task.query.get(task_id)
#         if not task:
#             return jsonify({"message": "Task not found"}), 404
#         return jsonify({"title": task.title, "description": task.description}), 200

#     if request.method == 'POST':
#         title = request.json.get('title')
#         description = request.json.get('description')
#         user_id = request.json.get('user_id')
        
#         task = Task(title=title, description=description, user_id=user_id)
#         db.session.add(task)
#         db.session.commit()
        
#         return jsonify({"message": "Task created successfully"}), 201



