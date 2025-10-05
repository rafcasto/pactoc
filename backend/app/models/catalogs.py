from datetime import datetime
from typing import Dict, List, Optional, Any
from ..services.firebase_service import FirebaseService

class Catalog:
    """Base catalog model for medical conditions, intolerances, dietary preferences, etc."""
    
    @staticmethod
    def get_all_from_collection(collection_name: str) -> List[Dict[str, Any]]:
        """Get all items from a catalog collection."""
        db = FirebaseService.get_firestore()
        items = []
        
        for doc in db.collection(collection_name).where('is_active', '==', True).stream():
            data = doc.to_dict()
            data['id'] = doc.id
            items.append(data)
        
        return items
    
    @staticmethod
    def create_item(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in a catalog collection."""
        db = FirebaseService.get_firestore()
        
        # Add timestamps and defaults
        data.update({
            'created_at': datetime.utcnow(),
            'is_active': True
        })
        
        # Create document with auto-generated ID
        doc_ref = db.collection(collection_name).document()
        doc_ref.set(data)
        
        # Return data with ID
        result = data.copy()
        result['id'] = doc_ref.id
        return result
    
    @staticmethod
    def update_item(collection_name: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Update item in catalog collection."""
        db = FirebaseService.get_firestore()
        
        try:
            db.collection(collection_name).document(item_id).update(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete_item(collection_name: str, item_id: str) -> bool:
        """Soft delete item (set is_active to False)."""
        return Catalog.update_item(collection_name, item_id, {'is_active': False})


class MedicalCondition:
    """Medical conditions catalog."""
    
    COLLECTION_NAME = 'medical_conditions'
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return Catalog.get_all_from_collection(MedicalCondition.COLLECTION_NAME)
    
    @staticmethod
    def create(name: str, description: str = None, severity_level: str = 'medium') -> Dict[str, Any]:
        data = {
            'condition_name': name,
            'description': description,
            'severity_level': severity_level
        }
        return Catalog.create_item(MedicalCondition.COLLECTION_NAME, data)
    
    @staticmethod
    def update(condition_id: str, data: Dict[str, Any]) -> bool:
        return Catalog.update_item(MedicalCondition.COLLECTION_NAME, condition_id, data)
    
    @staticmethod
    def delete(condition_id: str) -> bool:
        return Catalog.delete_item(MedicalCondition.COLLECTION_NAME, condition_id)


class FoodIntolerance:
    """Food intolerances catalog."""
    
    COLLECTION_NAME = 'food_intolerances'
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return Catalog.get_all_from_collection(FoodIntolerance.COLLECTION_NAME)
    
    @staticmethod
    def create(name: str, description: str = None) -> Dict[str, Any]:
        data = {
            'intolerance_name': name,
            'description': description
        }
        return Catalog.create_item(FoodIntolerance.COLLECTION_NAME, data)
    
    @staticmethod
    def update(intolerance_id: str, data: Dict[str, Any]) -> bool:
        return Catalog.update_item(FoodIntolerance.COLLECTION_NAME, intolerance_id, data)
    
    @staticmethod
    def delete(intolerance_id: str) -> bool:
        return Catalog.delete_item(FoodIntolerance.COLLECTION_NAME, intolerance_id)


class DietaryPreference:
    """Dietary preferences catalog."""
    
    COLLECTION_NAME = 'dietary_preferences'
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return Catalog.get_all_from_collection(DietaryPreference.COLLECTION_NAME)
    
    @staticmethod
    def create(name: str, description: str = None) -> Dict[str, Any]:
        data = {
            'preference_name': name,
            'description': description
        }
        return Catalog.create_item(DietaryPreference.COLLECTION_NAME, data)
    
    @staticmethod
    def update(preference_id: str, data: Dict[str, Any]) -> bool:
        return Catalog.update_item(DietaryPreference.COLLECTION_NAME, preference_id, data)
    
    @staticmethod
    def delete(preference_id: str) -> bool:
        return Catalog.delete_item(DietaryPreference.COLLECTION_NAME, preference_id)


class Ingredient:
    """Ingredients catalog."""
    
    COLLECTION_NAME = 'ingredients'
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return Catalog.get_all_from_collection(Ingredient.COLLECTION_NAME)
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        return Catalog.create_item(Ingredient.COLLECTION_NAME, data)
    
    @staticmethod
    def update(ingredient_id: str, data: Dict[str, Any]) -> bool:
        return Catalog.update_item(Ingredient.COLLECTION_NAME, ingredient_id, data)
    
    @staticmethod
    def delete(ingredient_id: str) -> bool:
        return Catalog.delete_item(Ingredient.COLLECTION_NAME, ingredient_id)
    
    @staticmethod
    def search_by_name(name: str) -> List[Dict[str, Any]]:
        """Search ingredients by name."""
        db = FirebaseService.get_firestore()
        ingredients = []
        
        # Simple search (Firestore doesn't have full-text search)
        for doc in db.collection(Ingredient.COLLECTION_NAME)\
                    .where('is_active', '==', True)\
                    .stream():
            data = doc.to_dict()
            data['id'] = doc.id
            
            if name.lower() in data.get('ingredient_name', '').lower():
                ingredients.append(data)
        
        return ingredients


class RecipeTag:
    """Recipe tags catalog."""
    
    COLLECTION_NAME = 'recipe_tags'
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return Catalog.get_all_from_collection(RecipeTag.COLLECTION_NAME)
    
    @staticmethod
    def create(name: str, color: str = '#3b82f6') -> Dict[str, Any]:
        data = {
            'tag_name': name,
            'color': color
        }
        return Catalog.create_item(RecipeTag.COLLECTION_NAME, data)
    
    @staticmethod
    def update(tag_id: str, data: Dict[str, Any]) -> bool:
        return Catalog.update_item(RecipeTag.COLLECTION_NAME, tag_id, data)
    
    @staticmethod
    def delete(tag_id: str) -> bool:
        return Catalog.delete_item(RecipeTag.COLLECTION_NAME, tag_id)
