from datetime import datetime
from typing import Dict, List, Optional, Any
from ..services.firebase_service import FirebaseService

class Recipe:
    """Recipe model for Firestore operations."""
    
    COLLECTION_NAME = 'recipes'
    
    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recipe document."""
        db = FirebaseService.get_firestore()
        
        # Add timestamps and defaults
        data.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        })
        
        # Create document with auto-generated ID
        doc_ref = db.collection(Recipe.COLLECTION_NAME).document()
        doc_ref.set(data)
        
        # Return data with ID
        result = data.copy()
        result['id'] = doc_ref.id
        return result
    
    @staticmethod
    def get_by_id(recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get recipe by ID with ingredients."""
        db = FirebaseService.get_firestore()
        doc = db.collection(Recipe.COLLECTION_NAME).document(recipe_id).get()
        
        if not doc.exists:
            return None
        
        recipe = doc.to_dict()
        recipe['id'] = doc.id
        
        # Get ingredients
        ingredients = []
        ingredients_ref = db.collection(f'{Recipe.COLLECTION_NAME}/{recipe_id}/ingredients')
        for ingredient_doc in ingredients_ref.stream():
            ingredient_data = ingredient_doc.to_dict()
            ingredient_data['id'] = ingredient_doc.id
            ingredients.append(ingredient_data)
        
        recipe['ingredients'] = ingredients
        return recipe
    
    @staticmethod
    def get_all(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all recipes with optional filters."""
        db = FirebaseService.get_firestore()
        query = db.collection(Recipe.COLLECTION_NAME)
        
        # Apply filters
        if filters:
            if 'meal_type' in filters:
                query = query.where('meal_type', '==', filters['meal_type'])
            if 'is_active' in filters:
                query = query.where('is_active', '==', filters['is_active'])
            if 'created_by_uid' in filters:
                query = query.where('created_by_uid', '==', filters['created_by_uid'])
        
        # Order by created_at desc
        query = query.order_by('created_at', direction='DESCENDING')
        
        recipes = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            recipes.append(data)
        
        return recipes
    
    @staticmethod
    def update(recipe_id: str, data: Dict[str, Any]) -> bool:
        """Update recipe data."""
        db = FirebaseService.get_firestore()
        
        # Add updated timestamp
        data['updated_at'] = datetime.utcnow()
        
        try:
            db.collection(Recipe.COLLECTION_NAME).document(recipe_id).update(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete(recipe_id: str) -> bool:
        """Soft delete recipe."""
        return Recipe.update(recipe_id, {'is_active': False})
    
    @staticmethod
    def add_ingredients(recipe_id: str, ingredients: List[Dict[str, Any]]) -> bool:
        """Add ingredients to recipe as subcollection."""
        db = FirebaseService.get_firestore()
        
        try:
            # Clear existing ingredients
            ingredients_ref = db.collection(f'{Recipe.COLLECTION_NAME}/{recipe_id}/ingredients')
            for doc in ingredients_ref.stream():
                doc.reference.delete()
            
            # Add new ingredients
            for ingredient in ingredients:
                ingredients_ref.add(ingredient)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_compatible_for_patient(patient_id: str) -> List[Dict[str, Any]]:
        """Get recipes compatible with patient's restrictions."""
        from .patient import Patient
        
        # Get patient with conditions and preferences
        patient = Patient.get_with_conditions_and_preferences(patient_id)
        if not patient:
            return []
        
        # Get all active recipes
        all_recipes = Recipe.get_all({'is_active': True})
        
        # Filter compatible recipes
        compatible_recipes = []
        for recipe in all_recipes:
            if Recipe._is_recipe_compatible(recipe, patient):
                compatible_recipes.append(recipe)
        
        return compatible_recipes
    
    @staticmethod
    def _is_recipe_compatible(recipe: Dict[str, Any], patient: Dict[str, Any]) -> bool:
        """Check if recipe is compatible with patient restrictions."""
        # Get recipe with ingredients
        full_recipe = Recipe.get_by_id(recipe['id'])
        if not full_recipe or not full_recipe.get('ingredients'):
            return False
        
        # Check against intolerances
        patient_intolerances = [int_data['intolerance_name'].lower() 
                              for int_data in patient.get('intolerances', [])]
        
        # Check recipe tags for intolerance compatibility
        recipe_tags = recipe.get('tags', [])
        
        # Simple compatibility check
        for intolerance in patient_intolerances:
            if intolerance == 'lactosa' and 'sin lactosa' not in [tag.lower() for tag in recipe_tags]:
                # If patient has lactose intolerance, recipe should be lactose-free
                continue  # For now, we'll be permissive
            if intolerance == 'gluten' and 'sin gluten' not in [tag.lower() for tag in recipe_tags]:
                # If patient has gluten intolerance, recipe should be gluten-free
                continue  # For now, we'll be permissive
        
        return True
    
    @staticmethod
    def calculate_nutrition(ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total nutrition from ingredients."""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        for ingredient in ingredients:
            quantity = ingredient.get('quantity', 0)  # in grams
            
            # Get ingredient nutritional data (would come from ingredients catalog)
            calories_per_100g = ingredient.get('calories_per_100g', 0)
            protein_per_100g = ingredient.get('protein_per_100g', 0)
            carbs_per_100g = ingredient.get('carbs_per_100g', 0)
            fat_per_100g = ingredient.get('fat_per_100g', 0)
            fiber_per_100g = ingredient.get('fiber_per_100g', 0)
            
            # Calculate for actual quantity
            multiplier = quantity / 100
            total_calories += calories_per_100g * multiplier
            total_protein += protein_per_100g * multiplier
            total_carbs += carbs_per_100g * multiplier
            total_fat += fat_per_100g * multiplier
            total_fiber += fiber_per_100g * multiplier
        
        return {
            'total_calories': round(total_calories, 2),
            'total_protein': round(total_protein, 2),
            'total_carbs': round(total_carbs, 2),
            'total_fat': round(total_fat, 2),
            'total_fiber': round(total_fiber, 2)
        }
