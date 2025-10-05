from flask import Blueprint, request, jsonify
from ..middleware.auth import require_auth
from ..models.recipe import Recipe
from ..utils.responses import success_response, error_response

recipes_bp = Blueprint('recipes', __name__, url_prefix='/api/recipes')

@recipes_bp.route('/', methods=['GET'])
@require_auth
def list_recipes():
    """Get all recipes with optional filters."""
    try:
        # Get query parameters
        meal_type = request.args.get('meal_type')  # breakfast, lunch, dinner, snack
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        search = request.args.get('search')  # Search by name
        created_by = request.args.get('created_by')  # Filter by creator
        
        # Build filters
        filters = {'is_active': is_active}
        if meal_type:
            filters['meal_type'] = meal_type
        if created_by:
            filters['created_by_uid'] = created_by
        
        recipes = Recipe.get_all(filters)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            recipes = [
                r for r in recipes 
                if search_lower in r.get('recipe_name', '').lower()
            ]
        
        return success_response({
            'recipes': recipes,
            'total': len(recipes)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving recipes: {str(e)}', 500)

@recipes_bp.route('/', methods=['POST'])
@require_auth
def create_recipe():
    """Create a new recipe."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Recipe data is required', 400)
        
        # Validate required fields
        required_fields = ['recipe_name', 'meal_type']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field} is required', 400)
        
        # Validate meal_type
        if data['meal_type'] not in ['breakfast', 'lunch', 'dinner', 'snack']:
            return error_response('Invalid meal_type', 400)
        
        # Add creator info
        data['created_by_uid'] = request.user.get('uid')
        
        # Extract ingredients from data
        ingredients = data.pop('ingredients', [])
        
        # Calculate nutrition if ingredients provided
        if ingredients:
            nutrition = Recipe.calculate_nutrition(ingredients)
            data.update(nutrition)
        
        # Create recipe
        recipe = Recipe.create(data)
        
        # Add ingredients as subcollection
        if ingredients:
            Recipe.add_ingredients(recipe['id'], ingredients)
        
        # Get complete recipe with ingredients
        complete_recipe = Recipe.get_by_id(recipe['id'])
        
        return success_response({
            'recipe': complete_recipe
        }, 'Recipe created successfully')
        
    except Exception as e:
        return error_response(f'Error creating recipe: {str(e)}', 500)

@recipes_bp.route('/<recipe_id>', methods=['GET'])
@require_auth
def get_recipe(recipe_id):
    """Get recipe details with ingredients."""
    try:
        recipe = Recipe.get_by_id(recipe_id)
        
        if not recipe:
            return error_response('Recipe not found', 404)
        
        return success_response({'recipe': recipe})
        
    except Exception as e:
        return error_response(f'Error retrieving recipe: {str(e)}', 500)

@recipes_bp.route('/<recipe_id>', methods=['PUT'])
@require_auth
def update_recipe(recipe_id):
    """Update recipe."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        # Check if recipe exists
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            return error_response('Recipe not found', 404)
        
        # Extract ingredients from data
        ingredients = data.pop('ingredients', None)
        
        # Calculate nutrition if ingredients provided
        if ingredients:
            nutrition = Recipe.calculate_nutrition(ingredients)
            data.update(nutrition)
        
        # Update recipe
        success = Recipe.update(recipe_id, data)
        
        if not success:
            return error_response('Error updating recipe', 500)
        
        # Update ingredients if provided
        if ingredients is not None:
            Recipe.add_ingredients(recipe_id, ingredients)
        
        # Get updated recipe
        updated_recipe = Recipe.get_by_id(recipe_id)
        
        return success_response({
            'recipe': updated_recipe
        }, 'Recipe updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating recipe: {str(e)}', 500)

@recipes_bp.route('/<recipe_id>', methods=['DELETE'])
@require_auth
def delete_recipe(recipe_id):
    """Soft delete recipe."""
    try:
        # Check if recipe exists
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            return error_response('Recipe not found', 404)
        
        # Soft delete
        success = Recipe.delete(recipe_id)
        
        if not success:
            return error_response('Error deleting recipe', 500)
        
        return success_response(message='Recipe deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting recipe: {str(e)}', 500)

@recipes_bp.route('/compatible/<patient_id>', methods=['GET'])
@require_auth
def get_compatible_recipes(patient_id):
    """Get recipes compatible with patient's restrictions."""
    try:
        compatible_recipes = Recipe.get_compatible_for_patient(patient_id)
        
        # Group by meal type
        by_meal_type = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }
        
        for recipe in compatible_recipes:
            meal_type = recipe.get('meal_type', 'lunch')
            if meal_type in by_meal_type:
                by_meal_type[meal_type].append(recipe)
        
        return success_response({
            'compatible_recipes': compatible_recipes,
            'by_meal_type': by_meal_type,
            'total': len(compatible_recipes)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving compatible recipes: {str(e)}', 500)

@recipes_bp.route('/<recipe_id>/duplicate', methods=['POST'])
@require_auth
def duplicate_recipe(recipe_id):
    """Duplicate an existing recipe."""
    try:
        # Get original recipe
        original_recipe = Recipe.get_by_id(recipe_id)
        if not original_recipe:
            return error_response('Original recipe not found', 404)
        
        # Create duplicate data
        duplicate_data = original_recipe.copy()
        duplicate_data.pop('id', None)  # Remove original ID
        duplicate_data.pop('created_at', None)  # Will be set automatically
        duplicate_data.pop('updated_at', None)
        duplicate_data['recipe_name'] = f"{duplicate_data['recipe_name']} (Copy)"
        duplicate_data['created_by_uid'] = request.user.get('uid')
        
        # Extract ingredients
        ingredients = duplicate_data.pop('ingredients', [])
        
        # Create duplicate recipe
        new_recipe = Recipe.create(duplicate_data)
        
        # Add ingredients
        if ingredients:
            Recipe.add_ingredients(new_recipe['id'], ingredients)
        
        # Get complete new recipe
        complete_recipe = Recipe.get_by_id(new_recipe['id'])
        
        return success_response({
            'recipe': complete_recipe
        }, 'Recipe duplicated successfully')
        
    except Exception as e:
        return error_response(f'Error duplicating recipe: {str(e)}', 500)

@recipes_bp.route('/batch', methods=['POST'])
@require_auth
def create_batch_recipes():
    """Create multiple recipes at once."""
    try:
        data = request.get_json()
        
        if not data or not data.get('recipes'):
            return error_response('Recipes data is required', 400)
        
        recipes_data = data['recipes']
        if not isinstance(recipes_data, list):
            return error_response('Recipes must be an array', 400)
        
        created_recipes = []
        errors = []
        
        for i, recipe_data in enumerate(recipes_data):
            try:
                # Add creator info
                recipe_data['created_by_uid'] = request.user.get('uid')
                
                # Extract ingredients
                ingredients = recipe_data.pop('ingredients', [])
                
                # Calculate nutrition
                if ingredients:
                    nutrition = Recipe.calculate_nutrition(ingredients)
                    recipe_data.update(nutrition)
                
                # Create recipe
                recipe = Recipe.create(recipe_data)
                
                # Add ingredients
                if ingredients:
                    Recipe.add_ingredients(recipe['id'], ingredients)
                
                created_recipes.append(recipe)
                
            except Exception as e:
                errors.append(f"Recipe {i + 1}: {str(e)}")
        
        return success_response({
            'created_recipes': created_recipes,
            'created_count': len(created_recipes),
            'errors': errors
        }, f'Created {len(created_recipes)} recipes successfully')
        
    except Exception as e:
        return error_response(f'Error creating batch recipes: {str(e)}', 500)
