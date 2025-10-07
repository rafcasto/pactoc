"""
Nutritionist Service - Handles nutritionist profile management and operations.
"""
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from app.services.database_service import db
from app.models.sql_models import Nutritionist, PatientInvitation, MealPlan, Patient

class NutritionistService:
    """Service for managing nutritionist profiles and operations."""
    
    @staticmethod
    def create_or_get_nutritionist(firebase_uid: str, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[Nutritionist], Optional[str]]:
        """Create or get nutritionist by Firebase UID."""
        try:
            # Try to get existing nutritionist
            nutritionist = Nutritionist.query.filter_by(firebase_uid=firebase_uid).first()
            
            if nutritionist:
                return True, nutritionist, None
            
            # Create new nutritionist
            nutritionist = Nutritionist(
                firebase_uid=firebase_uid,
                email=profile_data.get('email'),
                first_name=profile_data.get('first_name', ''),
                last_name=profile_data.get('last_name', ''),
                phone=profile_data.get('phone'),
                license_number=profile_data.get('license_number'),
                specialization=profile_data.get('specialization'),
                bio=profile_data.get('bio'),
                profile_image_url=profile_data.get('profile_image_url')
            )
            
            db.session.add(nutritionist)
            db.session.commit()
            
            return True, nutritionist, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error creating nutritionist: {str(e)}"
    
    @staticmethod
    def update_profile(nutritionist_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[Nutritionist], Optional[str]]:
        """Update nutritionist profile."""
        try:
            nutritionist = Nutritionist.query.get(nutritionist_id)
            if not nutritionist:
                return False, None, "Nutritionist not found"
            
            # Update fields
            for field in ['first_name', 'last_name', 'phone', 'license_number', 
                         'specialization', 'bio', 'profile_image_url']:
                if field in profile_data:
                    setattr(nutritionist, field, profile_data[field])
            
            db.session.commit()
            return True, nutritionist, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error updating profile: {str(e)}"
    
    @staticmethod
    def get_dashboard_data(nutritionist_id: int) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get comprehensive dashboard data for nutritionist."""
        try:
            nutritionist = Nutritionist.query.get(nutritionist_id)
            if not nutritionist:
                return False, None, "Nutritionist not found"
            
            # Get patients (through invitations)
            invitations = PatientInvitation.query.filter_by(nutritionist_id=nutritionist_id).all()
            
            # Categorize patients
            pending_invitations = [inv for inv in invitations if inv.status == 'pending']
            completed_forms = [inv for inv in invitations if inv.status == 'completed' and inv.patient]
            
            # Get approved patients with their latest meal plans
            approved_patients = []
            for invitation in invitations:
                if invitation.patient:
                    latest_plan = MealPlan.get_latest_for_patient(invitation.patient.id)
                    patient_data = invitation.patient.to_dict(include_relations=True)
                    patient_data['latest_meal_plan'] = latest_plan.to_dict() if latest_plan else None
                    patient_data['invitation_id'] = invitation.id
                    approved_patients.append(patient_data)
            
            # Get meal plan statistics
            total_meal_plans = MealPlan.query.filter_by(nutritionist_id=nutritionist_id).count()
            active_meal_plans = MealPlan.query.filter_by(
                nutritionist_id=nutritionist_id, 
                status='approved', 
                is_latest=True
            ).count()
            
            dashboard_data = {
                'nutritionist': nutritionist.to_dict(include_relations=True),
                'stats': {
                    'total_patients': len(approved_patients),
                    'pending_invitations': len(pending_invitations),
                    'pending_reviews': len(completed_forms),
                    'total_meal_plans': total_meal_plans,
                    'active_meal_plans': active_meal_plans
                },
                'pending_invitations': [inv.to_dict() for inv in pending_invitations],
                'pending_reviews': [
                    {
                        **inv.to_dict(),
                        'patient': inv.patient.to_dict(include_relations=True)
                    } for inv in completed_forms
                ],
                'patients': approved_patients
            }
            
            return True, dashboard_data, None
            
        except Exception as e:
            return False, None, f"Error getting dashboard data: {str(e)}"
    
    @staticmethod
    def get_patient_meal_plan_history(nutritionist_id: int, patient_id: int) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """Get all meal plan versions for a patient (nutritionist view)."""
        try:
            # Verify nutritionist has access to this patient
            patient = Patient.query.get(patient_id)
            if not patient or not patient.invitation or patient.invitation.nutritionist_id != nutritionist_id:
                return False, None, "Patient not found or access denied"
            
            # Get all versions
            meal_plans = MealPlan.get_all_versions_for_patient(patient_id)
            
            meal_plan_data = []
            for plan in meal_plans:
                plan_dict = plan.to_dict(include_relations=True)
                plan_dict['patient'] = patient.to_dict()
                meal_plan_data.append(plan_dict)
            
            return True, meal_plan_data, None
            
        except Exception as e:
            return False, None, f"Error getting meal plan history: {str(e)}"
    
    @staticmethod
    def create_meal_plan_version(nutritionist_id: int, patient_id: int, base_plan_id: int = None, 
                                plan_data: Dict[str, Any] = None) -> Tuple[bool, Optional[MealPlan], Optional[str]]:
        """Create a new meal plan version for a patient."""
        try:
            # Verify nutritionist has access to this patient
            patient = Patient.query.get(patient_id)
            if not patient or not patient.invitation or patient.invitation.nutritionist_id != nutritionist_id:
                return False, None, "Patient not found or access denied"
            
            if base_plan_id:
                # Create version from existing plan
                base_plan = MealPlan.query.get(base_plan_id)
                if not base_plan or base_plan.patient_id != patient_id:
                    return False, None, "Base meal plan not found or access denied"
                
                new_plan = base_plan.create_new_version(
                    nutritionist_id=nutritionist_id,
                    plan_name=plan_data.get('plan_name') if plan_data else None,
                    notes=plan_data.get('notes') if plan_data else None
                )
            else:
                # Create new meal plan from scratch
                if not plan_data:
                    return False, None, "Plan data required for new meal plan"
                
                # Mark existing plans as not latest
                db.session.query(MealPlan).filter_by(
                    patient_id=patient_id
                ).update({'is_latest': False})
                
                # Get next version number
                latest = db.session.query(MealPlan).filter_by(
                    patient_id=patient_id
                ).order_by(MealPlan.version.desc()).first()
                
                new_version = latest.version + 1 if latest else 1
                
                new_plan = MealPlan(
                    patient_id=patient_id,
                    nutritionist_id=nutritionist_id,
                    plan_name=plan_data.get('plan_name', f"Meal Plan v{new_version}"),
                    start_date=plan_data.get('start_date'),
                    end_date=plan_data.get('end_date'),
                    status='draft',
                    notes=plan_data.get('notes'),
                    generated_by_uid=patient.invitation.invited_by_uid,  # Keep for compatibility
                    version=new_version,
                    is_latest=True
                )
                
                db.session.add(new_plan)
                db.session.commit()
            
            return True, new_plan, None
            
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error creating meal plan version: {str(e)}"
    
    @staticmethod
    def migrate_existing_data(firebase_uid: str) -> Tuple[bool, Optional[str]]:
        """Migrate existing data to link with nutritionist entity."""
        try:
            # Get or create nutritionist
            nutritionist = Nutritionist.query.filter_by(firebase_uid=firebase_uid).first()
            if not nutritionist:
                return False, "Nutritionist not found"
            
            # Update invitations
            updated_invitations = PatientInvitation.query.filter_by(
                invited_by_uid=firebase_uid, 
                nutritionist_id=None
            ).update({'nutritionist_id': nutritionist.id})
            
            # Update meal plans
            updated_meal_plans = MealPlan.query.filter_by(
                generated_by_uid=firebase_uid,
                nutritionist_id=None
            ).update({'nutritionist_id': nutritionist.id})
            
            db.session.commit()
            
            return True, f"Migrated {updated_invitations} invitations and {updated_meal_plans} meal plans"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error migrating data: {str(e)}"
