from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import db, User, Preference

views = Blueprint('views', __name__)

# Sample meal data - in a real app, this would come from a database
MEALS = [
    {
        'id': 1,
        'name': 'Vegetable Stir Fry',
        'description': 'A quick and healthy stir fry with seasonal vegetables and tofu.',
        'cuisine': 'Asian',
        'diet_type': 'vegetarian',
        'ingredients': ['tofu', 'broccoli', 'bell peppers', 'carrots', 'soy sauce', 'ginger', 'garlic'],
        'image': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    },
    {
        'id': 2,
        'name': 'Grilled Chicken Salad',
        'description': 'Grilled chicken breast on a bed of fresh greens with a light vinaigrette.',
        'cuisine': 'American',
        'diet_type': 'omnivore',
        'ingredients': ['chicken breast', 'lettuce', 'tomatoes', 'cucumber', 'olive oil', 'vinegar', 'salt'],
        'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    },
    {
        'id': 3,
        'name': 'Spaghetti Bolognese',
        'description': 'Classic Italian pasta with rich meat sauce and parmesan cheese.',
        'cuisine': 'Italian',
        'diet_type': 'omnivore',
        'ingredients': ['ground beef', 'tomatoes', 'onion', 'garlic', 'spaghetti', 'parmesan cheese', 'olive oil'],
        'image': 'https://images.unsplash.com/photo-1563379926898-05f4575a45d8?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    },
    {
        'id': 4,
        'name': 'Vegan Buddha Bowl',
        'description': 'Nutritious bowl with quinoa, roasted vegetables, and tahini dressing.',
        'cuisine': 'International',
        'diet_type': 'vegan',
        'ingredients': ['quinoa', 'sweet potato', 'chickpeas', 'kale', 'avocado', 'tahini', 'lemon juice'],
        'image': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    },
    {
        'id': 5,
        'name': 'Beef Tacos',
        'description': 'Spicy beef tacos with fresh salsa and guacamole.',
        'cuisine': 'Mexican',
        'diet_type': 'omnivore',
        'ingredients': ['ground beef', 'taco shells', 'lettuce', 'tomatoes', 'cheese', 'avocado', 'sour cream'],
        'image': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    },
    {
        'id': 6,
        'name': 'Mushroom Risotto',
        'description': 'Creamy Italian rice dish with mushrooms and parmesan.',
        'cuisine': 'Italian',
        'diet_type': 'vegetarian',
        'ingredients': ['arborio rice', 'mushrooms', 'onion', 'white wine', 'vegetable broth', 'parmesan cheese', 'butter'],
        'image': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
    }
]

@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("home.html", user=current_user)
    else:
        return redirect(url_for('auth.login'))

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
        
        if user_pref:
            # Update existing preferences
            user_pref.diet_type = diet_type
            user_pref.allergies = allergies
            user_pref.favorite_cuisine = favorite_cuisine
            user_pref.disliked_ingredients = disliked_ingredients
        else:
            # Create new preferences
            user_pref = Preference(
                user_id=current_user.id,
                diet_type=diet_type,
                allergies=allergies,
                favorite_cuisine=favorite_cuisine,
                disliked_ingredients=disliked_ingredients
            )
            db.session.add(user_pref)
            
        db.session.commit()
        flash('Preferences saved successfully!', category='success')
        return redirect(url_for('views.recommendations'))
    
    return render_template("preferences.html", user=current_user, preferences=user_pref)

@views.route('/recommendations')
@login_required
def recommendations():
    user_pref = Preference.query.filter_by(user_id=current_user.id).first()
    
    if not user_pref:
        flash('Please set your meal preferences first!', category='error')
        return redirect(url_for('views.preferences'))
    
    # Filter meals based on user preferences
    recommended_meals = []
    
    # Convert comma-separated strings to lists
    allergies = [a.strip().lower() for a in user_pref.allergies.split(',')] if user_pref.allergies else []
    disliked = [d.strip().lower() for d in user_pref.disliked_ingredients.split(',')] if user_pref.disliked_ingredients else []
    
    for meal in MEALS:
        # Check if meal matches diet type
        if user_pref.diet_type and meal['diet_type'] != user_pref.diet_type:
            continue
            
        # Check for allergies and disliked ingredients
        has_allergen = False
        has_disliked = False
        
        for ingredient in meal['ingredients']:
            if any(allergen in ingredient.lower() for allergen in allergies):
                has_allergen = True
                break
            if any(disliked_item in ingredient.lower() for disliked_item in disliked):
                has_disliked = True
                break
                
        if has_allergen or has_disliked:
            continue
            
        # Prioritize favorite cuisine
        if user_pref.favorite_cuisine and meal['cuisine'].lower() == user_pref.favorite_cuisine.lower():
            # Add to the beginning of the list
            recommended_meals.insert(0, meal)
        else:
            recommended_meals.append(meal)
    
    return render_template("recommendations.html", user=current_user, meals=recommended_meals)