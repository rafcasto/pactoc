"""
Routes for catalog management (medical conditions, intolerances, preferences, ingredients, etc.).
"""
from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
from ..middleware.auth import require_auth
from ..utils.responses import success_response, error_response
from ..services.database_service import db
from ..models.sql_models import (
    MedicalCondition, FoodIntolerance, DietaryPreference, 
    Ingredient, RecipeTag
)

catalogs_bp = Blueprint('catalogs', __name__, url_prefix='/api/catalogs')

# Medical Conditions
@catalogs_bp.route('/medical-conditions', methods=['GET'])
def get_medical_conditions():
    """Get all medical conditions."""
    try:
        conditions = MedicalCondition.query.filter_by(is_active=True).order_by(MedicalCondition.condition_name).all()
        return success_response([condition.to_dict() for condition in conditions], "Medical conditions retrieved successfully")
    except Exception as e:
        return error_response(f"Error retrieving medical conditions: {str(e)}", 500)

@catalogs_bp.route('/medical-conditions', methods=['POST'])
@require_auth
def create_medical_condition():
    """Create a new medical condition."""
    try:
        data = request.get_json()
        
        if not data.get('condition_name'):
            return error_response("Missing required field: condition_name", 400)
        
        # Check if already exists
        existing = MedicalCondition.query.filter_by(condition_name=data['condition_name']).first()
        if existing:
            return error_response("Medical condition already exists", 400)
        
        condition = MedicalCondition(
            condition_name=data['condition_name'],
            description=data.get('description'),
            severity_level=data.get('severity_level', 'medium')
        )
        
        db.session.add(condition)
        db.session.commit()
        
        return success_response(condition.to_dict(), "Medical condition created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating medical condition: {str(e)}", 500)

@catalogs_bp.route('/medical-conditions/<int:condition_id>', methods=['PUT'])
@require_auth
def update_medical_condition(condition_id):
    """Update a medical condition."""
    try:
        condition = MedicalCondition.query.get_or_404(condition_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['condition_name', 'description', 'severity_level', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(condition, field, data[field])
        
        db.session.commit()
        return success_response(condition.to_dict(), "Medical condition updated successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error updating medical condition: {str(e)}", 500)

# Food Intolerances
@catalogs_bp.route('/food-intolerances', methods=['GET'])
def get_food_intolerances():
    """Get all food intolerances."""
    try:
        intolerances = FoodIntolerance.query.filter_by(is_active=True).order_by(FoodIntolerance.intolerance_name).all()
        return success_response([intolerance.to_dict() for intolerance in intolerances], "Food intolerances retrieved successfully")
    except Exception as e:
        return error_response(f"Error retrieving food intolerances: {str(e)}", 500)

@catalogs_bp.route('/food-intolerances', methods=['POST'])
@require_auth
def create_food_intolerance():
    """Create a new food intolerance."""
    try:
        data = request.get_json()
        
        if not data.get('intolerance_name'):
            return error_response("Missing required field: intolerance_name", 400)
        
        # Check if already exists
        existing = FoodIntolerance.query.filter_by(intolerance_name=data['intolerance_name']).first()
        if existing:
            return error_response("Food intolerance already exists", 400)
        
        intolerance = FoodIntolerance(
            intolerance_name=data['intolerance_name'],
            description=data.get('description')
        )
        
        db.session.add(intolerance)
        db.session.commit()
        
        return success_response(intolerance.to_dict(), "Food intolerance created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating food intolerance: {str(e)}", 500)

# Dietary Preferences
@catalogs_bp.route('/dietary-preferences', methods=['GET'])
def get_dietary_preferences():
    """Get all dietary preferences."""
    try:
        preferences = DietaryPreference.query.filter_by(is_active=True).order_by(DietaryPreference.preference_name).all()
        return success_response([preference.to_dict() for preference in preferences], "Dietary preferences retrieved successfully")
    except Exception as e:
        return error_response(f"Error retrieving dietary preferences: {str(e)}", 500)

@catalogs_bp.route('/dietary-preferences', methods=['POST'])
@require_auth
def create_dietary_preference():
    """Create a new dietary preference."""
    try:
        data = request.get_json()
        
        if not data.get('preference_name'):
            return error_response("Missing required field: preference_name", 400)
        
        # Check if already exists
        existing = DietaryPreference.query.filter_by(preference_name=data['preference_name']).first()
        if existing:
            return error_response("Dietary preference already exists", 400)
        
        preference = DietaryPreference(
            preference_name=data['preference_name'],
            description=data.get('description')
        )
        
        db.session.add(preference)
        db.session.commit()
        
        return success_response(preference.to_dict(), "Dietary preference created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating dietary preference: {str(e)}", 500)

# Ingredients
@catalogs_bp.route('/ingredients', methods=['GET'])
def get_ingredients():
    """Get all ingredients."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Ingredient.query.filter_by(is_active=True)
        
        if category:
            query = query.filter(Ingredient.category == category)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Ingredient.ingredient_name.ilike(search_filter))
        
        ingredients = query.order_by(Ingredient.ingredient_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return success_response({
            'ingredients': [ingredient.to_dict() for ingredient in ingredients.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': ingredients.total,
                'pages': ingredients.pages,
                'has_next': ingredients.has_next,
                'has_prev': ingredients.has_prev
            }
        }, "Ingredients retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving ingredients: {str(e)}", 500)

@catalogs_bp.route('/ingredients', methods=['POST'])
@require_auth
def create_ingredient():
    """Create a new ingredient."""
    try:
        data = request.get_json()
        
        if not data.get('ingredient_name'):
            return error_response("Missing required field: ingredient_name", 400)
        
        # Check if already exists
        existing = Ingredient.query.filter_by(ingredient_name=data['ingredient_name']).first()
        if existing:
            return error_response("Ingredient already exists", 400)
        
        ingredient = Ingredient(
            ingredient_name=data['ingredient_name'],
            category=data.get('category'),
            calories_per_100g=data.get('calories_per_100g'),
            protein_per_100g=data.get('protein_per_100g'),
            carbs_per_100g=data.get('carbs_per_100g'),
            fat_per_100g=data.get('fat_per_100g'),
            fiber_per_100g=data.get('fiber_per_100g')
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        return success_response(ingredient.to_dict(), "Ingredient created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating ingredient: {str(e)}", 500)

@catalogs_bp.route('/ingredients/<int:ingredient_id>', methods=['PUT'])
@require_auth
def update_ingredient(ingredient_id):
    """Update an ingredient."""
    try:
        ingredient = Ingredient.query.get_or_404(ingredient_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'ingredient_name', 'category', 'calories_per_100g', 
            'protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 
            'fiber_per_100g', 'is_active'
        ]
        for field in allowed_fields:
            if field in data:
                setattr(ingredient, field, data[field])
        
        db.session.commit()
        return success_response(ingredient.to_dict(), "Ingredient updated successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error updating ingredient: {str(e)}", 500)

# Recipe Tags
@catalogs_bp.route('/recipe-tags', methods=['GET'])
def get_recipe_tags():
    """Get all recipe tags."""
    try:
        tags = RecipeTag.query.filter_by(is_active=True).order_by(RecipeTag.tag_name).all()
        return success_response([tag.to_dict() for tag in tags], "Recipe tags retrieved successfully")
    except Exception as e:
        return error_response(f"Error retrieving recipe tags: {str(e)}", 500)

@catalogs_bp.route('/recipe-tags', methods=['POST'])
@require_auth
def create_recipe_tag():
    """Create a new recipe tag."""
    try:
        data = request.get_json()
        
        if not data.get('tag_name'):
            return error_response("Missing required field: tag_name", 400)
        
        # Check if already exists
        existing = RecipeTag.query.filter_by(tag_name=data['tag_name']).first()
        if existing:
            return error_response("Recipe tag already exists", 400)
        
        tag = RecipeTag(
            tag_name=data['tag_name'],
            color=data.get('color', '#3b82f6')
        )
        
        db.session.add(tag)
        db.session.commit()
        
        return success_response(tag.to_dict(), "Recipe tag created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating recipe tag: {str(e)}", 500)

# Bulk operations
@catalogs_bp.route('/bulk-seed', methods=['POST'])
@require_auth
def bulk_seed_catalogs():
    """Bulk seed catalog data."""
    try:
        # This endpoint can be used to populate initial data
        # Implementation would go here based on requirements
        return success_response({}, "Bulk seed operation completed successfully")
        
    except Exception as e:
        return error_response(f"Error in bulk seed operation: {str(e)}", 500)
