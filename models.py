from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db=SQLAlchemy()

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    
    def set_password (self, password):
        self.password_hash = generate_password_hash(password)
    def check_password (self, password):
        return check_password_hash(self.password_hash, password)
    task = db.relationship('tasks', backref='user', lazy=True)
    role = db.relationship('roles', backref='user', lazy=True)
    
    def __refr__(self):
        return f"User: {self.username}, Email: {self.email}"
    
class Task(db.Model):
    __tablename__='tasks'
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    description=db.Column(db.String(250), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    role=db.relationship('Role', backref='task', lazy=True)
    def __repr__(self):
        return f"Task: {self.title}, Description: {self.description}, User: {self.user.username}"
    
class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), unique=True, nullable=False)
    description=db.Column(db.String(250), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    task_id=db.Column(db.Integer, db.ForeignKey(Task.id), nullable=False)
    
    def __repr__(self):
        return f"Role: {self.name}, Description: {self.description}, User: {self.user.username}, Task: {self.task.title}"