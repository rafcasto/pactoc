from datetime import datetime, date
from typing import Dict, List, Optional, Any
from ..services.firebase_service import FirebaseService

class MealPlan:
    """Meal plan model for Firestore operations."""
    
    COLLECTION_NAME = 'meal_plans'
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new meal plan document."""
        db = FirebaseService.get_firestore()
        
        # Add timestamps and defaults
        data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': data.get('status', 'draft')
        })
        
        # Create document with auto-generated ID
        doc_ref = db.collection(MealPlan.COLLECTION_NAME).document()
        doc_ref.set(data)
        
        # Return data with ID
        result = data.copy()
        result['id'] = doc_ref.id
        return result
    
    @staticmethod
    def get_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
        """Get meal plan by ID with meals."""
        db = FirebaseService.get_firestore()
        doc = db.collection(MealPlan.COLLECTION_NAME).document(plan_id).get()
        
        if not doc.exists:
            return None
        
        plan = doc.to_dict()
        plan['id'] = doc.id
        
        # Get meals
        meals = []
        meals_ref = db.collection(f'{MealPlan.COLLECTION_NAME}/{plan_id}/meals')
        for meal_doc in meals_ref.order_by('day_of_week').order_by('meal_type').stream():
            meal_data = meal_doc.to_dict()
            meal_data['id'] = meal_doc.id
            meals.append(meal_data)
        
        plan['meals'] = meals
        return plan
    
    @staticmethod
    def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all meal plans with optional filters."""
        db = FirebaseService.get_firestore()
        query = db.collection(MealPlan.COLLECTION_NAME)
        
        # Apply filters
        if filters:
            if 'patient_id' in filters:
                query = query.where('patient_id', '==', filters['patient_id'])
            if 'status' in filters:
                query = query.where('status', '==', filters['status'])
            if 'generated_by_uid' in filters:
                query = query.where('generated_by_uid', '==', filters['generated_by_uid'])
        
        # Order by created_at desc
        query = query.order_by('created_at', direction='DESCENDING')
        
        plans = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            plans.append(data)
        
        return plans
    
    @staticmethod
    def update(plan_id: str, data: Dict[str, Any]) -> bool:
        """Update meal plan data."""
        db = FirebaseService.get_firestore()
        
        # Add updated timestamp
        data['updated_at'] = datetime.utcnow()
        
        try:
            db.collection(MealPlan.COLLECTION_NAME).document(plan_id).update(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete(plan_id: str) -> bool:
        """Delete meal plan."""
        db = FirebaseService.get_firestore()
        
        try:
            # Delete all meals first
            meals_ref = db.collection(f'{MealPlan.COLLECTION_NAME}/{plan_id}/meals')
            for meal_doc in meals_ref.stream():
                meal_doc.reference.delete()
            
            # Delete the plan
            db.collection(MealPlan.COLLECTION_NAME).document(plan_id).delete()
            return True
        except Exception:
            return False
    
    @staticmethod
    def add_meals(plan_id: str, meals: List[Dict[str, Any]]) -> bool:
        """Add meals to meal plan as subcollection."""
        db = FirebaseService.get_firestore()
        
        try:
            # Clear existing meals
            meals_ref = db.collection(f'{MealPlan.COLLECTION_NAME}/{plan_id}/meals')
            for doc in meals_ref.stream():
                doc.reference.delete()
            
            # Add new meals
            for meal in meals:
                meals_ref.add(meal)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def approve_plan(plan_id: str, approved_by_uid: str) -> bool:
        """Approve meal plan."""
        update_data = {
            'status': 'approved',
            'approved_by_uid': approved_by_uid,
            'approved_at': datetime.utcnow()
        }
        return MealPlan.update(plan_id, update_data)
    
    @staticmethod
    def get_by_patient_token(token: str) -> Optional[Dict[str, Any]]:
        """Get the latest approved meal plan for a patient using their invitation token."""
        from .patient_invitation import PatientInvitation
        from .patient import Patient
        
        # Get invitation
        invitation = PatientInvitation.get_by_token(token)
        if not invitation:
            return None
        
        # Get patient
        patient = Patient.get_by_invitation_id(invitation['id'])
        if not patient:
            return None
        
        # Get latest approved meal plan
        db = FirebaseService.get_firestore()
        plans = db.collection(MealPlan.COLLECTION_NAME)\
                 .where('patient_id', '==', patient['id'])\
                 .where('status', '==', 'approved')\
                 .order_by('created_at', direction='DESCENDING')\
                 .limit(1)\
                 .stream()
        
        for plan_doc in plans:
            plan = plan_doc.to_dict()
            plan['id'] = plan_doc.id
            
            # Get meals
            meals = []
            plan_id = plan['id']
            meals_ref = db.collection(f'{MealPlan.COLLECTION_NAME}/{plan_id}/meals')
            for meal_doc in meals_ref.order_by('day_of_week').order_by('meal_type').stream():
                meal_data = meal_doc.to_dict()
                meal_data['id'] = meal_doc.id
                meals.append(meal_data)
            
            plan['meals'] = meals
            plan['patient'] = patient
            return plan
        
        return None
    
    @staticmethod
    def get_weekly_calendar(plan_id: str) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Get meal plan organized by day and meal type."""
        plan = MealPlan.get_by_id(plan_id)
        if not plan:
            return {}
        
        # Initialize calendar structure
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        calendar = {}
        for day in days:
            calendar[day] = {}
            for meal_type in meal_types:
                calendar[day][meal_type] = []
        
        # Organize meals
        for meal in plan.get('meals', []):
            day = meal.get('day_of_week')
            meal_type = meal.get('meal_type')
            
            if day in calendar and meal_type in calendar[day]:
                calendar[day][meal_type].append(meal)
        
        return calendar
