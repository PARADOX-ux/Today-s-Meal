from app import db
from datetime import datetime


class Recipe(db.Model):
    """Recipe model for storing Indian vegetarian recipes"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    time = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Breakfast, Lunch, Dinner, Snacks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ingredients = db.relationship('RecipeIngredient', back_populates='recipe', cascade='all, delete-orphan')
    steps = db.relationship('RecipeStep', back_populates='recipe', cascade='all, delete-orphan')
    tags = db.relationship('RecipeTag', back_populates='recipe', cascade='all, delete-orphan')
    favorites = db.relationship('UserFavorite', back_populates='recipe', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert recipe to dictionary format"""
        return {
            'id': self.id,
            'name': self.name,
            'time': self.time,
            'type': self.type,
            'ingredients': [ing.ingredient.name for ing in self.ingredients],
            'steps': [step.description for step in sorted(self.steps, key=lambda x: x.step_number)],
            'tags': [tag.tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Ingredient(db.Model):
    """Ingredient model for storing all available ingredients"""
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipe_ingredients = db.relationship('RecipeIngredient', back_populates='ingredient')


class RecipeIngredient(db.Model):
    """Junction table for recipe-ingredient relationships"""
    __tablename__ = 'recipe_ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.String(50))  # Optional: e.g., "2 cups", "1 tsp"
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe_ingredients')
    
    # Ensure unique recipe-ingredient combinations
    __table_args__ = (db.UniqueConstraint('recipe_id', 'ingredient_id'),)


class RecipeStep(db.Model):
    """Model for storing recipe preparation steps"""
    __tablename__ = 'recipe_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='steps')
    
    # Ensure unique step numbers per recipe
    __table_args__ = (db.UniqueConstraint('recipe_id', 'step_number'),)


class Tag(db.Model):
    """Tag model for dietary preferences and recipe categories"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipe_tags = db.relationship('RecipeTag', back_populates='tag')


class RecipeTag(db.Model):
    """Junction table for recipe-tag relationships"""
    __tablename__ = 'recipe_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='tags')
    tag = db.relationship('Tag', back_populates='recipe_tags')
    
    # Ensure unique recipe-tag combinations
    __table_args__ = (db.UniqueConstraint('recipe_id', 'tag_id'),)


class User(db.Model):
    """User model for storing user sessions and preferences"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    favorites = db.relationship('UserFavorite', back_populates='user', cascade='all, delete-orphan')


class UserFavorite(db.Model):
    """Model for storing user's favorite recipes"""
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='favorites')
    recipe = db.relationship('Recipe', back_populates='favorites')
    
    # Ensure unique user-recipe favorite combinations
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id'),)