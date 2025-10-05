"""
SQLAlchemy models for the meal planning system.
"""
from datetime import datetime, timedelta
import secrets
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Date, Enum, DECIMAL, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.services.database_service import db

# Base model with common fields
class BaseModel(db.Model):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Patient Invitations
class PatientInvitation(BaseModel):
    __tablename__ = 'patient_invitations'
    
    token = Column(String(64), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    invited_by_uid = Column(String(255), nullable=False)  # Firebase UID
    status = Column(Enum('pending', 'completed', 'expired', name='invitation_status'), default='pending')
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    @property
    def is_valid(self):
        return (self.status == 'pending' and 
                self.expires_at > datetime.utcnow())
    
    def regenerate_token(self):
        """Generate a new token for the invitation and extend expiry."""
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(days=7)
        self.status = 'pending'
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'invited_by_uid': self.invited_by_uid,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Patients
class Patient(BaseModel):
    __tablename__ = 'patients'
    
    invitation_id = Column(Integer, ForeignKey('patient_invitations.id'), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum('male', 'female', 'other', name='gender_type'), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    profile_status = Column(Enum('pending_review', 'approved', name='profile_status'), default='pending_review')
    additional_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    invitation = relationship("PatientInvitation", backref="patient")
    medical_conditions = relationship("PatientMedicalCondition", back_populates="patient", cascade="all, delete-orphan")
    intolerances = relationship("PatientIntolerance", back_populates="patient", cascade="all, delete-orphan")
    dietary_preferences = relationship("PatientDietaryPreference", back_populates="patient", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="patient", cascade="all, delete-orphan")
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'invitation_id': self.invitation_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'profile_status': self.profile_status,
            'additional_notes': self.additional_notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_relations:
            data.update({
                'conditions_count': len(self.medical_conditions),
                'intolerances_count': len(self.intolerances),
                'preferences_count': len(self.dietary_preferences),
                'medical_conditions': [mc.to_dict() for mc in self.medical_conditions],
                'intolerances': [i.to_dict() for i in self.intolerances],
                'dietary_preferences': [dp.to_dict() for dp in self.dietary_preferences]
            })
        
        return data

# Medical Conditions Catalog
class MedicalCondition(BaseModel):
    __tablename__ = 'medical_conditions'
    
    condition_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    severity_level = Column(Enum('low', 'medium', 'high', 'critical', name='severity_level'), default='medium')
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'condition_name': self.condition_name,
            'description': self.description,
            'severity_level': self.severity_level,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Food Intolerances Catalog
class FoodIntolerance(BaseModel):
    __tablename__ = 'food_intolerances'
    
    intolerance_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'intolerance_name': self.intolerance_name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Dietary Preferences Catalog
class DietaryPreference(BaseModel):
    __tablename__ = 'dietary_preferences'
    
    preference_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'preference_name': self.preference_name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Patient Medical Conditions (Many-to-Many)
class PatientMedicalCondition(BaseModel):
    __tablename__ = 'patient_medical_conditions'
    
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    condition_id = Column(Integer, ForeignKey('medical_conditions.id'), nullable=False)
    notes = Column(Text)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_conditions")
    condition = relationship("MedicalCondition")
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'condition_id': self.condition_id,
            'condition_name': self.condition.condition_name if self.condition else None,
            'notes': self.notes,
            'added_at': self.created_at.isoformat()
        }

# Patient Intolerances (Many-to-Many)
class PatientIntolerance(BaseModel):
    __tablename__ = 'patient_intolerances'
    
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    intolerance_id = Column(Integer, ForeignKey('food_intolerances.id'), nullable=False)
    severity = Column(Enum('mild', 'moderate', 'severe', name='intolerance_severity'), default='mild')
    notes = Column(Text)
    
    # Relationships
    patient = relationship("Patient", back_populates="intolerances")
    intolerance = relationship("FoodIntolerance")
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'intolerance_id': self.intolerance_id,
            'intolerance_name': self.intolerance.intolerance_name if self.intolerance else None,
            'severity': self.severity,
            'notes': self.notes,
            'added_at': self.created_at.isoformat()
        }

# Patient Dietary Preferences (Many-to-Many)
class PatientDietaryPreference(BaseModel):
    __tablename__ = 'patient_dietary_preferences'
    
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    preference_id = Column(Integer, ForeignKey('dietary_preferences.id'), nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="dietary_preferences")
    preference = relationship("DietaryPreference")
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'preference_id': self.preference_id,
            'preference_name': self.preference.preference_name if self.preference else None,
            'added_at': self.created_at.isoformat()
        }

# Ingredients Catalog
class Ingredient(BaseModel):
    __tablename__ = 'ingredients'
    
    ingredient_name = Column(String(200), nullable=False, unique=True)
    category = Column(String(100))
    calories_per_100g = Column(DECIMAL(6,2))
    protein_per_100g = Column(DECIMAL(5,2))
    carbs_per_100g = Column(DECIMAL(5,2))
    fat_per_100g = Column(DECIMAL(5,2))
    fiber_per_100g = Column(DECIMAL(5,2))
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ingredient_name': self.ingredient_name,
            'category': self.category,
            'calories_per_100g': float(self.calories_per_100g) if self.calories_per_100g else None,
            'protein_per_100g': float(self.protein_per_100g) if self.protein_per_100g else None,
            'carbs_per_100g': float(self.carbs_per_100g) if self.carbs_per_100g else None,
            'fat_per_100g': float(self.fat_per_100g) if self.fat_per_100g else None,
            'fiber_per_100g': float(self.fiber_per_100g) if self.fiber_per_100g else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Recipe Tags Catalog
class RecipeTag(BaseModel):
    __tablename__ = 'recipe_tags'
    
    tag_name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), default='#3b82f6')  # Hex color
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_name': self.tag_name,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

# Recipes
class Recipe(BaseModel):
    __tablename__ = 'recipes'
    
    recipe_name = Column(String(200), nullable=False)
    description = Column(Text)
    meal_type = Column(Enum('breakfast', 'lunch', 'dinner', 'snack', name='meal_type'), nullable=False)
    preparation_time = Column(Integer)  # minutes
    cooking_time = Column(Integer)  # minutes
    servings = Column(Integer, default=1)
    difficulty_level = Column(Enum('easy', 'medium', 'hard', name='difficulty_level'), default='easy')
    total_calories = Column(DECIMAL(7,2))
    total_protein = Column(DECIMAL(6,2))
    total_carbs = Column(DECIMAL(6,2))
    total_fat = Column(DECIMAL(6,2))
    total_fiber = Column(DECIMAL(6,2))
    instructions = Column(Text)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_by_uid = Column(String(255))  # Firebase UID
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    tag_assignments = relationship("RecipeTagAssignment", back_populates="recipe", cascade="all, delete-orphan")
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'recipe_name': self.recipe_name,
            'description': self.description,
            'meal_type': self.meal_type,
            'preparation_time': self.preparation_time,
            'cooking_time': self.cooking_time,
            'servings': self.servings,
            'difficulty_level': self.difficulty_level,
            'total_calories': float(self.total_calories) if self.total_calories else None,
            'total_protein': float(self.total_protein) if self.total_protein else None,
            'total_carbs': float(self.total_carbs) if self.total_carbs else None,
            'total_fat': float(self.total_fat) if self.total_fat else None,
            'total_fiber': float(self.total_fiber) if self.total_fiber else None,
            'instructions': self.instructions,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'created_by_uid': self.created_by_uid,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_relations:
            data.update({
                'ingredients': [ri.to_dict() for ri in self.ingredients],
                'tags': [ta.tag.tag_name for ta in self.tag_assignments if ta.tag]
            })
        
        return data

# Recipe Ingredients (Many-to-Many)
class RecipeIngredient(BaseModel):
    __tablename__ = 'recipe_ingredients'
    
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity = Column(DECIMAL(8,2), nullable=False)
    unit = Column(String(50), nullable=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")
    
    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.ingredient_name if self.ingredient else None,
            'quantity': float(self.quantity),
            'unit': self.unit,
            'calories_per_100g': float(self.ingredient.calories_per_100g) if self.ingredient and self.ingredient.calories_per_100g else None,
            'protein_per_100g': float(self.ingredient.protein_per_100g) if self.ingredient and self.ingredient.protein_per_100g else None,
            'carbs_per_100g': float(self.ingredient.carbs_per_100g) if self.ingredient and self.ingredient.carbs_per_100g else None,
            'fat_per_100g': float(self.ingredient.fat_per_100g) if self.ingredient and self.ingredient.fat_per_100g else None,
            'fiber_per_100g': float(self.ingredient.fiber_per_100g) if self.ingredient and self.ingredient.fiber_per_100g else None
        }

# Recipe Tag Assignments (Many-to-Many)
class RecipeTagAssignment(BaseModel):
    __tablename__ = 'recipe_tag_assignments'
    
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('recipe_tags.id'), nullable=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="tag_assignments")
    tag = relationship("RecipeTag")

# Meal Plans
class MealPlan(BaseModel):
    __tablename__ = 'meal_plans'
    
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    plan_name = Column(String(200))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Enum('draft', 'approved', 'sent', name='meal_plan_status'), default='draft')
    notes = Column(Text)
    generated_by_uid = Column(String(255), nullable=False)  # Firebase UID
    approved_by_uid = Column(String(255))  # Firebase UID
    approved_at = Column(DateTime)
    
    # Relationships
    patient = relationship("Patient", back_populates="meal_plans")
    meals = relationship("MealPlanMeal", back_populates="meal_plan", cascade="all, delete-orphan")
    
    def to_dict(self, include_relations=False):
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'plan_name': self.plan_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'notes': self.notes,
            'generated_by_uid': self.generated_by_uid,
            'approved_by_uid': self.approved_by_uid,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_relations:
            data['meals'] = [meal.to_dict() for meal in self.meals]
        
        return data

# Meal Plan Tokens
class MealPlanToken(BaseModel):
    __tablename__ = 'meal_plan_tokens'
    
    plan_id = Column(Integer, ForeignKey('meal_plans.id'), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime)  # NULL = never expires
    
    # Relationships
    meal_plan = relationship("MealPlan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = secrets.token_urlsafe(32)
    
    @property
    def is_valid(self):
        if self.expires_at is None:
            return True  # Never expires
        return self.expires_at > datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }

# Meal Plan Meals
class MealPlanMeal(BaseModel):
    __tablename__ = 'meal_plan_meals'
    
    plan_id = Column(Integer, ForeignKey('meal_plans.id'), nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    day_of_week = Column(Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', name='day_of_week'), nullable=False)
    meal_type = Column(Enum('breakfast', 'lunch', 'dinner', 'snack', name='meal_type'), nullable=False)
    scheduled_time = Column(Time)
    servings = Column(DECIMAL(3,1), default=1.0)
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="meals")
    recipe = relationship("Recipe")
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'recipe_id': self.recipe_id,
            'recipe_name': self.recipe.recipe_name if self.recipe else None,
            'day_of_week': self.day_of_week,
            'meal_type': self.meal_type,
            'scheduled_time': self.scheduled_time.strftime('%H:%M') if self.scheduled_time else None,
            'servings': float(self.servings),
            'calories_per_serving': float(self.recipe.total_calories) if self.recipe and self.recipe.total_calories else None
        }
