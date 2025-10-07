"""
Patient Meal Plan Routes - Updated to handle versioning.
Patients can only see the latest approved version.
"""
from flask import Blueprint, request, jsonify
from app.services.meal_plan_versioning_service import MealPlanVersioningService
from app.models.sql_models import PatientInvitation

patient_meal_plan_bp = Blueprint('patient_meal_plan', __name__, url_prefix='/api/patient')

@patient_meal_plan_bp.route('/meal-plan/<token>', methods=['GET'])
def get_patient_meal_plan(token):
    """Get the latest approved meal plan for a patient using their invitation token."""
    try:
        # Get invitation by token
        invitation = PatientInvitation.query.filter_by(token=token).first()
        if not invitation:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 404
        
        # Check if invitation is valid
        if not invitation.is_valid:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 400
        
        # Get patient
        if not invitation.patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found'
            }), 404
        
        # Get latest approved meal plan
        latest_plan = MealPlanVersioningService.get_patient_latest_meal_plan(invitation.patient.id)
        
        if not latest_plan:
            return jsonify({
                'success': False,
                'message': 'No approved meal plan found'
            }), 404
        
        # Build response with patient info and meal plan
        response_data = {
            'patient': {
                'name': f"{invitation.patient.first_name} {invitation.patient.last_name}",
                'email': invitation.patient.email,
                'conditions': [mc.condition.condition_name for mc in invitation.patient.medical_conditions],
                'intolerances': [pi.intolerance.intolerance_name for pi in invitation.patient.intolerances],
                'preferences': [dp.preference.preference_name for dp in invitation.patient.dietary_preferences]
            },
            'meal_plan': {
                'id': latest_plan.id,
                'plan_name': latest_plan.plan_name,
                'version': latest_plan.version,
                'start_date': latest_plan.start_date.isoformat(),
                'end_date': latest_plan.end_date.isoformat(),
                'notes': latest_plan.notes,
                'approved_at': latest_plan.approved_at.isoformat() if latest_plan.approved_at else None,
                'nutritionist': {
                    'name': f"{latest_plan.nutritionist.first_name} {latest_plan.nutritionist.last_name}" if latest_plan.nutritionist else "Unknown",
                    'specialization': latest_plan.nutritionist.specialization if latest_plan.nutritionist else None
                }
            },
            'meals': []
        }
        
        # Organize meals by day and type
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_types_order = ['breakfast', 'lunch', 'dinner', 'snack']
        
        # Group meals by day
        meals_by_day = {}
        for meal in latest_plan.meals:
            day = meal.day_of_week
            if day not in meals_by_day:
                meals_by_day[day] = {}
            meals_by_day[day][meal.meal_type] = {
                'recipe_name': meal.recipe.recipe_name if meal.recipe else 'Unknown Recipe',
                'recipe_id': meal.recipe_id,
                'servings': float(meal.servings),
                'scheduled_time': meal.scheduled_time.strftime('%H:%M') if meal.scheduled_time else None,
                'calories': float(meal.recipe.total_calories) if meal.recipe and meal.recipe.total_calories else 0,
                'protein': float(meal.recipe.total_protein) if meal.recipe and meal.recipe.total_protein else 0,
                'carbs': float(meal.recipe.total_carbs) if meal.recipe and meal.recipe.total_carbs else 0,
                'fat': float(meal.recipe.total_fat) if meal.recipe and meal.recipe.total_fat else 0,
                'preparation_time': meal.recipe.preparation_time if meal.recipe else None,
                'cooking_time': meal.recipe.cooking_time if meal.recipe else None,
                'difficulty': meal.recipe.difficulty_level if meal.recipe else None,
                'ingredients': [
                    {
                        'name': ri.ingredient.ingredient_name,
                        'quantity': float(ri.quantity),
                        'unit': ri.unit
                    } for ri in meal.recipe.ingredients
                ] if meal.recipe else [],
                'instructions': meal.recipe.instructions if meal.recipe else None
            }
        
        # Format meals in ordered structure
        for day in days_order:
            if day in meals_by_day:
                day_meals = []
                for meal_type in meal_types_order:
                    if meal_type in meals_by_day[day]:
                        meal_data = meals_by_day[day][meal_type]
                        meal_data['type'] = meal_type.title()
                        day_meals.append(meal_data)
                
                if day_meals:  # Only add days that have meals
                    response_data['meals'].append({
                        'day': day.title(),
                        'day_of_week': day,
                        'meals': day_meals
                    })
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@patient_meal_plan_bp.route('/meal-plan/<token>/summary', methods=['GET'])
def get_patient_meal_plan_summary(token):
    """Get a summary of the patient's latest meal plan."""
    try:
        # Get invitation by token
        invitation = PatientInvitation.query.filter_by(token=token).first()
        if not invitation:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 404
        
        if not invitation.patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found'
            }), 404
        
        # Get latest approved meal plan
        latest_plan = MealPlanVersioningService.get_patient_latest_meal_plan(invitation.patient.id)
        
        if not latest_plan:
            return jsonify({
                'success': False,
                'message': 'No approved meal plan found'
            }), 404
        
        # Calculate summary statistics
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        meal_count = 0
        
        for meal in latest_plan.meals:
            if meal.recipe:
                meal_count += 1
                servings = float(meal.servings)
                total_calories += float(meal.recipe.total_calories or 0) * servings
                total_protein += float(meal.recipe.total_protein or 0) * servings
                total_carbs += float(meal.recipe.total_carbs or 0) * servings
                total_fat += float(meal.recipe.total_fat or 0) * servings
        
        # Calculate daily averages (assuming 7 days)
        days_count = 7
        avg_daily_calories = total_calories / days_count if days_count > 0 else 0
        avg_daily_protein = total_protein / days_count if days_count > 0 else 0
        avg_daily_carbs = total_carbs / days_count if days_count > 0 else 0
        avg_daily_fat = total_fat / days_count if days_count > 0 else 0
        
        summary = {
            'patient_name': f"{invitation.patient.first_name} {invitation.patient.last_name}",
            'plan_name': latest_plan.plan_name,
            'version': latest_plan.version,
            'start_date': latest_plan.start_date.isoformat(),
            'end_date': latest_plan.end_date.isoformat(),
            'total_meals': meal_count,
            'nutritionist': f"{latest_plan.nutritionist.first_name} {latest_plan.nutritionist.last_name}" if latest_plan.nutritionist else "Unknown",
            'daily_averages': {
                'calories': round(avg_daily_calories, 1),
                'protein': round(avg_daily_protein, 1),
                'carbs': round(avg_daily_carbs, 1),
                'fat': round(avg_daily_fat, 1)
            },
            'weekly_totals': {
                'calories': round(total_calories, 1),
                'protein': round(total_protein, 1),
                'carbs': round(total_carbs, 1),
                'fat': round(total_fat, 1)
            }
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
