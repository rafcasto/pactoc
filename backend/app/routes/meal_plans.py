from flask import Blueprint, request, jsonify
from datetime import datetime, date
from ..middleware.auth import require_auth
from ..models.meal_plan import MealPlan
from ..services.meal_plan_service import MealPlanService
from ..utils.responses import success_response, error_response

meal_plans_bp = Blueprint('meal_plans', __name__, url_prefix='/api/meal-plans')

@meal_plans_bp.route('/generate', methods=['POST'])
@require_auth
def generate_meal_plan():
    """Generate a new meal plan for a patient."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Generation data is required', 400)
        
        # Validate required fields
        required_fields = ['patient_id', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field} is required', 400)
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        # Validate date range
        if start_date >= end_date:
            return error_response('End date must be after start date', 400)
        
        if (end_date - start_date).days > 30:
            return error_response('Date range cannot exceed 30 days', 400)
        
        patient_id = data['patient_id']
        generated_by_uid = request.user.get('uid')
        preferences = data.get('preferences', {})
        
        # Generate meal plan
        success, meal_plan, error_msg = MealPlanService.generate_meal_plan(
            patient_id, start_date, end_date, generated_by_uid, preferences
        )
        
        if not success:
            return error_response(error_msg, 400)
        
        return success_response({
            'meal_plan': meal_plan
        }, 'Meal plan generated successfully')
        
    except Exception as e:
        return error_response(f'Error generating meal plan: {str(e)}', 500)

@meal_plans_bp.route('/', methods=['GET'])
@require_auth
def list_meal_plans():
    """Get all meal plans with optional filters."""
    try:
        # Get query parameters
        patient_id = request.args.get('patient_id')
        status = request.args.get('status')  # draft, approved, sent
        generated_by = request.args.get('generated_by')
        
        # Build filters
        filters = {}
        if patient_id:
            filters['patient_id'] = patient_id
        if status:
            filters['status'] = status
        if generated_by:
            filters['generated_by_uid'] = generated_by
        
        meal_plans = MealPlan.get_all(filters)
        
        return success_response({
            'meal_plans': meal_plans,
            'total': len(meal_plans)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving meal plans: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>', methods=['GET'])
@require_auth
def get_meal_plan(plan_id):
    """Get meal plan details with meals."""
    try:
        meal_plan = MealPlan.get_by_id(plan_id)
        
        if not meal_plan:
            return error_response('Meal plan not found', 404)
        
        # Get calendar view
        calendar = MealPlan.get_weekly_calendar(plan_id)
        meal_plan['calendar'] = calendar
        
        return success_response({'meal_plan': meal_plan})
        
    except Exception as e:
        return error_response(f'Error retrieving meal plan: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>', methods=['PUT'])
@require_auth
def update_meal_plan(plan_id):
    """Update meal plan information."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        # Check if meal plan exists
        meal_plan = MealPlan.get_by_id(plan_id)
        if not meal_plan:
            return error_response('Meal plan not found', 404)
        
        # Extract meals from data if provided
        meals = data.pop('meals', None)
        
        # Update meal plan
        success = MealPlan.update(plan_id, data)
        
        if not success:
            return error_response('Error updating meal plan', 500)
        
        # Update meals if provided
        if meals is not None:
            MealPlan.add_meals(plan_id, meals)
        
        # Get updated meal plan
        updated_plan = MealPlan.get_by_id(plan_id)
        
        return success_response({
            'meal_plan': updated_plan
        }, 'Meal plan updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating meal plan: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>/approve', methods=['PUT'])
@require_auth
def approve_meal_plan(plan_id):
    """Approve meal plan and make it available to patient."""
    try:
        # Check if meal plan exists
        meal_plan = MealPlan.get_by_id(plan_id)
        if not meal_plan:
            return error_response('Meal plan not found', 404)
        
        # Check if already approved
        if meal_plan.get('status') == 'approved':
            return error_response('Meal plan is already approved', 400)
        
        approved_by_uid = request.user.get('uid')
        
        # Approve meal plan
        success, error_msg = MealPlanService.approve_meal_plan(plan_id, approved_by_uid)
        
        if not success:
            return error_response(error_msg, 500)
        
        return success_response(message='Meal plan approved successfully')
        
    except Exception as e:
        return error_response(f'Error approving meal plan: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>', methods=['DELETE'])
@require_auth
def delete_meal_plan(plan_id):
    """Delete meal plan."""
    try:
        # Check if meal plan exists
        meal_plan = MealPlan.get_by_id(plan_id)
        if not meal_plan:
            return error_response('Meal plan not found', 404)
        
        # Delete meal plan
        success = MealPlan.delete(plan_id)
        
        if not success:
            return error_response('Error deleting meal plan', 500)
        
        return success_response(message='Meal plan deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting meal plan: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>/meals/<meal_id>', methods=['PUT'])
@require_auth
def update_meal_in_plan(plan_id, meal_id):
    """Update a specific meal in the meal plan."""
    try:
        data = request.get_json()
        
        if not data or not data.get('recipe_id'):
            return error_response('Recipe ID is required', 400)
        
        new_recipe_id = data['recipe_id']
        
        # Update meal
        success, error_msg = MealPlanService.update_meal_in_plan(plan_id, meal_id, new_recipe_id)
        
        if not success:
            return error_response(error_msg, 400)
        
        return success_response(message='Meal updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating meal: {str(e)}', 500)

@meal_plans_bp.route('/<plan_id>/duplicate', methods=['POST'])
@require_auth
def duplicate_meal_plan(plan_id):
    """Duplicate an existing meal plan with new dates."""
    try:
        data = request.get_json()
        
        if not data or not data.get('start_date'):
            return error_response('Start date is required', 400)
        
        # Parse start date
        try:
            new_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        generated_by_uid = request.user.get('uid')
        
        # Duplicate meal plan
        success, new_plan, error_msg = MealPlanService.duplicate_meal_plan(
            plan_id, new_start_date, generated_by_uid
        )
        
        if not success:
            return error_response(error_msg, 400)
        
        return success_response({
            'meal_plan': new_plan
        }, 'Meal plan duplicated successfully')
        
    except Exception as e:
        return error_response(f'Error duplicating meal plan: {str(e)}', 500)

@meal_plans_bp.route('/stats', methods=['GET'])
@require_auth
def get_meal_plan_stats():
    """Get meal plan statistics."""
    try:
        all_plans = MealPlan.get_all()
        
        stats = {
            'total': len(all_plans),
            'draft': len([p for p in all_plans if p.get('status') == 'draft']),
            'approved': len([p for p in all_plans if p.get('status') == 'approved']),
            'sent': len([p for p in all_plans if p.get('status') == 'sent'])
        }
        
        # Plans by current user
        user_uid = request.user.get('uid')
        user_plans = [p for p in all_plans if p.get('generated_by_uid') == user_uid]
        stats['created_by_me'] = len(user_plans)
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f'Error retrieving stats: {str(e)}', 500)
