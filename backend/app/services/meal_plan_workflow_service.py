"""
Meal Plan Workflow Service - Manages the complete nutritionist-patient workflow.
Handles dynamic link routing based on invitation status.
"""
import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from ..services.database_service import db
from ..models.sql_models import (
    PatientInvitation, Patient, MealPlan, MealPlanToken, MealPlanMeal
)
from ..services.meal_plan_generator import MealPlanGeneratorService

class MealPlanWorkflowService:
    """Service for managing the complete meal plan workflow system."""
    
    @staticmethod
    def create_workflow_invitation(email: str, patient_name: str, invited_by_uid: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Create a new workflow invitation for the meal plan process."""
        try:
            # Check if there's already a pending invitation for this email
            existing = PatientInvitation.query.filter_by(
                email=email, 
                status='pending'
            ).first()
            
            if existing and existing.is_valid:
                # Extend existing invitation
                existing.regenerate_token()
                db.session.commit()
                
                invitation_data = existing.to_dict()
                invitation_data['dynamic_link'] = MealPlanWorkflowService._generate_dynamic_link(existing.token)
                
                return True, invitation_data, None
            
            # Create new invitation with extended fields for workflow
            name_parts = patient_name.split(' ', 1) if patient_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            invitation = PatientInvitation(
                email=email,
                first_name=first_name,
                last_name=last_name,
                invited_by_uid=invited_by_uid,
                status='pending'  # This will control the dynamic link behavior
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            invitation_data = invitation.to_dict()
            invitation_data['dynamic_link'] = MealPlanWorkflowService._generate_dynamic_link(invitation.token)
            
            # TODO: Send invitation email
            # MealPlanWorkflowService._send_workflow_invitation_email(email, invitation_data['dynamic_link'], patient_name)
            
            return True, invitation_data, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            return False, None, f"Error creating workflow invitation: {str(e)}"
    
    @staticmethod
    def get_dynamic_link_content(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get content for the dynamic link based on invitation status."""
        try:
            invitation = PatientInvitation.query.filter_by(token=token).first()
            
            if not invitation:
                return False, None, "Invalid invitation token"
            
            if not invitation.is_valid and invitation.status == 'pending':
                return False, None, "Invitation has expired"
            
            # Build response based on status
            response_data = {
                'invitation': invitation.to_dict(),
                'status': invitation.status,
                'content_type': None,
                'data': {}
            }
            
            if invitation.status == 'pending':
                # Show patient form
                response_data['content_type'] = 'patient_form'
                response_data['data'] = MealPlanWorkflowService._get_form_data()
                
            elif invitation.status == 'completed':
                # Check if there's a patient profile
                patient = Patient.query.filter_by(invitation_id=invitation.id).first()
                if not patient:
                    return False, None, "Patient profile not found"
                
                # Check meal plan status
                meal_plan = MealPlan.query.filter_by(patient_id=patient.id).order_by(MealPlan.created_at.desc()).first()
                
                if not meal_plan:
                    response_data['content_type'] = 'pending_review'
                    response_data['data'] = {
                        'message': 'Your meal plan is being reviewed by your nutritionist and will be ready soon.',
                        'patient_name': f"{patient.first_name} {patient.last_name}"
                    }
                elif meal_plan.status == 'draft':
                    response_data['content_type'] = 'pending_review'
                    response_data['data'] = {
                        'message': 'Your meal plan is being reviewed by your nutritionist and will be ready soon.',
                        'patient_name': f"{patient.first_name} {patient.last_name}"
                    }
                elif meal_plan.status == 'approved':
                    response_data['content_type'] = 'meal_plan'
                    response_data['data'] = MealPlanWorkflowService._get_meal_plan_data(meal_plan, patient)
                else:
                    response_data['content_type'] = 'pending_review'
                    response_data['data'] = {
                        'message': 'Your meal plan is being prepared.',
                        'patient_name': f"{patient.first_name} {patient.last_name}"
                    }
            else:
                return False, None, "Invalid invitation status"
            
            return True, response_data, None
            
        except Exception as e:
            return False, None, f"Error getting dynamic link content: {str(e)}"
    
    @staticmethod
    def submit_patient_form(token: str, form_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Submit patient form and update invitation status."""
        try:
            invitation = PatientInvitation.query.filter_by(token=token).first()
            
            if not invitation or not invitation.is_valid:
                return False, None, "Invalid or expired invitation token"
            
            if invitation.status != 'pending':
                return False, None, "Form has already been submitted"
            
            # Check if patient already exists for this invitation
            existing_patient = Patient.query.filter_by(invitation_id=invitation.id).first()
            if existing_patient:
                return False, None, "Patient profile already exists for this invitation"
            
            # Create patient profile
            # Handle database enum truncation issue
            try:
                profile_status = 'pending_review'
                patient = Patient(
                    invitation_id=invitation.id,
                    first_name=form_data['first_name'],
                    last_name=form_data['last_name'],
                    date_of_birth=datetime.strptime(form_data['date_of_birth'], '%Y-%m-%d').date(),
                    gender=form_data['gender'],
                    email=form_data.get('email', invitation.email),
                    phone=form_data.get('phone'),
                    additional_notes=form_data.get('additional_notes'),
                    profile_status=profile_status
                )
            except Exception:
                # Fallback to truncated enum if full version fails
                patient = Patient(
                    invitation_id=invitation.id,
                    first_name=form_data['first_name'],
                    last_name=form_data['last_name'],
                    date_of_birth=datetime.strptime(form_data['date_of_birth'], '%Y-%m-%d').date(),
                    gender=form_data['gender'],
                    email=form_data.get('email', invitation.email),
                    phone=form_data.get('phone'),
                    additional_notes=form_data.get('additional_notes'),
                    profile_status='pending_rev'
                )
            
            db.session.add(patient)
            db.session.flush()  # Get patient ID
            
            # Add medical conditions, intolerances, and preferences
            MealPlanWorkflowService._add_patient_relations(patient.id, form_data)
            
            # Update invitation status to completed
            invitation.status = 'completed'
            invitation.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, {
                'patient_id': patient.id,
                'message': 'Thank you! Your information has been submitted and is pending nutritionist review.',
                'status': 'completed'
            }, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error submitting form: {str(e)}"
    
    @staticmethod
    def approve_meal_plan(invitation_id: int, approved_by_uid: str, meal_plan_data: Dict[str, Any] = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Approve meal plan and make it available to patient."""
        try:
            invitation = PatientInvitation.query.get(invitation_id)
            if not invitation:
                return False, None, "Invitation not found"
            
            patient = Patient.query.filter_by(invitation_id=invitation_id).first()
            if not patient:
                return False, None, "Patient not found"
            
            # Get or create meal plan
            meal_plan = MealPlan.query.filter_by(patient_id=patient.id).order_by(MealPlan.created_at.desc()).first()
            
            if not meal_plan:
                # Create a basic meal plan if none exists
                from datetime import date, timedelta
                start_date = date.today() + timedelta(days=1)
                end_date = start_date + timedelta(days=6)
                
                meal_plan = MealPlan(
                    patient_id=patient.id,
                    plan_name=f"Plan Semanal - {patient.first_name} {patient.last_name}",
                    start_date=start_date,
                    end_date=end_date,
                    status='draft',
                    notes=meal_plan_data.get('notes', 'Plan personalizado creado por nutricionista'),
                    generated_by_uid=approved_by_uid
                )
                db.session.add(meal_plan)
                db.session.flush()
            
            # Update meal plan with approval
            meal_plan.status = 'approved'
            meal_plan.approved_by_uid = approved_by_uid
            meal_plan.approved_at = datetime.utcnow()
            
            if meal_plan_data:
                if 'notes' in meal_plan_data:
                    meal_plan.notes = meal_plan_data['notes']
                if 'plan_name' in meal_plan_data:
                    meal_plan.plan_name = meal_plan_data['plan_name']
            
            db.session.commit()
            
            # TODO: Send notification email to patient
            # MealPlanWorkflowService._send_meal_plan_ready_email(patient.email, invitation.token)
            
            return True, {
                'meal_plan_id': meal_plan.id,
                'message': 'Meal plan approved successfully',
                'patient_name': f"{patient.first_name} {patient.last_name}"
            }, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, None, f"Database error: {str(e)}"
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error approving meal plan: {str(e)}"
    
    @staticmethod
    def get_nutritionist_dashboard_data(nutritionist_uid: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Get dashboard data for nutritionist."""
        try:
            # Get invitations where patients have submitted forms (completed status)
            # and don't have approved meal plans yet
            completed_invitations = PatientInvitation.query.filter_by(
                invited_by_uid=nutritionist_uid,
                status='completed'
            ).all()
            
            # Filter for those that need review (no approved meal plans)
            pending_review = []
            for invitation in completed_invitations:
                if invitation.patient:
                    # Check if there's an approved meal plan
                    approved_plan = MealPlan.query.filter_by(
                        patient_id=invitation.patient.id,
                        status='approved'
                    ).first()
                    
                    if not approved_plan:
                        pending_review.append(invitation)
            
            # Get approved meal plans
            approved_plans = db.session.query(MealPlan)\
                .join(Patient, MealPlan.patient_id == Patient.id)\
                .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
                .filter(
                    PatientInvitation.invited_by_uid == nutritionist_uid,
                    MealPlan.status == 'approved'
                ).all()
            
            # Get pending invitations
            pending_invitations = PatientInvitation.query.filter_by(
                invited_by_uid=nutritionist_uid,
                status='pending'
            ).all()
            
            dashboard_data = {
                'pending_review': [
                    {
                        'invitation_id': inv.id,
                        'patient_name': f"{inv.first_name or ''} {inv.last_name or ''}".strip(),
                        'email': inv.email,
                        'submitted_at': inv.completed_at.isoformat() if inv.completed_at else None,
                        'patient_id': inv.patient.id if inv.patient else None,
                        'dynamic_link': MealPlanWorkflowService._generate_dynamic_link(inv.token)
                    }
                    for inv in pending_review
                ],
                'approved_plans': [
                    {
                        'meal_plan_id': plan.id,
                        'patient_name': f"{plan.patient.first_name} {plan.patient.last_name}",
                        'plan_name': plan.plan_name,
                        'start_date': plan.start_date.isoformat(),
                        'end_date': plan.end_date.isoformat(),
                        'approved_at': plan.approved_at.isoformat() if plan.approved_at else None,
                        'dynamic_link': MealPlanWorkflowService._generate_dynamic_link(plan.patient.invitation.token)
                    }
                    for plan in approved_plans
                ],
                'pending_invitations': [
                    {
                        'invitation_id': inv.id,
                        'patient_name': f"{inv.first_name or ''} {inv.last_name or ''}".strip(),
                        'email': inv.email,
                        'sent_at': inv.created_at.isoformat(),
                        'expires_at': inv.expires_at.isoformat(),
                        'dynamic_link': MealPlanWorkflowService._generate_dynamic_link(inv.token)
                    }
                    for inv in pending_invitations
                ]
            }
            
            return True, dashboard_data, None
            
        except Exception as e:
            return False, None, f"Error getting dashboard data: {str(e)}"
    
    @staticmethod
    def export_meal_plan_pdf(token: str) -> Tuple[bool, Optional[bytes], Optional[str], Optional[str]]:
        """Export meal plan as PDF."""
        try:
            # Get meal plan data
            success, content_data, error = MealPlanWorkflowService.get_dynamic_link_content(token)
            
            if not success or content_data['content_type'] != 'meal_plan':
                return False, None, None, error or "Meal plan not available for PDF export"
            
            meal_plan_data = content_data['data']
            patient_name = meal_plan_data['patient']['name']
            
            # Generate PDF using reportlab or weasyprint
            pdf_content = MealPlanWorkflowService._generate_pdf_content(meal_plan_data)
            
            # Generate filename
            safe_name = patient_name.replace(' ', '_').replace('.', '')
            today = datetime.now().strftime('%Y%m%d')
            filename = f"MealPlan_{safe_name}_{today}.pdf"
            
            return True, pdf_content, filename, None
            
        except Exception as e:
            return False, None, None, f"Error exporting PDF: {str(e)}"
    
    # Private helper methods
    
    @staticmethod
    def _generate_dynamic_link(token: str) -> str:
        """Generate the dynamic patient link."""
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/patient/invitation/{token}"
    
    @staticmethod
    def _get_form_data() -> Dict[str, Any]:
        """Get form data including catalogs."""
        try:
            from ..models.sql_models import MedicalCondition, FoodIntolerance, DietaryPreference
            
            return {
                'medical_conditions': [mc.to_dict() for mc in MedicalCondition.query.filter_by(is_active=True).all()],
                'food_intolerances': [fi.to_dict() for fi in FoodIntolerance.query.filter_by(is_active=True).all()],
                'dietary_preferences': [dp.to_dict() for dp in DietaryPreference.query.filter_by(is_active=True).all()]
            }
        except Exception:
            return {'medical_conditions': [], 'food_intolerances': [], 'dietary_preferences': []}
    
    @staticmethod
    def _get_meal_plan_data(meal_plan: MealPlan, patient: Patient) -> Dict[str, Any]:
        """Get formatted meal plan data for display."""
        # Load meals with recipes
        meals = MealPlanMeal.query.filter_by(plan_id=meal_plan.id).all()
        
        # Organize meals by day and type
        calendar = {}
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for day in days:
            calendar[day] = {}
            for meal_type in meal_types:
                day_meals = [meal for meal in meals if meal.day_of_week == day and meal.meal_type == meal_type]
                calendar[day][meal_type] = [meal.to_dict() for meal in day_meals]
        
        return {
            'meal_plan': meal_plan.to_dict(),
            'patient': {
                'name': f"{patient.first_name} {patient.last_name}",
                'email': patient.email,
                'conditions': [mc.condition.condition_name for mc in patient.medical_conditions],
                'intolerances': [pi.intolerance.intolerance_name for pi in patient.intolerances],
                'preferences': [dp.preference.preference_name for dp in patient.dietary_preferences]
            },
            'calendar': calendar,
            'meals': [meal.to_dict() for meal in meals]
        }
    
    @staticmethod
    def _add_patient_relations(patient_id: int, form_data: Dict[str, Any]):
        """Add patient medical conditions, intolerances, and preferences."""
        from ..models.sql_models import PatientMedicalCondition, PatientIntolerance, PatientDietaryPreference
        
        # Add medical conditions
        for condition_id in form_data.get('medical_conditions', []):
            pmc = PatientMedicalCondition(
                patient_id=patient_id,
                condition_id=condition_id
            )
            db.session.add(pmc)
        
        # Add intolerances
        for intolerance_id in form_data.get('intolerances', []):
            pi = PatientIntolerance(
                patient_id=patient_id,
                intolerance_id=intolerance_id,
                severity='mild'  # Default severity
            )
            db.session.add(pi)
        
        # Add dietary preferences
        for preference_id in form_data.get('dietary_preferences', []):
            pdp = PatientDietaryPreference(
                patient_id=patient_id,
                preference_id=preference_id
            )
            db.session.add(pdp)
    
    @staticmethod
    def _generate_pdf_content(meal_plan_data: Dict[str, Any]) -> bytes:
        """Generate PDF content for meal plan."""
        # This is a placeholder implementation
        # In a real implementation, you would use libraries like:
        # - reportlab for PDF generation
        # - weasyprint for HTML to PDF conversion
        # - jinja2 for templating
        
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.pdfgen import canvas
            from io import BytesIO
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            
            # Title
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 800, f"Meal Plan - {meal_plan_data['patient']['name']}")
            
            # Plan details
            p.setFont("Helvetica", 12)
            y = 750
            p.drawString(50, y, f"Plan: {meal_plan_data['meal_plan']['plan_name']}")
            y -= 20
            p.drawString(50, y, f"Duration: {meal_plan_data['meal_plan']['start_date']} to {meal_plan_data['meal_plan']['end_date']}")
            y -= 30
            
            # Patient info
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Patient Information:")
            y -= 20
            
            p.setFont("Helvetica", 10)
            if meal_plan_data['patient']['conditions']:
                p.drawString(50, y, f"Medical Conditions: {', '.join(meal_plan_data['patient']['conditions'])}")
                y -= 15
            
            if meal_plan_data['patient']['intolerances']:
                p.drawString(50, y, f"Food Intolerances: {', '.join(meal_plan_data['patient']['intolerances'])}")
                y -= 15
            
            if meal_plan_data['patient']['preferences']:
                p.drawString(50, y, f"Dietary Preferences: {', '.join(meal_plan_data['patient']['preferences'])}")
                y -= 30
            
            # Meal schedule (simplified)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Weekly Meal Schedule:")
            y -= 20
            
            p.setFont("Helvetica", 10)
            for day, meals in meal_plan_data['calendar'].items():
                p.drawString(50, y, f"{day.capitalize()}:")
                y -= 15
                for meal_type, meal_list in meals.items():
                    if meal_list:
                        for meal in meal_list:
                            p.drawString(70, y, f"  {meal_type.capitalize()}: {meal.get('recipe_name', 'Recipe')}")
                            y -= 12
                y -= 10
                
                if y < 100:  # Start new page if needed
                    p.showPage()
                    y = 800
            
            p.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback: return a simple text-based PDF placeholder
            return b"PDF generation requires reportlab library installation."
        except Exception as e:
            return f"Error generating PDF: {str(e)}".encode()
    
    @staticmethod
    def _send_workflow_invitation_email(email: str, dynamic_link: str, patient_name: str):
        """Send workflow invitation email."""
        # TODO: Implement email sending
        pass
    
    @staticmethod
    def _send_meal_plan_ready_email(email: str, token: str):
        """Send meal plan ready notification email."""
        # TODO: Implement email sending
        pass