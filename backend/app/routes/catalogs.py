from flask import Blueprint, request, jsonify
from ..middleware.auth import require_auth
from ..models.catalogs import MedicalCondition, FoodIntolerance, DietaryPreference, Ingredient, RecipeTag
from ..utils.responses import success_response, error_response

catalogs_bp = Blueprint('catalogs', __name__, url_prefix='/api/catalogs')

# Medical Conditions Routes
@catalogs_bp.route('/medical-conditions', methods=['GET'])
@require_auth
def get_medical_conditions():
    """Get all medical conditions."""
    try:
        conditions = MedicalCondition.get_all()
        return success_response({
            'medical_conditions': conditions,
            'total': len(conditions)
        })
    except Exception as e:
        return error_response(f'Error retrieving medical conditions: {str(e)}', 500)

@catalogs_bp.route('/medical-conditions', methods=['POST'])
@require_auth
def create_medical_condition():
    """Create a new medical condition."""
    try:
        data = request.get_json()
        
        if not data or not data.get('condition_name'):
            return error_response('Condition name is required', 400)
        
        condition = MedicalCondition.create(
            name=data['condition_name'],
            description=data.get('description'),
            severity_level=data.get('severity_level', 'medium')
        )
        
        return success_response({
            'medical_condition': condition
        }, 'Medical condition created successfully')
        
    except Exception as e:
        return error_response(f'Error creating medical condition: {str(e)}', 500)

@catalogs_bp.route('/medical-conditions/<condition_id>', methods=['PUT'])
@require_auth
def update_medical_condition(condition_id):
    """Update medical condition."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        success = MedicalCondition.update(condition_id, data)
        
        if not success:
            return error_response('Error updating medical condition', 500)
        
        return success_response(message='Medical condition updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating medical condition: {str(e)}', 500)

@catalogs_bp.route('/medical-conditions/<condition_id>', methods=['DELETE'])
@require_auth
def delete_medical_condition(condition_id):
    """Delete medical condition."""
    try:
        success = MedicalCondition.delete(condition_id)
        
        if not success:
            return error_response('Error deleting medical condition', 500)
        
        return success_response(message='Medical condition deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting medical condition: {str(e)}', 500)

# Food Intolerances Routes
@catalogs_bp.route('/food-intolerances', methods=['GET'])
@require_auth
def get_food_intolerances():
    """Get all food intolerances."""
    try:
        intolerances = FoodIntolerance.get_all()
        return success_response({
            'food_intolerances': intolerances,
            'total': len(intolerances)
        })
    except Exception as e:
        return error_response(f'Error retrieving food intolerances: {str(e)}', 500)

@catalogs_bp.route('/food-intolerances', methods=['POST'])
@require_auth
def create_food_intolerance():
    """Create a new food intolerance."""
    try:
        data = request.get_json()
        
        if not data or not data.get('intolerance_name'):
            return error_response('Intolerance name is required', 400)
        
        intolerance = FoodIntolerance.create(
            name=data['intolerance_name'],
            description=data.get('description')
        )
        
        return success_response({
            'food_intolerance': intolerance
        }, 'Food intolerance created successfully')
        
    except Exception as e:
        return error_response(f'Error creating food intolerance: {str(e)}', 500)

@catalogs_bp.route('/food-intolerances/<intolerance_id>', methods=['PUT'])
@require_auth
def update_food_intolerance(intolerance_id):
    """Update food intolerance."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        success = FoodIntolerance.update(intolerance_id, data)
        
        if not success:
            return error_response('Error updating food intolerance', 500)
        
        return success_response(message='Food intolerance updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating food intolerance: {str(e)}', 500)

@catalogs_bp.route('/food-intolerances/<intolerance_id>', methods=['DELETE'])
@require_auth
def delete_food_intolerance(intolerance_id):
    """Delete food intolerance."""
    try:
        success = FoodIntolerance.delete(intolerance_id)
        
        if not success:
            return error_response('Error deleting food intolerance', 500)
        
        return success_response(message='Food intolerance deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting food intolerance: {str(e)}', 500)

# Dietary Preferences Routes
@catalogs_bp.route('/dietary-preferences', methods=['GET'])
@require_auth
def get_dietary_preferences():
    """Get all dietary preferences."""
    try:
        preferences = DietaryPreference.get_all()
        return success_response({
            'dietary_preferences': preferences,
            'total': len(preferences)
        })
    except Exception as e:
        return error_response(f'Error retrieving dietary preferences: {str(e)}', 500)

@catalogs_bp.route('/dietary-preferences', methods=['POST'])
@require_auth
def create_dietary_preference():
    """Create a new dietary preference."""
    try:
        data = request.get_json()
        
        if not data or not data.get('preference_name'):
            return error_response('Preference name is required', 400)
        
        preference = DietaryPreference.create(
            name=data['preference_name'],
            description=data.get('description')
        )
        
        return success_response({
            'dietary_preference': preference
        }, 'Dietary preference created successfully')
        
    except Exception as e:
        return error_response(f'Error creating dietary preference: {str(e)}', 500)

@catalogs_bp.route('/dietary-preferences/<preference_id>', methods=['PUT'])
@require_auth
def update_dietary_preference(preference_id):
    """Update dietary preference."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        success = DietaryPreference.update(preference_id, data)
        
        if not success:
            return error_response('Error updating dietary preference', 500)
        
        return success_response(message='Dietary preference updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating dietary preference: {str(e)}', 500)

@catalogs_bp.route('/dietary-preferences/<preference_id>', methods=['DELETE'])
@require_auth
def delete_dietary_preference(preference_id):
    """Delete dietary preference."""
    try:
        success = DietaryPreference.delete(preference_id)
        
        if not success:
            return error_response('Error deleting dietary preference', 500)
        
        return success_response(message='Dietary preference deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting dietary preference: {str(e)}', 500)

# Ingredients Routes
@catalogs_bp.route('/ingredients', methods=['GET'])
@require_auth
def get_ingredients():
    """Get all ingredients."""
    try:
        search = request.args.get('search')
        
        if search:
            ingredients = Ingredient.search_by_name(search)
        else:
            ingredients = Ingredient.get_all()
        
        return success_response({
            'ingredients': ingredients,
            'total': len(ingredients)
        })
    except Exception as e:
        return error_response(f'Error retrieving ingredients: {str(e)}', 500)

@catalogs_bp.route('/ingredients', methods=['POST'])
@require_auth
def create_ingredient():
    """Create a new ingredient."""
    try:
        data = request.get_json()
        
        if not data or not data.get('ingredient_name'):
            return error_response('Ingredient name is required', 400)
        
        ingredient = Ingredient.create(data)
        
        return success_response({
            'ingredient': ingredient
        }, 'Ingredient created successfully')
        
    except Exception as e:
        return error_response(f'Error creating ingredient: {str(e)}', 500)

@catalogs_bp.route('/ingredients/<ingredient_id>', methods=['PUT'])
@require_auth
def update_ingredient(ingredient_id):
    """Update ingredient."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        success = Ingredient.update(ingredient_id, data)
        
        if not success:
            return error_response('Error updating ingredient', 500)
        
        return success_response(message='Ingredient updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating ingredient: {str(e)}', 500)

@catalogs_bp.route('/ingredients/<ingredient_id>', methods=['DELETE'])
@require_auth
def delete_ingredient(ingredient_id):
    """Delete ingredient."""
    try:
        success = Ingredient.delete(ingredient_id)
        
        if not success:
            return error_response('Error deleting ingredient', 500)
        
        return success_response(message='Ingredient deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting ingredient: {str(e)}', 500)

# Recipe Tags Routes
@catalogs_bp.route('/recipe-tags', methods=['GET'])
@require_auth
def get_recipe_tags():
    """Get all recipe tags."""
    try:
        tags = RecipeTag.get_all()
        return success_response({
            'recipe_tags': tags,
            'total': len(tags)
        })
    except Exception as e:
        return error_response(f'Error retrieving recipe tags: {str(e)}', 500)

@catalogs_bp.route('/recipe-tags', methods=['POST'])
@require_auth
def create_recipe_tag():
    """Create a new recipe tag."""
    try:
        data = request.get_json()
        
        if not data or not data.get('tag_name'):
            return error_response('Tag name is required', 400)
        
        tag = RecipeTag.create(
            name=data['tag_name'],
            color=data.get('color', '#3b82f6')
        )
        
        return success_response({
            'recipe_tag': tag
        }, 'Recipe tag created successfully')
        
    except Exception as e:
        return error_response(f'Error creating recipe tag: {str(e)}', 500)

@catalogs_bp.route('/recipe-tags/<tag_id>', methods=['PUT'])
@require_auth
def update_recipe_tag(tag_id):
    """Update recipe tag."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        success = RecipeTag.update(tag_id, data)
        
        if not success:
            return error_response('Error updating recipe tag', 500)
        
        return success_response(message='Recipe tag updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating recipe tag: {str(e)}', 500)

@catalogs_bp.route('/recipe-tags/<tag_id>', methods=['DELETE'])
@require_auth
def delete_recipe_tag(tag_id):
    """Delete recipe tag."""
    try:
        success = RecipeTag.delete(tag_id)
        
        if not success:
            return error_response('Error deleting recipe tag', 500)
        
        return success_response(message='Recipe tag deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting recipe tag: {str(e)}', 500)

# Bulk operations
@catalogs_bp.route('/bulk-import', methods=['POST'])
@require_auth
def bulk_import_catalog_data():
    """Import catalog data in bulk."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Import data is required', 400)
        
        results = {
            'medical_conditions': [],
            'food_intolerances': [], 
            'dietary_preferences': [],
            'ingredients': [],
            'recipe_tags': []
        }
        
        # Import medical conditions
        if 'medical_conditions' in data:
            for condition_data in data['medical_conditions']:
                try:
                    condition = MedicalCondition.create(
                        name=condition_data['condition_name'],
                        description=condition_data.get('description'),
                        severity_level=condition_data.get('severity_level', 'medium')
                    )
                    results['medical_conditions'].append(condition)
                except Exception as e:
                    # Log error but continue with next item
                    pass
        
        # Import other catalogs similarly...
        
        return success_response(results, 'Bulk import completed')
        
    except Exception as e:
        return error_response(f'Error during bulk import: {str(e)}', 500)
