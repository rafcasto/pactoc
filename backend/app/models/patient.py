from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ..services.firebase_service import FirebaseService

class Patient:
    """Patient model for Firestore operations."""
    
    COLLECTION_NAME = 'patients'
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new patient document."""
        db = FirebaseService.get_firestore()
        
        # Add timestamps
        data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'profile_status': 'pending_review'
        })
        
        # Create document with auto-generated ID
        doc_ref = db.collection(Patient.COLLECTION_NAME).document()
        doc_ref.set(data)
        
        # Return data with ID
        result = data.copy()
        result['id'] = doc_ref.id
        return result
    
    @staticmethod
    def get_by_id(patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID."""
        db = FirebaseService.get_firestore()
        doc = db.collection(Patient.COLLECTION_NAME).document(patient_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    @staticmethod
    def get_by_invitation_id(invitation_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by invitation ID."""
        db = FirebaseService.get_firestore()
        patients = db.collection(Patient.COLLECTION_NAME)\
                    .where('invitation_id', '==', invitation_id)\
                    .limit(1)\
                    .stream()
        
        for patient in patients:
            data = patient.to_dict()
            data['id'] = patient.id
            return data
        return None
    
    @staticmethod
    def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all patients with optional filters."""
        db = FirebaseService.get_firestore()
        query = db.collection(Patient.COLLECTION_NAME)
        
        # Apply filters
        if filters:
            if 'profile_status' in filters:
                query = query.where('profile_status', '==', filters['profile_status'])
            if 'is_active' in filters:
                query = query.where('is_active', '==', filters['is_active'])
        
        # Order by created_at desc
        query = query.order_by('created_at', direction='DESCENDING')
        
        patients = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            patients.append(data)
        
        return patients
    
    @staticmethod
    def update(patient_id: str, data: Dict[str, Any]) -> bool:
        """Update patient data."""
        db = FirebaseService.get_firestore()
        
        # Add updated timestamp
        data['updated_at'] = datetime.utcnow()
        
        try:
            db.collection(Patient.COLLECTION_NAME).document(patient_id).update(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete(patient_id: str) -> bool:
        """Soft delete patient (set is_active to False)."""
        return Patient.update(patient_id, {'is_active': False})
    
    @staticmethod
    def get_with_conditions_and_preferences(patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient with their medical conditions, intolerances, and preferences."""
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return None
        
        db = FirebaseService.get_firestore()
        
        # Get medical conditions
        conditions = []
        conditions_ref = db.collection(f'{Patient.COLLECTION_NAME}/{patient_id}/medical_conditions')
        for doc in conditions_ref.stream():
            condition = doc.to_dict()
            condition['id'] = doc.id
            conditions.append(condition)
        
        # Get intolerances
        intolerances = []
        intolerances_ref = db.collection(f'{Patient.COLLECTION_NAME}/{patient_id}/intolerances')
        for doc in intolerances_ref.stream():
            intolerance = doc.to_dict()
            intolerance['id'] = doc.id
            intolerances.append(intolerance)
        
        # Get dietary preferences
        preferences = []
        preferences_ref = db.collection(f'{Patient.COLLECTION_NAME}/{patient_id}/dietary_preferences')
        for doc in preferences_ref.stream():
            preference = doc.to_dict()
            preference['id'] = doc.id
            preferences.append(preference)
        
        patient['medical_conditions'] = conditions
        patient['intolerances'] = intolerances
        patient['dietary_preferences'] = preferences
        
        return patient
