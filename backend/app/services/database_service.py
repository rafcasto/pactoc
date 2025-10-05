"""
Database service for PostgreSQL connection using SQLAlchemy.
"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Initialize SQLAlchemy instance
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app."""
    # Database configuration
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///pactoc_dev.db')
    
    # Fix for PostgreSQL URL format (some providers use postgres:// instead of postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Initialize with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    return db

def get_db():
    """Get database instance."""
    return db

def create_tables():
    """Create all database tables."""
    try:
        # Import all models to register them
        from app.models.sql_models import (
            PatientInvitation, Patient, MedicalCondition, FoodIntolerance, 
            DietaryPreference, PatientMedicalCondition, PatientIntolerance, 
            PatientDietaryPreference, Ingredient, RecipeTag, Recipe, 
            RecipeIngredient, RecipeTagAssignment, MealPlan, MealPlanMeal, MealPlanToken
        )
        
        db.create_all()
        print("✅ All database tables created successfully")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_connection():
    """Test database connection."""
    try:
        # Test connection with SQLAlchemy 2.0 syntax
        with db.engine.connect() as connection:
            result = connection.execute(text('SELECT 1'))
            result.fetchone()
        print("✅ Database connection successful")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing connection: {e}")
        return False
