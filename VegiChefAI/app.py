import os
import json
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from openai_helper import get_cooking_instructions

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Create tables and import models after db initialization
with app.app_context():
    import models  # noqa: F401
    db.create_all()

# Database-based recipe loading
def load_recipes():
    """Load recipes from the database"""
    try:
        from models import Recipe
        recipes = Recipe.query.all()
        return [recipe.to_dict() for recipe in recipes]
    except Exception as e:
        logging.error(f"Error loading recipes from database: {e}")
        return []

def calculate_match_percentage(user_ingredients, recipe_ingredients):
    """Calculate what percentage of recipe ingredients the user has"""
    if not recipe_ingredients:
        return 0
    
    user_ingredients_lower = [ing.lower().strip() for ing in user_ingredients]
    recipe_ingredients_lower = [ing.lower().strip() for ing in recipe_ingredients]
    
    matches = sum(1 for recipe_ing in recipe_ingredients_lower 
                  if any(user_ing in recipe_ing or recipe_ing in user_ing 
                        for user_ing in user_ingredients_lower))
    
    return round((matches / len(recipe_ingredients_lower)) * 100)

def get_missing_ingredients(user_ingredients, recipe_ingredients):
    """Get list of missing ingredients"""
    user_ingredients_lower = [ing.lower().strip() for ing in user_ingredients]
    recipe_ingredients_lower = [ing.lower().strip() for ing in recipe_ingredients]
    
    missing = []
    for recipe_ing in recipe_ingredients_lower:
        if not any(user_ing in recipe_ing or recipe_ing in user_ing 
                  for user_ing in user_ingredients_lower):
            # Find the original case ingredient
            original_ing = next(ing for ing in recipe_ingredients 
                              if ing.lower().strip() == recipe_ing)
            missing.append(original_ing)
    
    return missing

def filter_recipes(recipes, filters, meal_type):
    """Filter recipes based on dietary preferences and meal type"""
    filtered = []
    
    for recipe in recipes:
        # Check meal type filter
        if meal_type and meal_type != "All" and recipe.get("type", "").lower() != meal_type.lower():
            continue
            
        # Check dietary filters
        recipe_tags = [tag.lower() for tag in recipe.get("tags", [])]
        
        # Skip if filters don't match
        if filters.get("no_onion_garlic") and "no onion/garlic" not in recipe_tags:
            continue
        if filters.get("jain") and "jain" not in recipe_tags:
            continue
        if filters.get("satvik") and "satvik" not in recipe_tags:
            continue
        if filters.get("quick") and "quick" not in recipe_tags:
            continue
        if filters.get("healthy") and "healthy" not in recipe_tags:
            continue
            
        filtered.append(recipe)
    
    return filtered

@app.route('/')
def index():
    try:
        from models import Ingredient
        ingredients = Ingredient.query.all()
        sorted_ingredients = sorted([ing.name for ing in ingredients])
        return render_template('index.html', ingredients=sorted_ingredients)
    except Exception as e:
        logging.error(f"Error loading ingredients: {e}")
        return render_template('index.html', ingredients=[])

@app.route('/search_recipes', methods=['POST'])
def search_recipes():
    try:
        data = request.get_json()
        user_ingredients = data.get('ingredients', [])
        filters = data.get('filters', {})
        meal_type = data.get('meal_type', 'All')
        
        if not user_ingredients:
            return jsonify({'recipes': [], 'message': 'Please select some ingredients first!'})
        
        recipes = load_recipes()
        
        # Apply filters
        filtered_recipes = filter_recipes(recipes, filters, meal_type)
        
        # Calculate matches and sort
        recipe_matches = []
        for recipe in filtered_recipes:
            match_percentage = calculate_match_percentage(user_ingredients, recipe.get("ingredients", []))
            
            # Only include recipes with at least 30% match
            if match_percentage >= 30:
                missing_ingredients = get_missing_ingredients(user_ingredients, recipe.get("ingredients", []))
                
                recipe_matches.append({
                    'name': recipe.get('name', ''),
                    'ingredients': recipe.get('ingredients', []),
                    'time': recipe.get('time', ''),
                    'steps': recipe.get('steps', []),
                    'type': recipe.get('type', ''),
                    'tags': recipe.get('tags', []),
                    'match_percentage': match_percentage,
                    'missing_ingredients': missing_ingredients
                })
        
        # Sort by match percentage (highest first) and limit to top 10
        recipe_matches.sort(key=lambda x: x['match_percentage'], reverse=True)
        top_recipes = recipe_matches[:10]
        
        if not top_recipes:
            return jsonify({'recipes': [], 'message': 'No recipes found with your ingredients. Try adding more ingredients or adjusting filters!'})
        
        return jsonify({'recipes': top_recipes, 'message': f'Found {len(top_recipes)} recipes!'})
        
    except Exception as e:
        logging.error(f"Error in search_recipes: {str(e)}")
        return jsonify({'error': 'An error occurred while searching recipes'}), 500

@app.route('/get_ai_instructions', methods=['POST'])
def get_ai_instructions():
    try:
        data = request.get_json()
        recipe_name = data.get('recipe_name', '')
        user_ingredients = data.get('user_ingredients', [])
        recipe_ingredients = data.get('recipe_ingredients', [])
        
        if not recipe_name:
            return jsonify({'error': 'Recipe name is required'}), 400
        
        # Get AI-powered cooking instructions
        ai_instructions = get_cooking_instructions(recipe_name, user_ingredients, recipe_ingredients)
        
        return jsonify({'instructions': ai_instructions})
        
    except Exception as e:
        logging.error(f"Error in get_ai_instructions: {str(e)}")
        return jsonify({'error': 'Failed to get AI cooking instructions. Please try again.'}), 500


def get_or_create_user():
    """Get or create user based on session"""
    from models import User
    
    if 'user_id' not in session:
        # Create new user
        import uuid
        session_id = str(uuid.uuid4())
        user = User(session_id=session_id)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return user
    else:
        user = User.query.get(session['user_id'])
        if not user:
            # Session user doesn't exist, create new one
            import uuid
            session_id = str(uuid.uuid4())
            user = User(session_id=session_id)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
        return user


@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    """Toggle recipe favorite status for current user"""
    try:
        from models import Recipe, UserFavorite
        
        data = request.get_json()
        recipe_name = data.get('recipe_name', '')
        
        if not recipe_name:
            return jsonify({'error': 'Recipe name is required'}), 400
        
        # Get recipe
        recipe = Recipe.query.filter_by(name=recipe_name).first()
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # Get or create user
        user = get_or_create_user()
        
        # Check if already favorited
        favorite = UserFavorite.query.filter_by(
            user_id=user.id, 
            recipe_id=recipe.id
        ).first()
        
        if favorite:
            # Remove from favorites
            db.session.delete(favorite)
            is_favorite = False
        else:
            # Add to favorites
            favorite = UserFavorite(user_id=user.id, recipe_id=recipe.id)
            db.session.add(favorite)
            is_favorite = True
        
        db.session.commit()
        
        return jsonify({'is_favorite': is_favorite})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in toggle_favorite: {str(e)}")
        return jsonify({'error': 'Failed to toggle favorite'}), 500


@app.route('/get_favorites', methods=['GET'])
def get_favorites():
    """Get user's favorite recipes"""
    try:
        from models import Recipe, UserFavorite
        
        user = get_or_create_user()
        
        # Get user's favorite recipes
        favorites = db.session.query(Recipe).join(UserFavorite).filter(
            UserFavorite.user_id == user.id
        ).all()
        
        favorite_recipes = [recipe.to_dict() for recipe in favorites]
        
        return jsonify({'recipes': favorite_recipes})
        
    except Exception as e:
        logging.error(f"Error in get_favorites: {str(e)}")
        return jsonify({'error': 'Failed to get favorites'}), 500


@app.route('/check_favorites', methods=['POST'])
def check_favorites():
    """Check which recipes are favorited by current user"""
    try:
        from models import Recipe, UserFavorite
        
        data = request.get_json()
        recipe_names = data.get('recipe_names', [])
        
        user = get_or_create_user()
        
        # Get favorited recipe names
        favorited_recipes = db.session.query(Recipe.name).join(UserFavorite).filter(
            UserFavorite.user_id == user.id,
            Recipe.name.in_(recipe_names)
        ).all()
        
        favorited_names = [recipe.name for recipe in favorited_recipes]
        
        return jsonify({'favorited_recipes': favorited_names})
        
    except Exception as e:
        logging.error(f"Error in check_favorites: {str(e)}")
        return jsonify({'error': 'Failed to check favorites'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
