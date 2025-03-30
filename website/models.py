from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(500))  # Increased from 150 to 500
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.relationship('Preference', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diet_type = db.Column(db.String(50))  # vegetarian, vegan, omnivore, etc.
    allergies = db.Column(db.String(200))  # comma-separated list of allergies
    favorite_cuisine = db.Column(db.String(100))  # Italian, Mexican, etc.
    disliked_ingredients = db.Column(db.String(200))  # comma-separated list

