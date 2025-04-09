from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import db, User, Preference, Meal, Category, Ingredient, MealIngredient, Rating, Favorite
from datetime import datetime
import random

views = Blueprint('views', __name__)

# Landing page route
@views.route('/')
def home():
    if current_user.is_authenticated:
        # Get recommended meals for the user
        recommended_meals = get_recommended_meals(current_user.id, limit=3)
        
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
            
        return render_template("home.html", user=current_user, meals=recommended_meals, get_category_color=get_category_color)
    else:
        return render_template("landing.html", user=current_user)  # Added user=current_user here

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
        return redirect(url_for('views.recommendations'))
    
    return render_template("gather_data.html", user=current_user, preferences=user_pref)

@views.route('/recommendations')
@login_required
def recommendations():
    user_pref = Preference.query.filter_by(user_id=current_user.id).first()
    
    if not user_pref:
        flash('Please set your meal preferences first!', category='error')
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

@views.route('/profile')
@login_required
def profile():
    user_pref = Preference.query.filter_by(user_id=current_user.id).first()
    return render_template("user_profile.html", user=current_user, preferences=user_pref)

@views.route('/meal/<int:meal_id>')
@login_required
def meal_detail(meal_id):
    # In a real app, you would fetch the meal from the database
    meal = next((m for m in MEALS if m['id'] == meal_id), None)
    
    if not meal:
        flash('Meal not found!', category='error')
        return redirect(url_for('views.recommendations'))
    
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
    
    return render_template("meal_detail.html", user=current_user, meal=meal, meals=MEALS, get_category_color=get_category_color)

@views.route('/favorites')
@login_required
def favorites():
    # In a real app, you would fetch the user's favorite meals from the database
    favorite_meals = [m for m in MEALS if m['id'] % 2 == 0]  # Just for demo purposes
    
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
    # In a real app, you would fetch all meals from the database
    all_meals = MEALS
    
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
    # In a real app, you would toggle the favorite status in the database
    return jsonify({'status': 'success', 'isFavorite': True})

@views.route('/api/rate-meal/<int:meal_id>', methods=['POST'])
@login_required
def rate_meal(meal_id):
    rating = request.json.get('rating')
    # In a real app, you would save the rating to the database
    return jsonify({'status': 'success', 'rating': rating})

# Helper function to get recommended meals for a user
def get_recommended_meals(user_id, limit=None):
    # In a real app, this would use the user's preferences to filter meals from the database
    # For now, we'll just return the sample meals
    recommended = MEALS
    if limit:
        recommended = recommended[:limit]
    return recommended

# Sample meal data - in a real app, this would come from a database
MEALS = [
    {
        'id': 1,
        'name': 'Spaghetti Bolognese',
        'description': 'A classic Italian pasta with rich meat sauce and parmesan cheese.',
        'cuisine': 'Italian',
        'diet_type': 'pasta',
        'ingredients': ['spaghetti', 'ground beef', 'tomato sauce', 'garlic', 'onions', 'parmesan cheese'],
        'image': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Cook the spaghetti according to package instructions. In a separate pan, brown the ground beef with garlic and onions. Add tomato sauce and simmer for 20 minutes. Serve the sauce over the pasta and top with grated parmesan cheese.',
        'prep_time': 15,
        'cook_time': 25,
        'servings': 4,
        'calories': 450,
        'protein': 25,
        'carbs': 65,
        'fat': 10,
        'complexity': 'simple',
        'spice_level': 'mild'
    },
    {
        'id': 2,
        'name': 'Chicken Caesar Salad',
        'description': 'A healthy, crunchy salad with grilled chicken and Caesar dressing.',
        'cuisine': 'American',
        'diet_type': 'salad',
        'ingredients': ['chicken breast', 'romaine lettuce', 'caesar dressing', 'parmesan cheese', 'croutons'],
        'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Grill the chicken breast until cooked through. Slice into strips. Wash and chop the romaine lettuce. Toss the lettuce with Caesar dressing. Top with grilled chicken, parmesan cheese, and croutons.',
        'prep_time': 10,
        'cook_time': 15,
        'servings': 2,
        'calories': 350,
        'protein': 30,
        'carbs': 15,
        'fat': 20,
        'complexity': 'simple',
        'spice_level': 'mild'
    },
    {
        'id': 3,
        'name': 'Grilled Salmon',
        'description': 'A light and healthy grilled salmon dish with lemon and herbs.',
        'cuisine': 'International',
        'diet_type': 'seafood',
        'ingredients': ['salmon fillet', 'lemon', 'garlic', 'olive oil', 'dill', 'black pepper'],
        'image': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Marinate the salmon fillet in olive oil, lemon juice, garlic, and herbs for 30 minutes. Grill the salmon for 4-5 minutes per side until cooked through. Serve with a lemon wedge and fresh dill.',
        'prep_time': 35,
        'cook_time': 10,
        'servings': 2,
        'calories': 300,
        'protein': 35,
        'carbs': 0,
        'fat': 18,
        'complexity': 'moderate',
        'spice_level': 'mild'
    },
    {
        'id': 4,
        'name': 'Vegetable Stir Fry',
        'description': 'A quick and healthy stir fry with seasonal vegetables and tofu.',
        'cuisine': 'Asian',
        'diet_type': 'vegetarian',
        'ingredients': ['tofu', 'broccoli', 'bell peppers', 'carrots', 'soy sauce', 'ginger', 'garlic'],
        'image': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Press and cube the tofu. Stir-fry the tofu until golden. Remove from the pan. Stir-fry the vegetables with ginger and garlic. Add the tofu back to the pan. Season with soy sauce and serve over rice.',
        'prep_time': 15,
        'cook_time': 10,
        'servings': 3,
        'calories': 250,
        'protein': 15,
        'carbs': 25,
        'fat': 12,
        'complexity': 'moderate',
        'spice_level': 'medium'
    },
    {
        'id': 5,
        'name': 'Beef Tacos',
        'description': 'Spicy beef tacos with fresh salsa and guacamole.',
        'cuisine': 'Mexican',
        'diet_type': 'dinner',
        'ingredients': ['ground beef', 'taco shells', 'lettuce', 'tomatoes', 'cheese', 'avocado', 'sour cream'],
        'image': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Brown the ground beef with taco seasoning. Warm the taco shells. Fill the shells with the beef, lettuce, tomatoes, cheese, guacamole, and sour cream.',
        'prep_time': 15,
        'cook_time': 15,
        'servings': 4,
        'calories': 400,
        'protein': 20,
        'carbs': 30,
        'fat': 25,
        'complexity': 'simple',
        'spice_level': 'hot'
    },
    {
        'id': 6,
        'name': 'Mushroom Risotto',
        'description': 'Creamy Italian rice dish with mushrooms and parmesan.',
        'cuisine': 'Italian',
        'diet_type': 'vegetarian',
        'ingredients': ['arborio rice', 'mushrooms', 'onion', 'white wine', 'vegetable broth', 'parmesan cheese', 'butter'],
        'image': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        'instructions': 'Sauté the onions and mushrooms in butter. Add the rice and toast for 2 minutes. Add the white wine and cook until absorbed. Gradually add hot vegetable broth, stirring constantly, until the rice is creamy and cooked. Stir in parmesan cheese.',
        'prep_time': 10,
        'cook_time': 30,
        'servings': 4,
        'calories': 380,
        'protein': 10,
        'carbs': 60,
        'fat': 15,
        'complexity': 'complex',
        'spice_level': 'mild'
    }
]
