from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(200), nullable=True)
    preferences = db.relationship('Preference', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    
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
    calorie_preference = db.Column(db.String(50), nullable=True)  # low, medium, high
    meal_complexity = db.Column(db.String(50), nullable=True)  # simple, moderate, complex
    cooking_time = db.Column(db.String(50), nullable=True)  # quick, medium, long
    spice_level = db.Column(db.String(50), nullable=True)  # mild, medium, hot

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), nullable=True)  # For category color coding
    meals = db.relationship('Meal', backref='category', lazy=True)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cuisine = db.Column(db.String(50), nullable=True)
    diet_type = db.Column(db.String(50), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)  # in minutes
    cook_time = db.Column(db.Integer, nullable=True)  # in minutes
    servings = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    complexity = db.Column(db.String(50), nullable=True)  # simple, moderate, complex
    spice_level = db.Column(db.String(50), nullable=True)  # mild, medium, hot
    
    ingredients = db.relationship('MealIngredient', backref='meal', lazy=True)
    ratings = db.relationship('Rating', backref='meal', lazy=True)
    favorites = db.relationship('Favorite', backref='meal', lazy=True)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    meal_ingredients = db.relationship('MealIngredient', backref='ingredient', lazy=True)

class MealIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    unit = db.Column(db.String(20), nullable=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    date_rated = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

