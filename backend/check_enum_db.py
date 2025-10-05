#!/usr/bin/env python3
"""
Quick database check to see what enum values are actually stored.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.services.database_service import db
from sqlalchemy import text

def check_enum_values():
    """Check what enum values are actually in the database."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Checking enum values in database...")
            
            # Check what profile_status values exist in patients table
            result = db.session.execute(text("""
                SELECT DISTINCT profile_status 
                FROM patients 
                ORDER BY profile_status;
            """))
            
            print("Current profile_status values in database:")
            for row in result.fetchall():
                print(f"  - '{row[0]}'")
            
            # Check the actual enum definition
            result = db.session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            print("\nDefined enum values:")
            for row in result.fetchall():
                print(f"  - '{row[0]}'")
            
            # Count patients by status
            result = db.session.execute(text("""
                SELECT profile_status, COUNT(*) 
                FROM patients 
                GROUP BY profile_status;
            """))
            
            print("\nPatient count by status:")
            for row in result.fetchall():
                print(f"  - '{row[0]}': {row[1]} patients")
            
        except Exception as e:
            print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_enum_values()
