from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import secrets
from ..services.firebase_service import FirebaseService

class PatientInvitation:
    """Patient invitation model for Firestore operations."""
    
    COLLECTION_NAME = 'patient_invitations'
    
    @staticmethod
    def create(email: str, invited_by_uid: str, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Create a new patient invitation."""
        db = FirebaseService.get_firestore()
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        invitation_data = {
            'token': token,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'invited_by_uid': invited_by_uid,
            'status': 'pending',
            'expires_at': datetime.utcnow() + timedelta(days=7),
            'created_at': datetime.utcnow()
        }
        
        # Create document with auto-generated ID
        doc_ref = db.collection(PatientInvitation.COLLECTION_NAME).document()
        doc_ref.set(invitation_data)
        
        # Return invitation with ID
        result = invitation_data.copy()
        result['id'] = doc_ref.id
        return result
    
    @staticmethod
    def get_by_token(token: str) -> Optional[Dict[str, Any]]:
        """Get invitation by token."""
        db = FirebaseService.get_firestore()
        invitations = db.collection(PatientInvitation.COLLECTION_NAME)\
                       .where('token', '==', token)\
                       .limit(1)\
                       .stream()
        
        for invitation in invitations:
            data = invitation.to_dict()
            data['id'] = invitation.id
            return data
        return None
    
    @staticmethod
    def get_by_id(invitation_id: str) -> Optional[Dict[str, Any]]:
        """Get invitation by ID."""
        db = FirebaseService.get_firestore()
        doc = db.collection(PatientInvitation.COLLECTION_NAME).document(invitation_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    @staticmethod
    def get_all_by_user(invited_by_uid: str) -> List[Dict[str, Any]]:
        """Get all invitations created by a user."""
        db = FirebaseService.get_firestore()
        invitations = db.collection(PatientInvitation.COLLECTION_NAME)\
                       .where('invited_by_uid', '==', invited_by_uid)\
                       .order_by('created_at', direction='DESCENDING')\
                       .stream()
        
        result = []
        for doc in invitations:
            data = doc.to_dict()
            data['id'] = doc.id
            result.append(data)
        
        return result
    
    @staticmethod
    def update_status(invitation_id: str, status: str, completed_at: datetime = None) -> bool:
        """Update invitation status."""
        db = FirebaseService.get_firestore()
        
        update_data = {'status': status}
        if completed_at:
            update_data['completed_at'] = completed_at
        
        try:
            db.collection(PatientInvitation.COLLECTION_NAME).document(invitation_id).update(update_data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_valid_token(token: str) -> bool:
        """Check if token is valid (exists, not expired, pending status)."""
        invitation = PatientInvitation.get_by_token(token)
        
        if not invitation:
            return False
        
        # Check if expired
        if invitation['expires_at'] < datetime.utcnow():
            return False
        
        # Check if still pending
        if invitation['status'] != 'pending':
            return False
        
        return True
    
    @staticmethod
    def extend_expiration(invitation_id: str, days: int = 7) -> bool:
        """Extend invitation expiration."""
        db = FirebaseService.get_firestore()
        
        new_expiration = datetime.utcnow() + timedelta(days=days)
        
        try:
            db.collection(PatientInvitation.COLLECTION_NAME)\
              .document(invitation_id)\
              .update({'expires_at': new_expiration})
            return True
        except Exception:
            return False
    
    @staticmethod
    def cancel_invitation(invitation_id: str) -> bool:
        """Cancel invitation by setting status to expired."""
        return PatientInvitation.update_status(invitation_id, 'expired')
