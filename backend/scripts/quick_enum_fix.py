#!/usr/bin/env python3
"""
Quick enum fix script - Run this if you encounter any enum errors.
This script will automatically detect and fix common enum issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def quick_enum_fix():
    """Quick fix for common enum issues."""
    
    print("🔧 QUICK ENUM FIX TOOL")
    print("=" * 30)
    
    try:
        from app import create_app
        from app.services.database_service import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            # Check if profile_status enum exists and has correct values
            print("Checking profile_status enum...")
            
            result = db.session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            current_values = [row[0] for row in result.fetchall()]
            expected_values = ['pending_review', 'approved']
            
            if set(current_values) == set(expected_values):
                print("✅ profile_status enum is correct!")
            else:
                print(f"❌ Enum issue found. Current: {current_values}")
                print("🔧 Fixing enum...")
                
                # Recreate the enum with correct values
                db.session.execute(text("DROP TYPE IF EXISTS profile_status CASCADE;"))
                db.session.execute(text("CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');"))
                
                # Restore the column
                db.session.execute(text("""
                    ALTER TABLE patients 
                    ADD COLUMN profile_status profile_status DEFAULT 'pending_review';
                """))
                
                db.session.commit()
                print("✅ Enum fixed!")
            
            # Check for invalid data
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM patients 
                WHERE profile_status IS NULL 
                   OR profile_status NOT IN ('pending_review', 'approved');
            """))
            
            invalid_count = result.fetchone()[0]
            
            if invalid_count > 0:
                print(f"🔧 Fixing {invalid_count} invalid status values...")
                db.session.execute(text("""
                    UPDATE patients 
                    SET profile_status = 'pending_review' 
                    WHERE profile_status IS NULL 
                       OR profile_status NOT IN ('pending_review', 'approved');
                """))
                db.session.commit()
                print("✅ Invalid data fixed!")
            else:
                print("✅ No invalid data found!")
            
            print("\n🎉 ALL FIXES APPLIED SUCCESSFULLY!")
            return True
            
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = quick_enum_fix()
    
    if success:
        print("\n🚀 Your system is ready to use!")
        print("Try running the application again.")
    else:
        print("\n💡 If issues persist, check the full validation script:")
        print("./venv/bin/python validate_enums.py")
    
    sys.exit(0 if success else 1)
