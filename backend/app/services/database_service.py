"""
Database service for PostgreSQL connection using SQLAlchemy.
"""
import os
import time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from sqlalchemy import text

# Initialize SQLAlchemy instance
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app."""
    # Database configuration - PostgreSQL required
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required. Please set it to your PostgreSQL connection string.")
    
    # Fix for PostgreSQL URL format (some providers use postgres:// instead of postgresql://)
    # For pg8000, we need to use postgresql+pg8000:// scheme and handle SSL separately
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
    
    # Handle SSL mode for pg8000 - remove sslmode from URL and add to connect_args
    ssl_required = False
    if 'sslmode=require' in database_url:
        # Remove any sslmode parameter from the URL
        import re
        database_url = re.sub(r'[?&]sslmode=require', '', database_url)
        ssl_required = True
    
    # Configure SQLAlchemy with optimized settings
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Prepare connect_args based on SSL requirements
    connect_args = {
        'application_name': 'pactoc_app',  # Identify your app in database logs
    }
    
    # Add SSL settings if required (for pg8000, SSL is handled differently)
    if ssl_required:
        import ssl
        connect_args['ssl_context'] = ssl.create_default_context()  # Enable SSL for pg8000
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        # Connection pool settings
        'pool_size': 10,                    # Maintain 10 persistent connections
        'max_overflow': 20,                 # Allow up to 30 total connections
        'pool_pre_ping': True,              # Verify connections before use
        'pool_recycle': 3600,               # Recycle connections after 1 hour (instead of 5 min)
        
        # Connection timeout settings
        'connect_args': connect_args
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

def test_connection(retry_count=3, retry_delay=1):
    """Test database connection with retry logic."""
    for attempt in range(retry_count):
        try:
            start_time = time.time()
            # Test connection with SQLAlchemy 2.0 syntax
            with db.engine.connect() as connection:
                result = connection.execute(text('SELECT 1'))
                result.fetchone()
            
            connection_time = time.time() - start_time
            print(f"✅ Database connection successful in {connection_time:.3f}s")
            return True
            
        except (SQLAlchemyError, DisconnectionError) as e:
            if attempt < retry_count - 1:
                print(f"⚠️ Database connection attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"❌ Database connection failed after {retry_count} attempts: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error testing connection: {e}")
            return False
    
    return False
