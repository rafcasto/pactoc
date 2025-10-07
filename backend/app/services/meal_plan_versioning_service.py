"""
Meal Plan Versioning Service - Handles meal plan versioning logic.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.services.database_service import db
from app.models.sql_models import MealPlan, MealPlanMeal, Patient, Nutritionist

class MealPlanVersioningService:
    """Service for managing meal plan versions."""
    
    @staticmethod
    def get_patient_latest_meal_plan(patient_id: int) -> Optional[MealPlan]:
        """Get the latest approved meal plan for a patient (patient view)."""
        return MealPlan.query.filter_by(
            patient_id=patient_id,
            is_latest=True,
            status='approved'
        ).first()
    
    @staticmethod
    def get_nutritionist_meal_plan_versions(nutritionist_id: int, patient_id: int) -> List[MealPlan]:
        """Get all meal plan versions for a patient (nutritionist view)."""
        # Verify nutritionist has access
        patient = Patient.query.get(patient_id)
        if not patient or not patient.invitation or patient.invitation.nutritionist_id != nutritionist_id:
            return []
        
        return MealPlan.query.filter_by(
            patient_id=patient_id
        ).order_by(MealPlan.version.desc()).all()
    
    @staticmethod
    def create_new_version_from_existing(base_plan_id: int, nutritionist_id: int, 
                                       updates: Dict[str, Any] = None) -> Tuple[bool, Optional[MealPlan], Optional[str]]:
        """Create a new version of an existing meal plan."""
        try:
            base_plan = MealPlan.query.get(base_plan_id)
            if not base_plan:
                return False, None, "Base meal plan not found"
            
            # Verify nutritionist has access
            if base_plan.nutritionist_id != nutritionist_id:
                return False, None, "Access denied"
            
            # Get next version number
            latest_version = db.session.query(MealPlan)\
                .filter_by(patient_id=base_plan.patient_id)\
                .order_by(MealPlan.version.desc())\
                .first()
            
            new_version_num = (latest_version.version + 1) if latest_version else 1
            
            # Mark all existing versions as not latest
            db.session.query(MealPlan).filter_by(
                patient_id=base_plan.patient_id
            ).update({'is_latest': False})
            
            # Create new version
            new_plan = MealPlan(
                patient_id=base_plan.patient_id,
                nutritionist_id=nutritionist_id,
                plan_name=updates.get('plan_name', f"{base_plan.plan_name} (v{new_version_num})"),
                start_date=updates.get('start_date', base_plan.start_date),
                end_date=updates.get('end_date', base_plan.end_date),
                status='draft',  # Always start as draft
                notes=updates.get('notes', f"Version {new_version_num} - Updated from v{base_plan.version}"),
                generated_by_uid=base_plan.generated_by_uid,
                version=new_version_num,
                is_latest=True,
                parent_plan_id=base_plan.id
            )
            
            db.session.add(new_plan)
            db.session.flush()  # Get the new plan ID
            
            # Copy meals from base plan (if not overridden)
            if not updates or 'meals' not in updates:
                for meal in base_plan.meals:
                    new_meal = MealPlanMeal(
                        plan_id=new_plan.id,
                        recipe_id=meal.recipe_id,
                        day_of_week=meal.day_of_week,
                        meal_type=meal.meal_type,
                        scheduled_time=meal.scheduled_time,
                        servings=meal.servings
                    )
                    db.session.add(new_meal)
            else:
                # Add custom meals if provided
                for meal_data in updates.get('meals', []):
                    new_meal = MealPlanMeal(
                        plan_id=new_plan.id,
                        recipe_id=meal_data['recipe_id'],
                        day_of_week=meal_data['day_of_week'],
                        meal_type=meal_data['meal_type'],
                        scheduled_time=meal_data.get('scheduled_time'),
                        servings=meal_data.get('servings', 1.0)
                    )
                    db.session.add(new_meal)
            
            db.session.commit()
            return True, new_plan, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error creating new version: {str(e)}"
    
    @staticmethod
    def approve_meal_plan_version(plan_id: int, nutritionist_id: int, approval_notes: str = None) -> Tuple[bool, Optional[MealPlan], Optional[str]]:
        """Approve a meal plan version."""
        try:
            meal_plan = MealPlan.query.get(plan_id)
            if not meal_plan:
                return False, None, "Meal plan not found"
            
            # Verify nutritionist has access
            if meal_plan.nutritionist_id != nutritionist_id:
                return False, None, "Access denied"
            
            # Update meal plan status
            meal_plan.status = 'approved'
            meal_plan.approved_by_uid = meal_plan.generated_by_uid  # Keep for compatibility
            meal_plan.approved_at = datetime.utcnow()
            
            if approval_notes:
                meal_plan.notes = f"{meal_plan.notes}\n\nApproval Notes: {approval_notes}"
            
            db.session.commit()
            return True, meal_plan, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error approving meal plan: {str(e)}"
    
    @staticmethod
    def get_version_comparison(plan_id_1: int, plan_id_2: int, nutritionist_id: int) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Compare two meal plan versions."""
        try:
            plan1 = MealPlan.query.get(plan_id_1)
            plan2 = MealPlan.query.get(plan_id_2)
            
            if not plan1 or not plan2:
                return False, None, "One or both meal plans not found"
            
            # Verify access and same patient
            if (plan1.nutritionist_id != nutritionist_id or 
                plan2.nutritionist_id != nutritionist_id or
                plan1.patient_id != plan2.patient_id):
                return False, None, "Access denied or plans are not for the same patient"
            
            # Build comparison data
            comparison = {
                'patient_id': plan1.patient_id,
                'patient_name': f"{plan1.patient.first_name} {plan1.patient.last_name}",
                'plan1': {
                    'id': plan1.id,
                    'version': plan1.version,
                    'plan_name': plan1.plan_name,
                    'status': plan1.status,
                    'created_at': plan1.created_at.isoformat(),
                    'meals': [meal.to_dict() for meal in plan1.meals]
                },
                'plan2': {
                    'id': plan2.id,
                    'version': plan2.version,
                    'plan_name': plan2.plan_name,
                    'status': plan2.status,
                    'created_at': plan2.created_at.isoformat(),
                    'meals': [meal.to_dict() for meal in plan2.meals]
                }
            }
            
            # Calculate differences
            plan1_recipes = {(m.day_of_week, m.meal_type): m.recipe_id for m in plan1.meals}
            plan2_recipes = {(m.day_of_week, m.meal_type): m.recipe_id for m in plan2.meals}
            
            changes = []
            all_slots = set(plan1_recipes.keys()) | set(plan2_recipes.keys())
            
            for slot in all_slots:
                day, meal_type = slot
                recipe1 = plan1_recipes.get(slot)
                recipe2 = plan2_recipes.get(slot)
                
                if recipe1 != recipe2:
                    changes.append({
                        'day_of_week': day,
                        'meal_type': meal_type,
                        'old_recipe_id': recipe1,
                        'new_recipe_id': recipe2,
                        'change_type': 'added' if not recipe1 else ('removed' if not recipe2 else 'modified')
                    })
            
            comparison['changes'] = changes
            comparison['total_changes'] = len(changes)
            
            return True, comparison, None
            
        except Exception as e:
            return False, None, f"Error comparing versions: {str(e)}"
    
    @staticmethod
    def revert_to_version(target_plan_id: int, nutritionist_id: int) -> Tuple[bool, Optional[MealPlan], Optional[str]]:
        """Create a new version based on an older version (revert)."""
        try:
            target_plan = MealPlan.query.get(target_plan_id)
            if not target_plan:
                return False, None, "Target meal plan not found"
            
            # Verify access
            if target_plan.nutritionist_id != nutritionist_id:
                return False, None, "Access denied"
            
            # Create new version from target plan
            return MealPlanVersioningService.create_new_version_from_existing(
                base_plan_id=target_plan_id,
                nutritionist_id=nutritionist_id,
                updates={
                    'plan_name': f"{target_plan.plan_name} (Reverted)",
                    'notes': f"Reverted to version {target_plan.version}"
                }
            )
            
        except Exception as e:
            return False, None, f"Error reverting to version: {str(e)}"
    
    @staticmethod
    def get_version_statistics(patient_id: int, nutritionist_id: int) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get statistics about meal plan versions for a patient."""
        try:
            # Verify access
            patient = Patient.query.get(patient_id)
            if not patient or not patient.invitation or patient.invitation.nutritionist_id != nutritionist_id:
                return False, None, "Patient not found or access denied"
            
            versions = MealPlan.query.filter_by(patient_id=patient_id).all()
            
            if not versions:
                return True, {
                    'patient_id': patient_id,
                    'total_versions': 0,
                    'approved_versions': 0,
                    'draft_versions': 0,
                    'latest_version': None,
                    'first_created': None,
                    'last_updated': None
                }, None
            
            approved_count = len([v for v in versions if v.status == 'approved'])
            draft_count = len([v for v in versions if v.status == 'draft'])
            latest = next((v for v in versions if v.is_latest), None)
            
            stats = {
                'patient_id': patient_id,
                'patient_name': f"{patient.first_name} {patient.last_name}",
                'total_versions': len(versions),
                'approved_versions': approved_count,
                'draft_versions': draft_count,
                'latest_version': latest.version if latest else None,
                'latest_status': latest.status if latest else None,
                'first_created': min(v.created_at for v in versions).isoformat(),
                'last_updated': max(v.updated_at for v in versions).isoformat(),
                'versions_timeline': [
                    {
                        'version': v.version,
                        'status': v.status,
                        'created_at': v.created_at.isoformat(),
                        'is_latest': v.is_latest,
                        'meal_count': len(v.meals)
                    } for v in sorted(versions, key=lambda x: x.version)
                ]
            }
            
            return True, stats, None
            
        except Exception as e:
            return False, None, f"Error getting version statistics: {str(e)}"
