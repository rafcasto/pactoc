import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from ..models.sql_models import PatientInvitation, Patient, Nutritionist
from ..services.database_service import db
from ..utils.responses import success_response, error_response

class InvitationService:
    """Service for managing patient invitations."""
    
    @staticmethod
    def create_invitation(email: str, invited_by_uid: str, first_name: str = None, last_name: str = None) -> Tuple[Dict[str, Any], Optional[str]]:
        """Create a new patient invitation and return the public link."""
        try:
            # Get nutritionist entity
            nutritionist = Nutritionist.query.filter_by(firebase_uid=invited_by_uid).first()
            if not nutritionist:
                return None, "Nutritionist not found"
            
            # Check if there's already a pending invitation for this email from this nutritionist
            existing = PatientInvitation.query.filter_by(
                email=email,
                nutritionist_id=nutritionist.id,
                status='pending'
            ).first()
            
            if existing and existing.is_valid:
                # Extend the existing invitation
                existing.regenerate_token()
                db.session.commit()
                public_link = InvitationService._generate_public_link(existing.token)
                return existing.to_dict(), public_link
            
            # Create new invitation
            invitation = PatientInvitation(
                email=email,
                first_name=first_name,
                last_name=last_name,
                invited_by_uid=invited_by_uid,  # Keep for backward compatibility
                nutritionist_id=nutritionist.id,  # New FK relationship
                status='pending'
            )
            
            db.session.add(invitation)
            db.session.commit()
            
            public_link = InvitationService._generate_public_link(invitation.token)
            
            # TODO: Send email notification
            # InvitationService._send_invitation_email(email, public_link, first_name)
            
            return invitation.to_dict(), public_link
            
        except Exception as e:
            db.session.rollback()
            return None, f"Error creating invitation: {str(e)}"
    
    @staticmethod
    def _generate_public_link(token: str) -> str:
        """Generate the public link for completing profile."""
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/complete-profile/{token}"
    
    @staticmethod
    def _send_invitation_email(email: str, link: str, first_name: str = None):
        """Send invitation email to patient."""
        # TODO: Implement email sending with your preferred service
        # This could use SendGrid, AWS SES, or any other email service
        pass
    
    @staticmethod
    def validate_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate invitation token and return invitation data."""
        try:
            invitation = PatientInvitation.query.filter_by(token=token).first()
            
            if not invitation:
                return False, None, "Invitation not found"
            
            if not invitation.is_valid:
                return False, None, "Invalid or expired token"
            
            # Check if already completed
            if invitation.status == 'completed':
                return False, None, "This invitation has already been used"
            
            return True, invitation.to_dict(), None
            
        except Exception as e:
            return False, None, f"Error validating token: {str(e)}"
    
    @staticmethod
    def complete_profile(token: str, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Complete patient profile using invitation token."""
        try:
            # Validate token
            is_valid, invitation_dict, error = InvitationService.validate_token(token)
            if not is_valid:
                return False, None, error
            
            # Get invitation object
            invitation = PatientInvitation.query.filter_by(token=token).first()
            if not invitation:
                return False, None, "Invitation not found"
            
            # Check if patient already exists
            existing_patient = Patient.query.filter_by(invitation_id=invitation.id).first()
            if existing_patient:
                return False, None, "Profile already completed for this invitation"
            
            # Create patient profile
            patient = Patient(
                invitation_id=invitation.id,
                first_name=profile_data.get('first_name', invitation.first_name),
                last_name=profile_data.get('last_name', invitation.last_name),
                date_of_birth=datetime.strptime(profile_data['date_of_birth'], '%Y-%m-%d').date(),
                gender=profile_data['gender'],
                email=profile_data.get('email', invitation.email),
                phone=profile_data.get('phone'),
                additional_notes=profile_data.get('additional_notes'),
                profile_status='pending_review'
            )
            
            db.session.add(patient)
            db.session.flush()  # Get patient ID
            
            # Add medical conditions, intolerances, and preferences
            InvitationService._add_patient_conditions(patient.id, profile_data)
            
            # Mark invitation as completed
            invitation.status = 'completed'
            invitation.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, patient.to_dict(), None
            
        except Exception as e:
            db.session.rollback()
            return False, None, f"Error completing profile: {str(e)}"
    
    @staticmethod
    def _add_patient_conditions(patient_id: int, profile_data: Dict[str, Any]):
        """Add patient's medical conditions, intolerances, and preferences."""
        from ..models.sql_models import PatientMedicalCondition, PatientIntolerance, PatientDietaryPreference
        
        # Add medical conditions
        for condition_id in profile_data.get('medical_conditions', []):
            pmc = PatientMedicalCondition(
                patient_id=patient_id,
                condition_id=condition_id
            )
            db.session.add(pmc)
        
        # Add intolerances
        for intolerance_id in profile_data.get('intolerances', []):
            pi = PatientIntolerance(
                patient_id=patient_id,
                intolerance_id=intolerance_id,
                severity='mild'  # Default severity
            )
            db.session.add(pi)
        
        # Add dietary preferences
        for preference_id in profile_data.get('dietary_preferences', []):
            pdp = PatientDietaryPreference(
                patient_id=patient_id,
                preference_id=preference_id
            )
            db.session.add(pdp)
    
    @staticmethod
    def resend_invitation(invitation_id: int) -> Tuple[bool, Optional[str]]:
        """Resend invitation email."""
        try:
            invitation = PatientInvitation.query.get(invitation_id)
            if not invitation:
                return False, "Invitation not found"
            
            if invitation.status != 'pending':
                return False, "Cannot resend completed or expired invitation"
            
            # Extend expiration
            invitation.regenerate_token()
            db.session.commit()
            
            # Generate new link and send email
            public_link = InvitationService._generate_public_link(invitation.token)
            # TODO: Send email
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error resending invitation: {str(e)}"
