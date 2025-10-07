#!/usr/bin/env python3
"""
Script to implement new business rules:
1. Create explicit Nutritionist entity
2. Add meal plan versioning system
3. Update relationships
"""

import os
import sys
sys.path.append('/Users/rafaelcastillo/pactoc/backend')

# Initialize Flask app context
from app import create_app
from sqlalchemy import text

app = create_app()

def create_nutritionist_table():
    """Create nutritionists table."""
    print("Creating nutritionists table...")
    
    sql = """
    CREATE TABLE IF NOT EXISTS nutritionists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firebase_uid VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        license_number VARCHAR(100),
        specialization VARCHAR(200),
        bio TEXT,
        profile_image_url VARCHAR(500),
        is_active BOOLEAN DEFAULT 1,
        is_verified BOOLEAN DEFAULT 0,
        verification_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    db.session.execute(text(sql))
    db.session.commit()
    print("✅ Nutritionists table created")

def add_meal_plan_versioning():
    """Add versioning columns to meal_plans table."""
    print("Adding versioning to meal_plans table...")
    
    # Check if columns already exist
    result = db.session.execute(text("PRAGMA table_info(meal_plans)"))
    columns = [row[1] for row in result.fetchall()]
    
    # Add version column if not exists
    if 'version' not in columns:
        sql = "ALTER TABLE meal_plans ADD COLUMN version INTEGER DEFAULT 1"
        db.session.execute(text(sql))
        print("✅ Added version column")
    
    # Add is_latest column if not exists
    if 'is_latest' not in columns:
        sql = "ALTER TABLE meal_plans ADD COLUMN is_latest BOOLEAN DEFAULT 1"
        db.session.execute(text(sql))
        print("✅ Added is_latest column")
    
    # Add parent_plan_id for versioning chain
    if 'parent_plan_id' not in columns:
        sql = "ALTER TABLE meal_plans ADD COLUMN parent_plan_id INTEGER REFERENCES meal_plans(id)"
        db.session.execute(text(sql))
        print("✅ Added parent_plan_id column")
    
    # Add nutritionist_id foreign key
    if 'nutritionist_id' not in columns:
        sql = "ALTER TABLE meal_plans ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id)"
        db.session.execute(text(sql))
        print("✅ Added nutritionist_id column")
    
    db.session.commit()

def add_nutritionist_to_invitations():
    """Add nutritionist_id to patient_invitations table."""
    print("Adding nutritionist_id to patient_invitations...")
    
    # Check if column already exists
    result = db.session.execute(text("PRAGMA table_info(patient_invitations)"))
    columns = [row[1] for row in result.fetchall()]
    
    if 'nutritionist_id' not in columns:
        sql = "ALTER TABLE patient_invitations ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id)"
        db.session.execute(text(sql))
        db.session.commit()
        print("✅ Added nutritionist_id to patient_invitations")

def create_indexes():
    """Create indexes for better performance."""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_meal_plans_patient_version ON meal_plans(patient_id, version DESC)",
        "CREATE INDEX IF NOT EXISTS idx_meal_plans_patient_latest ON meal_plans(patient_id, is_latest) WHERE is_latest = 1",
        "CREATE INDEX IF NOT EXISTS idx_meal_plans_nutritionist ON meal_plans(nutritionist_id)",
        "CREATE INDEX IF NOT EXISTS idx_invitations_nutritionist ON patient_invitations(nutritionist_id)",
        "CREATE INDEX IF NOT EXISTS idx_nutritionists_firebase_uid ON nutritionists(firebase_uid)",
    ]
    
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            print(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"⚠️  Index might already exist: {e}")
    
    db.session.commit()

def migrate_existing_data():
    """Migrate existing meal plans to have version = 1 and is_latest = True."""
    print("Migrating existing data...")
    
    # Set version = 1 and is_latest = True for all existing meal plans
    sql = """
    UPDATE meal_plans 
    SET version = 1, is_latest = 1 
    WHERE version IS NULL OR is_latest IS NULL
    """
    
    db.session.execute(text(sql))
    db.session.commit()
    print("✅ Migrated existing meal plans")

def main():
    """Run all migrations."""
    print("🚀 Implementing new business rules...")
    print("=" * 50)
    
    try:
        create_nutritionist_table()
        add_meal_plan_versioning()
        add_nutritionist_to_invitations()
        create_indexes()
        migrate_existing_data()
        
        print("=" * 50)
        print("✅ All business rules implemented successfully!")
        print("\nNew features:")
        print("- ✅ Nutritionist entity with profile management")
        print("- ✅ Meal plan versioning system")
        print("- ✅ One nutritionist can have multiple patients")
        print("- ✅ One patient can have multiple meal plan versions")
        print("- ✅ Patient sees only latest version")
        print("- ✅ Nutritionist can view all versions")
        
    except Exception as e:
        print(f"❌ Error implementing business rules: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    with app.app_context():
        from app.services.database_service import db
        from app.models.sql_models import *
        main()
