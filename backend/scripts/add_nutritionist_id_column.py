#!/usr/bin/env python3
"""
PostgreSQL Migration: Add nutritionist_id column to patient_invitations table
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app import create_app
from app.services.database_service import db

def add_nutritionist_id_column():
    """Add nutritionist_id column to patient_invitations table."""
    
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Check if column already exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'patient_invitations' 
                    AND column_name = 'nutritionist_id'
                """))
                
                if result.fetchone():
                    print("✅ nutritionist_id column already exists")
                    return True
                
                print("🔧 Adding nutritionist_id column to patient_invitations table...")
                
                # Add the column
                conn.execute(text("""
                    ALTER TABLE patient_invitations 
                    ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id)
                """))
                
                # Create index for performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_patient_invitations_nutritionist_id 
                    ON patient_invitations(nutritionist_id)
                """))
                
                # Update existing records - set nutritionist_id based on invited_by_uid
                # This assumes there's a mapping between Firebase UID and nutritionist records
                conn.execute(text("""
                    UPDATE patient_invitations 
                    SET nutritionist_id = (
                        SELECT id FROM nutritionists 
                        WHERE firebase_uid = patient_invitations.invited_by_uid
                        LIMIT 1
                    )
                    WHERE nutritionist_id IS NULL
                """))
                
                # Commit the transaction
                conn.commit()
                
                print("✅ Successfully added nutritionist_id column")
                print("✅ Created index on nutritionist_id")
                print("✅ Updated existing records with nutritionist_id")
                
                # Show final columns
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'patient_invitations'
                    ORDER BY ordinal_position
                """))
                
                print("\n📋 Final patient_invitations schema:")
                for row in result:
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    print(f"  - {row[0]} ({row[1]}) {nullable}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            return False

if __name__ == "__main__":
    success = add_nutritionist_id_column()
    sys.exit(0 if success else 1)
