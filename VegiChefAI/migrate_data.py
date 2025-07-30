"""
Data migration script to populate the database with recipes from JSON file
"""
import json
from app import app, db
from models import Recipe, Ingredient, RecipeIngredient, RecipeStep, Tag, RecipeTag


def migrate_json_to_database():
    """Migrate recipes from JSON file to PostgreSQL database"""
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        try:
            # Load recipes from JSON file
            with open('recipes.json', 'r', encoding='utf-8') as f:
                recipes_data = json.load(f)
            
            print(f"Migrating {len(recipes_data)} recipes to database...")
            
            for recipe_data in recipes_data:
                # Create recipe
                recipe = Recipe(
                    name=recipe_data['name'],
                    time=recipe_data['time'],
                    type=recipe_data['type']
                )
                db.session.add(recipe)
                db.session.flush()  # Get the recipe ID
                
                # Add ingredients
                for idx, ingredient_name in enumerate(recipe_data.get('ingredients', [])):
                    # Get or create ingredient
                    ingredient = Ingredient.query.filter_by(name=ingredient_name.lower().strip()).first()
                    if not ingredient:
                        ingredient = Ingredient(name=ingredient_name.lower().strip())
                        db.session.add(ingredient)
                        db.session.flush()
                    
                    # Create recipe-ingredient relationship
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id
                    )
                    db.session.add(recipe_ingredient)
                
                # Add steps
                for idx, step_description in enumerate(recipe_data.get('steps', [])):
                    step = RecipeStep(
                        recipe_id=recipe.id,
                        step_number=idx + 1,
                        description=step_description
                    )
                    db.session.add(step)
                
                # Add tags
                for tag_name in recipe_data.get('tags', []):
                    # Get or create tag
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        db.session.flush()
                    
                    # Create recipe-tag relationship
                    recipe_tag = RecipeTag(
                        recipe_id=recipe.id,
                        tag_id=tag.id
                    )
                    db.session.add(recipe_tag)
                
                print(f"Migrated: {recipe_data['name']}")
            
            # Commit all changes
            db.session.commit()
            
            # Verify migration
            recipe_count = Recipe.query.count()
            ingredient_count = Ingredient.query.count()
            tag_count = Tag.query.count()
            
            print(f"\nMigration completed successfully!")
            print(f"- {recipe_count} recipes")
            print(f"- {ingredient_count} unique ingredients")
            print(f"- {tag_count} unique tags")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            raise


if __name__ == '__main__':
    migrate_json_to_database()