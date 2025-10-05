#!/usr/bin/env python3
"""
Database migration to fix enum values for profile_status.
This script will update the enum type to ensure it has the correct values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database_service import db, init_db
from app import create_app
from sqlalchemy import text

def migrate_profile_status_enum():
    """Update the profile_status enum to have correct values."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Checking current enum values...")
            
            # Check current enum values
            result = db.session.execute(text("""
                SELECT enumtypid, enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            current_values = [row[1] for row in result.fetchall()]
            print(f"Current enum values: {current_values}")
            
            expected_values = ['pending_review', 'approved']
            
            if set(current_values) == set(expected_values):
                print("✅ Enum values are already correct!")
                return True
            
            print("🔧 Updating enum values...")
            
            # Drop and recreate the enum type
            db.session.execute(text("ALTER TABLE patients ALTER COLUMN profile_status DROP DEFAULT;"))
            db.session.execute(text("ALTER TABLE patients ALTER COLUMN profile_status TYPE varchar(50);"))
            db.session.execute(text("DROP TYPE IF EXISTS profile_status CASCADE;"))
            db.session.execute(text("CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');"))
            db.session.execute(text("ALTER TABLE patients ALTER COLUMN profile_status TYPE profile_status USING profile_status::profile_status;"))
            db.session.execute(text("ALTER TABLE patients ALTER COLUMN profile_status SET DEFAULT 'pending_review';"))
            
            db.session.commit()
            print("✅ Profile status enum updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating enum: {e}")
            db.session.rollback()
            return False

def migrate_invitation_status_enum():
    """Update the invitation_status enum to have correct values."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Checking invitation status enum values...")
            
            # Check current enum values
            result = db.session.execute(text("""
                SELECT enumtypid, enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'invitation_status'
                )
                ORDER BY enumsortorder;
            """))
            
            current_values = [row[1] for row in result.fetchall()]
            print(f"Current invitation enum values: {current_values}")
            
            expected_values = ['pending', 'completed', 'expired']
            
            if set(current_values) == set(expected_values):
                print("✅ Invitation enum values are already correct!")
                return True
            
            print("🔧 Updating invitation enum values...")
            
            # Drop and recreate the enum type
            db.session.execute(text("ALTER TABLE patient_invitations ALTER COLUMN status DROP DEFAULT;"))
            db.session.execute(text("ALTER TABLE patient_invitations ALTER COLUMN status TYPE varchar(50);"))
            db.session.execute(text("DROP TYPE IF EXISTS invitation_status CASCADE;"))
            db.session.execute(text("CREATE TYPE invitation_status AS ENUM ('pending', 'completed', 'expired');"))
            db.session.execute(text("ALTER TABLE patient_invitations ALTER COLUMN status TYPE invitation_status USING status::invitation_status;"))
            db.session.execute(text("ALTER TABLE patient_invitations ALTER COLUMN status SET DEFAULT 'pending';"))
            
            db.session.commit()
            print("✅ Invitation status enum updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating invitation enum: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔧 MEAL PLAN WORKFLOW - DATABASE MIGRATION")
    print("==========================================")
    
    success = True
    
    success &= migrate_profile_status_enum()
    success &= migrate_invitation_status_enum()
    
    if success:
        print("\n✅ All migrations completed successfully!")
        print("🚀 You can now start the application.")
    else:
        print("\n❌ Some migrations failed. Please check the errors above.")
        sys.exit(1)
