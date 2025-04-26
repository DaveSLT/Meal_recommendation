from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import db, User, Preference, Meal, Category, Ingredient, MealIngredient, Rating, Favorite
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import os
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

# Landing page route
@views.route('/')
def home():
    if current_user.is_authenticated:
        # Check if user has set preferences
        user_pref = Preference.query.filter_by(user_id=current_user.id).first()
        
        if not user_pref:
            # New user who hasn't set preferences yet
            flash('Please set your meal preferences to get personalized recommendations!', category='info')
            return redirect(url_for('views.preferences'))
        
        # Get recommended meals for the user
        recommended_meals = get_recommended_meals(current_user.id)
        
        # Helper function for template to get category color
        def get_category_color(category):
            colors = {
                'pasta': '#dc3545',      # red
                'salad': '#28a745',      # green
                'seafood': '#007bff',    # blue
                'dessert': '#e83e8c',    # pink
                'breakfast': '#ffc107',  # amber
                'dinner': '#6f42c1',     # purple
                'vegetarian': '#28a745', # green
                'vegan': '#20c997',      # teal
                'omnivore': '#fd7e14'    # orange
            }
            return colors.get(category.lower(), '#6c757d')  # default gray
            
        return render_template("meal_recommendation.html", user=current_user, meals=recommended_meals, get_category_color=get_category_color)
    else:
        return render_template("landing.html", user=current_user)

@views.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    # Get existing preferences or create new ones
    user_pref = Preference.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        diet_type = request.form.get('diet_type')
        allergies = request.form.get('allergies')
        favorite_cuisine = request.form.get('favorite_cuisine')
        disliked_ingredients = request.form.get('disliked_ingredients')
        calorie_preference = request.form.get('calorie_preference')
        meal_complexity = request.form.get('meal_complexity')
        cooking_time = request.form.get('cooking_time')
        spice_level = request.form.get('spice_level')
        
        if user_pref:
            # Update existing preferences
            user_pref.diet_type = diet_type
            user_pref.allergies = allergies
            user_pref.favorite_cuisine = favorite_cuisine
            user_pref.disliked_ingredients = disliked_ingredients
            user_pref.calorie_preference = calorie_preference
            user_pref.meal_complexity = meal_complexity
            user_pref.cooking_time = cooking_time
            user_pref.spice_level = spice_level
        else:
            # Create new preferences
            user_pref = Preference(
                user_id=current_user.id,
                diet_type=diet_type,
                allergies=allergies,
                favorite_cuisine=favorite_cuisine,
                disliked_ingredients=disliked_ingredients,
                calorie_preference=calorie_preference,
                meal_complexity=meal_complexity,
                cooking_time=cooking_time,
                spice_level=spice_level
            )
            db.session.add(user_pref)
            
        db.session.commit()
        flash('Preferences saved successfully!', category='success')
        return redirect(url_for('views.home'))
    
    # Use the preferences.html template
    return render_template("preferences.html", user=current_user, preferences=user_pref)

@views.route('/recommendations')
@login_required
def recommendations():
    # Since we've moved recommendations to the home page, 
    # we'll just redirect to home
    return redirect(url_for('views.home'))

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_pref = Preference.query.filter_by(user_id=current_user.id).first()
    return render_template("user_profile.html", user=current_user, preferences=user_pref)

@views.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        bio = request.form.get('bio')
        
        # Check if username or email already exists
        if username != current_user.username:
            user_exists = User.query.filter_by(username=username).first()
            if user_exists:
                flash('Username already exists.', category='error')
                return redirect(url_for('views.profile'))
        
        if email != current_user.email:
            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                flash('Email already exists.', category='error')
                return redirect(url_for('views.profile'))
        
        # Update user profile
        current_user.username = username
        current_user.email = email
        # Add bio field to User model if needed
        # current_user.bio = bio
        
        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('views.profile'))

@views.route('/update_profile_picture', methods=['POST'])
@login_required
def update_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file part', category='error')
        return redirect(url_for('views.profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file', category='error')
        return redirect(url_for('views.profile'))
    
    if file:
        filename = secure_filename(file.filename)
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join('website', 'static', 'uploads', 'profile_pictures')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Update user profile picture path in database
        relative_path = f'/static/uploads/profile_pictures/{filename}'
        current_user.profile_picture = relative_path
        db.session.commit()
        
        flash('Profile picture updated successfully!', category='success')
    
    return redirect(url_for('views.profile'))

@views.route('/meal/<int:meal_id>')
@login_required
def meal_detail(meal_id):
    # Fetch the meal from the database
    meal = Meal.query.get_or_404(meal_id)
    
    # Get similar meals (same cuisine or diet type)
    similar_meals = Meal.query.filter(
        (Meal.cuisine == meal.cuisine) | (Meal.diet_type == meal.diet_type),
        Meal.id != meal.id
    ).limit(3).all()
    
    # Helper function for template to get category color
    def get_category_color(category):
        colors = {
            'pasta': '#dc3545',      # red
            'salad': '#28a745',      # green
            'seafood': '#007bff',    # blue
            'dessert': '#e83e8c',    # pink
            'breakfast': '#ffc107',  # amber
            'dinner': '#6f42c1',     # purple
            'vegetarian': '#28a745', # green
            'vegan': '#20c997',      # teal
            'omnivore': '#fd7e14'    # orange
        }
        return colors.get(category.lower(), '#6c757d')  # default gray
    
    return render_template("meal_detail.html", user=current_user, meal=meal, meals=similar_meals, get_category_color=get_category_color)

@views.route('/favorites')
@login_required
def favorites():
    # Fetch the user's favorite meals from the database
    favorite_records = Favorite.query.filter_by(user_id=current_user.id).all()
    favorite_meal_ids = [fav.meal_id for fav in favorite_records]
    favorite_meals = Meal.query.filter(Meal.id.in_(favorite_meal_ids)).all()
    
    # Helper function for template to get category color
    def get_category_color(category):
        colors = {
            'pasta': '#dc3545',      # red
            'salad': '#28a745',      # green
            'seafood': '#007bff',    # blue
            'dessert': '#e83e8c',    # pink
            'breakfast': '#ffc107',  # amber
            'dinner': '#6f42c1',     # purple
            'vegetarian': '#28a745', # green
            'vegan': '#20c997',      # teal
            'omnivore': '#fd7e14'    # orange
        }
        return colors.get(category.lower(), '#6c757d')  # default gray
    
    return render_template("favorites.html", user=current_user, meals=favorite_meals, get_category_color=get_category_color)

@views.route('/browse')
@login_required
def browse():
    # Fetch all meals from the database
    all_meals = Meal.query.all()
    
    # Helper function for template to get category color
    def get_category_color(category):
        colors = {
            'pasta': '#dc3545',      # red
            'salad': '#28a745',      # green
            'seafood': '#007bff',    # blue
            'dessert': '#e83e8c',    # pink
            'breakfast': '#ffc107',  # amber
            'dinner': '#6f42c1',     # purple
            'vegetarian': '#28a745', # green
            'vegan': '#20c997',      # teal
            'omnivore': '#fd7e14'    # orange
        }
        return colors.get(category.lower(), '#6c757d')  # default gray
    
    return render_template("browse.html", user=current_user, meals=all_meals, get_category_color=get_category_color)

@views.route('/api/toggle-favorite/<int:meal_id>', methods=['POST'])
@login_required
def toggle_favorite(meal_id):
    # Check if meal exists
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if already a favorite
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id, 
        meal_id=meal_id
    ).first()
    
    if existing_favorite:
        # Remove from favorites
        db.session.delete(existing_favorite)
        db.session.commit()
        return jsonify({'status': 'success', 'isFavorite': False})
    else:
        # Add to favorites
        new_favorite = Favorite(
            user_id=current_user.id,
            meal_id=meal_id
        )
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status': 'success', 'isFavorite': True})

@views.route('/api/rate-meal/<int:meal_id>', methods=['POST'])
@login_required
def rate_meal(meal_id):
    rating_value = request.json.get('rating')
    
    # Check if meal exists
    meal = Meal.query.get_or_404(meal_id)
    
    # Check if user already rated this meal
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id, 
        meal_id=meal_id
    ).first()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_value
    else:
        # Create new rating
        new_rating = Rating(
            user_id=current_user.id,
            meal_id=meal_id,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    db.session.commit()
    return jsonify({'status': 'success', 'rating': rating_value})

# Helper function to get recommended meals for a user
def get_recommended_meals(user_id, limit=None):
    # Get user preferences
    user_pref = Preference.query.filter_by(user_id=user_id).first()
    
    if not user_pref:
        # If no preferences, return all meals
        meals = Meal.query.all()
    else:
        # Start with a base query
        query = Meal.query
        
        # Filter by diet type if specified
        if user_pref.diet_type:
            query = query.filter(Meal.diet_type == user_pref.diet_type)
        
        # Filter by cuisine if specified
        if user_pref.favorite_cuisine:
            query = query.filter(Meal.cuisine == user_pref.favorite_cuisine)
        
        # Filter out meals with disliked ingredients
        if user_pref.disliked_ingredients:
            disliked = [ing.strip() for ing in user_pref.disliked_ingredients.split(',')]
            for ingredient in disliked:
                # This is a simplified approach - in a real app, you'd need a more complex query
                # to check ingredients through the MealIngredient relationship
                query = query.filter(~Meal.name.contains(ingredient))
        
        # Get meals matching preferences
        meals = query.all()
        
        # If no meals match the strict criteria, fall back to cuisine only
        if not meals and user_pref.favorite_cuisine:
            meals = Meal.query.filter(Meal.cuisine == user_pref.favorite_cuisine).all()
        
        # If still no meals, fall back to diet type only
        if not meals and user_pref.diet_type:
            meals = Meal.query.filter(Meal.diet_type == user_pref.diet_type).all()
        
        # If still no meals, return all meals
        if not meals:
            meals = Meal.query.all()
    
    # Apply limit if specified
    if limit and len(meals) > limit:
        meals = meals[:limit]
    
    return meals
