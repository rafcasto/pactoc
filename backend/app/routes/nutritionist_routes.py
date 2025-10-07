"""
Nutritionist API Routes - Handles nutritionist-specific operations.
"""
from flask import Blueprint, request, jsonify
from app.services.nutritionist_service import NutritionistService
from app.services.meal_plan_versioning_service import MealPlanVersioningService
from app.utils.auth_utils import require_auth, get_current_user_uid

nutritionist_bp = Blueprint('nutritionist', __name__, url_prefix='/api/nutritionist')

@nutritionist_bp.route('/profile', methods=['POST'])
@require_auth
def create_or_update_profile():
    """Create or update nutritionist profile."""
    try:
        firebase_uid = get_current_user_uid()
        profile_data = request.get_json()
        
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'Profile data is required'
            }), 400
        
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data=profile_data
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': {
                'nutritionist': nutritionist.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get nutritionist profile."""
    try:
        firebase_uid = get_current_user_uid()
        
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}  # Just get existing
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        if not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'nutritionist': nutritionist.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get nutritionist dashboard data."""
    try:
        firebase_uid = get_current_user_uid()
        
        # Get nutritionist first
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Get dashboard data
        success, dashboard_data, error = NutritionistService.get_dashboard_data(nutritionist.id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/patients/<int:patient_id>/meal-plans', methods=['GET'])
@require_auth
def get_patient_meal_plan_history(patient_id):
    """Get all meal plan versions for a patient (nutritionist view)."""
    try:
        firebase_uid = get_current_user_uid()
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Get meal plan history
        success, meal_plans, error = NutritionistService.get_patient_meal_plan_history(
            nutritionist_id=nutritionist.id,
            patient_id=patient_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'meal_plans': meal_plans,
                'total_versions': len(meal_plans)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/patients/<int:patient_id>/meal-plans', methods=['POST'])
@require_auth
def create_meal_plan_version(patient_id):
    """Create new meal plan version for patient."""
    try:
        firebase_uid = get_current_user_uid()
        request_data = request.get_json()
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Create meal plan version
        success, meal_plan, error = NutritionistService.create_meal_plan_version(
            nutritionist_id=nutritionist.id,
            patient_id=patient_id,
            base_plan_id=request_data.get('base_plan_id'),
            plan_data=request_data.get('plan_data', {})
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Meal plan version created successfully',
            'data': {
                'meal_plan': meal_plan.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/meal-plans/<int:plan_id>/approve', methods=['POST'])
@require_auth
def approve_meal_plan(plan_id):
    """Approve a meal plan version."""
    try:
        firebase_uid = get_current_user_uid()
        request_data = request.get_json() or {}
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Approve meal plan
        success, meal_plan, error = MealPlanVersioningService.approve_meal_plan_version(
            plan_id=plan_id,
            nutritionist_id=nutritionist.id,
            approval_notes=request_data.get('approval_notes')
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Meal plan approved successfully',
            'data': {
                'meal_plan': meal_plan.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/meal-plans/<int:plan_id>/versions', methods=['POST'])
@require_auth
def create_version_from_existing(plan_id):
    """Create a new version from an existing meal plan."""
    try:
        firebase_uid = get_current_user_uid()
        request_data = request.get_json() or {}
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Create new version
        success, new_plan, error = MealPlanVersioningService.create_new_version_from_existing(
            base_plan_id=plan_id,
            nutritionist_id=nutritionist.id,
            updates=request_data.get('updates', {})
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'New meal plan version created successfully',
            'data': {
                'meal_plan': new_plan.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/meal-plans/compare', methods=['POST'])
@require_auth
def compare_meal_plan_versions():
    """Compare two meal plan versions."""
    try:
        firebase_uid = get_current_user_uid()
        request_data = request.get_json()
        
        if not request_data or 'plan_id_1' not in request_data or 'plan_id_2' not in request_data:
            return jsonify({
                'success': False,
                'message': 'Both plan_id_1 and plan_id_2 are required'
            }), 400
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Compare versions
        success, comparison, error = MealPlanVersioningService.get_version_comparison(
            plan_id_1=request_data['plan_id_1'],
            plan_id_2=request_data['plan_id_2'],
            nutritionist_id=nutritionist.id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': comparison
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/patients/<int:patient_id>/meal-plans/stats', methods=['GET'])
@require_auth
def get_patient_meal_plan_stats(patient_id):
    """Get meal plan version statistics for a patient."""
    try:
        firebase_uid = get_current_user_uid()
        
        # Get nutritionist
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data={}
        )
        
        if not success or not nutritionist:
            return jsonify({
                'success': False,
                'message': 'Nutritionist not found'
            }), 404
        
        # Get statistics
        success, stats, error = MealPlanVersioningService.get_version_statistics(
            patient_id=patient_id,
            nutritionist_id=nutritionist.id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@nutritionist_bp.route('/migrate-data', methods=['POST'])
@require_auth
def migrate_existing_data():
    """Migrate existing data to link with nutritionist entity."""
    try:
        firebase_uid = get_current_user_uid()
        
        # Get or create nutritionist profile first
        profile_data = request.get_json() or {}
        success, nutritionist, error = NutritionistService.create_or_get_nutritionist(
            firebase_uid=firebase_uid,
            profile_data=profile_data
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': error
            }), 400
        
        # Migrate data
        success, message = NutritionistService.migrate_existing_data(firebase_uid)
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'nutritionist': nutritionist.to_dict(include_relations=True)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
