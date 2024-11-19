from flask_sqlalchemy import SQLAlchemy
import app
from werkzeug import generate_password_hash, check_password_hash

db=SQLAlchemy()

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Colum(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)