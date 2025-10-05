import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from ..models.patient_invitation import PatientInvitation
from ..models.patient import Patient
from ..utils.responses import success_response, error_response

class InvitationService:
    """Service for managing patient invitations."""
    
    @staticmethod
    def create_invitation(email: str, invited_by_uid: str, first_name: str = None, last_name: str = None) -> Tuple[Dict[str, Any], Optional[str]]:
        """Create a new patient invitation and return the public link."""
        try:
            # Check if there's already a pending invitation for this email
            existing_invitations = PatientInvitation.get_all_by_user(invited_by_uid)
            for inv in existing_invitations:
                if inv['email'] == email and inv['status'] == 'pending':
                    # Extend the existing invitation
                    PatientInvitation.extend_expiration(inv['id'])
                    public_link = InvitationService._generate_public_link(inv['token'])
                    return inv, public_link
            
            # Create new invitation
            invitation = PatientInvitation.create(email, invited_by_uid, first_name, last_name)
            public_link = InvitationService._generate_public_link(invitation['token'])
            
            # TODO: Send email notification
            # InvitationService._send_invitation_email(email, public_link, first_name)
            
            return invitation, public_link
            
        except Exception as e:
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
            if not PatientInvitation.is_valid_token(token):
                return False, None, "Invalid or expired token"
            
            invitation = PatientInvitation.get_by_token(token)
            if not invitation:
                return False, None, "Invitation not found"
            
            # Check if already completed
            if invitation['status'] == 'completed':
                return False, None, "This invitation has already been used"
            
            return True, invitation, None
            
        except Exception as e:
            return False, None, f"Error validating token: {str(e)}"
    
    @staticmethod
    def complete_profile(token: str, profile_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Complete patient profile using invitation token."""
        try:
            # Validate token
            is_valid, invitation, error = InvitationService.validate_token(token)
            if not is_valid:
                return False, None, error
            
            # Check if patient already exists
            existing_patient = Patient.get_by_invitation_id(invitation['id'])
            if existing_patient:
                return False, None, "Profile already completed for this invitation"
            
            # Create patient profile
            patient_data = {
                'invitation_id': invitation['id'],
                'first_name': profile_data.get('first_name', invitation.get('first_name')),
                'last_name': profile_data.get('last_name', invitation.get('last_name')),
                'date_of_birth': profile_data['date_of_birth'],
                'gender': profile_data['gender'],
                'email': profile_data.get('email', invitation['email']),
                'phone': profile_data.get('phone'),
                'additional_notes': profile_data.get('additional_notes'),
                'profile_status': 'pending_review'
            }
            
            patient = Patient.create(patient_data)
            
            # Add medical conditions, intolerances, and preferences as subcollections
            InvitationService._add_patient_conditions(patient['id'], profile_data)
            
            # Mark invitation as completed
            PatientInvitation.update_status(invitation['id'], 'completed', datetime.utcnow())
            
            return True, patient, None
            
        except Exception as e:
            return False, None, f"Error completing profile: {str(e)}"
    
    @staticmethod
    def _add_patient_conditions(patient_id: str, profile_data: Dict[str, Any]):
        """Add patient's medical conditions, intolerances, and preferences."""
        from ..services.firebase_service import FirebaseService
        
        db = FirebaseService.get_firestore()
        
        # Add medical conditions
        conditions = profile_data.get('medical_conditions', [])
        for condition in conditions:
            db.collection(f'patients/{patient_id}/medical_conditions').add({
                'condition_id': condition.get('id'),
                'condition_name': condition.get('name'),
                'notes': condition.get('notes', ''),
                'added_at': datetime.utcnow()
            })
        
        # Add intolerances
        intolerances = profile_data.get('intolerances', [])
        for intolerance in intolerances:
            db.collection(f'patients/{patient_id}/intolerances').add({
                'intolerance_id': intolerance.get('id'),
                'intolerance_name': intolerance.get('name'),
                'severity': intolerance.get('severity', 'mild'),
                'notes': intolerance.get('notes', ''),
                'added_at': datetime.utcnow()
            })
        
        # Add dietary preferences
        preferences = profile_data.get('dietary_preferences', [])
        for preference in preferences:
            db.collection(f'patients/{patient_id}/dietary_preferences').add({
                'preference_id': preference.get('id'),
                'preference_name': preference.get('name'),
                'added_at': datetime.utcnow()
            })
    
    @staticmethod
    def resend_invitation(invitation_id: str) -> Tuple[bool, Optional[str]]:
        """Resend invitation email."""
        try:
            invitation = PatientInvitation.get_by_id(invitation_id)
            if not invitation:
                return False, "Invitation not found"
            
            if invitation['status'] != 'pending':
                return False, "Cannot resend completed or expired invitation"
            
            # Extend expiration
            PatientInvitation.extend_expiration(invitation_id)
            
            # Generate new link and send email
            public_link = InvitationService._generate_public_link(invitation['token'])
            # TODO: Send email
            
            return True, None
            
        except Exception as e:
            return False, f"Error resending invitation: {str(e)}"
