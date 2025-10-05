"""
Servicio para generación automática de planes de comidas personalizados.
"""
import random
import secrets
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import and_, not_, exists
from sqlalchemy.orm import joinedload

from app.services.database_service import db
from app.models.sql_models import (
    Patient, MealPlan, MealPlanMeal, MealPlanToken,
    Recipe, RecipeIngredient, Ingredient,
    PatientMedicalCondition, PatientIntolerance, PatientDietaryPreference,
    MedicalCondition, FoodIntolerance, DietaryPreference
)


class MealPlanService:
    """Servicio para generar planes de comidas automáticamente."""
    
    def __init__(self):
        self.MEAL_TIMES = {
            'breakfast': time(8, 0),    # 8:00 AM
            'lunch': time(13, 0),       # 1:00 PM
            'dinner': time(19, 0)       # 7:00 PM
        }
        
        self.DAY_ORDER = [
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday'
        ]
    
    @staticmethod
    def generate_meal_plan(patient_id: str, start_date: date, end_date: date, generated_by_uid: str, preferences: Dict[str, Any] = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Generate a meal plan for a patient."""
        try:
            from ..models.meal_plan import MealPlan
            
            # For now, create a basic meal plan structure without complex recipe matching
            plan_data = {
                'patient_id': patient_id,
                'start_date': start_date,
                'end_date': end_date,
                'plan_name': f"Plan {start_date.strftime('%d/%m/%Y')}",
                'generated_by_uid': generated_by_uid,
                'status': 'draft'
            }
            
            # Create meal plan
            meal_plan = MealPlan.create(plan_data)
            
            # Generate basic meals for the date range
            meals = MealPlanService._generate_basic_meals(start_date, end_date, preferences or {})
            
            # Add meals to plan
            if meals:
                MealPlan.add_meals(meal_plan['id'], meals)
            
            # Get complete plan with meals
            complete_plan = MealPlan.get_by_id(meal_plan['id'])
            
            return True, complete_plan, None
            
        except Exception as e:
            return False, None, f"Error generating meal plan: {str(e)}"
    
    @staticmethod
    def _generate_basic_meals(
        start_date: date, 
        end_date: date,
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate basic meals without recipe matching."""
        meals = []
        
        # Days of the week mapping
        days_map = {
            0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
            4: 'friday', 5: 'saturday', 6: 'sunday'
        }
        
        # Basic meal templates
        meal_types = ['breakfast', 'lunch', 'dinner']
        
        current_date = start_date
        while current_date <= end_date:
            day_of_week = days_map[current_date.weekday()]
            
            for meal_type in meal_types:
                meal = {
                    'recipe_id': f'sample_{meal_type}',
                    'recipe_name': f'Sample {meal_type.title()}',
                    'day_of_week': day_of_week,
                    'meal_type': meal_type,
                    'servings': 1.0,
                    'scheduled_time': MealPlanService._get_default_meal_time(meal_type),
                    'calories_per_serving': 300,
                    'date': current_date.isoformat()
                }
                meals.append(meal)
            
            current_date += timedelta(days=1)
        
        return meals
    
    @staticmethod
    def _generate_meals(
        recipes: List[Dict[str, Any]], 
        start_date: date, 
        end_date: date,
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate meals for the specified date range."""
        meals = []
        
        # Group recipes by meal type
        recipes_by_type = {
            'breakfast': [r for r in recipes if r.get('meal_type') == 'breakfast'],
            'lunch': [r for r in recipes if r.get('meal_type') == 'lunch'],
            'dinner': [r for r in recipes if r.get('meal_type') == 'dinner'],
            'snack': [r for r in recipes if r.get('meal_type') == 'snack']
        }
        
        # Days of the week mapping
        days_map = {
            0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday',
            4: 'friday', 5: 'saturday', 6: 'sunday'
        }
        
        # Generate meals for each day
        current_date = start_date
        while current_date <= end_date:
            day_of_week = days_map[current_date.weekday()]
            
            # Generate meals for each meal type
            for meal_type, type_recipes in recipes_by_type.items():
                if not type_recipes:
                    continue
                
                # Skip snacks if not requested
                if meal_type == 'snack' and not preferences.get('include_snacks', False):
                    continue
                
                # Select random recipe
                selected_recipe = random.choice(type_recipes)
                
                meal = {
                    'recipe_id': selected_recipe['id'],
                    'recipe_name': selected_recipe['recipe_name'],
                    'day_of_week': day_of_week,
                    'meal_type': meal_type,
                    'servings': 1.0,
                    'scheduled_time': MealPlanService._get_default_meal_time(meal_type),
                    'calories_per_serving': selected_recipe.get('total_calories', 0),
                    'date': current_date.isoformat()
                }
                
                meals.append(meal)
            
            current_date += timedelta(days=1)
        
        return meals
    
    @staticmethod
    def _get_default_meal_time(meal_type: str) -> str:
        """Get default time for meal type."""
        default_times = {
            'breakfast': '08:00',
            'lunch': '13:00',
            'dinner': '19:00',
            'snack': '16:00'
        }
        return default_times.get(meal_type, '12:00')
    
    @staticmethod
    def update_meal_in_plan(
        plan_id: str, 
        meal_id: str, 
        new_recipe_id: str
    ) -> Tuple[bool, Optional[str]]:
        """Update a specific meal in a meal plan."""
        try:
            from ..services.firebase_service import FirebaseService
            
            # Get recipe details
            recipe = Recipe.get_by_id(new_recipe_id)
            if not recipe:
                return False, "Recipe not found"
            
            # Update meal
            db = FirebaseService.get_firestore()
            meal_ref = db.collection(f'meal_plans/{plan_id}/meals').document(meal_id)
            
            update_data = {
                'recipe_id': new_recipe_id,
                'recipe_name': recipe['recipe_name'],
                'calories_per_serving': recipe.get('total_calories', 0),
                'updated_at': datetime.utcnow()
            }
            
            meal_ref.update(update_data)
            
            return True, None
            
        except Exception as e:
            return False, f"Error updating meal: {str(e)}"
    
    @staticmethod
    def approve_meal_plan(plan_id: str, approved_by_uid: str) -> Tuple[bool, Optional[str]]:
        """Approve a meal plan and make it available to patient."""
        try:
            success = MealPlan.approve_plan(plan_id, approved_by_uid)
            if not success:
                return False, "Error approving meal plan"
            
            # TODO: Send notification to patient
            # MealPlanService._notify_patient_plan_ready(plan_id)
            
            return True, None
            
        except Exception as e:
            return False, f"Error approving meal plan: {str(e)}"
    
    @staticmethod
    def get_plan_for_patient_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get meal plan for patient using their invitation token."""
        try:
            plan = MealPlan.get_by_patient_token(token)
            if not plan:
                return False, None, "No approved meal plan found for this patient"
            
            # Organize meals by day and meal type
            calendar = MealPlan.get_weekly_calendar(plan['id'])
            plan['calendar'] = calendar
            
            return True, plan, None
            
        except Exception as e:
            return False, None, f"Error retrieving meal plan: {str(e)}"
    
    @staticmethod
    def duplicate_meal_plan(plan_id: str, new_start_date: date, generated_by_uid: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Duplicate an existing meal plan with new dates."""
        try:
            # Get original plan
            original_plan = MealPlan.get_by_id(plan_id)
            if not original_plan:
                return False, None, "Original meal plan not found"
            
            # Calculate end date (same duration as original)
            original_duration = (original_plan['end_date'] - original_plan['start_date']).days
            new_end_date = new_start_date + timedelta(days=original_duration)
            
            # Create new plan
            new_plan_data = {
                'patient_id': original_plan['patient_id'],
                'start_date': new_start_date,
                'end_date': new_end_date,
                'plan_name': f"Plan {new_start_date.strftime('%d/%m/%Y')} (Copy)",
                'generated_by_uid': generated_by_uid,
                'status': 'draft',
                'notes': f"Duplicated from plan {plan_id}"
            }
            
            new_plan = MealPlan.create(new_plan_data)
            
            # Copy meals with updated dates
            new_meals = []
            date_offset = (new_start_date - original_plan['start_date']).days
            
            for meal in original_plan.get('meals', []):
                new_meal = meal.copy()
                new_meal.pop('id', None)  # Remove original ID
                
                # Update date if present
                if 'date' in new_meal:
                    original_date = datetime.fromisoformat(new_meal['date']).date()
                    new_date = original_date + timedelta(days=date_offset)
                    new_meal['date'] = new_date.isoformat()
                
                new_meals.append(new_meal)
            
            # Add meals to new plan
            if new_meals:
                MealPlan.add_meals(new_plan['id'], new_meals)
            
            # Get complete new plan
            complete_plan = MealPlan.get_by_id(new_plan['id'])
            
            return True, complete_plan, None
            
        except Exception as e:
            return False, None, f"Error duplicating meal plan: {str(e)}"
