#!/usr/bin/env python3
"""
Emergency enum fix script - Run this to fix the ready_for_review error immediately.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def emergency_enum_fix():
    """Emergency fix for the ready_for_review enum error."""
    
    print("🚨 EMERGENCY ENUM FIX")
    print("=" * 40)
    
    try:
        from app import create_app
        from app.services.database_service import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("1. Checking current enum state...")
            
            # Check enum definition
            result = db.session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            current_values = [row[0] for row in result.fetchall()]
            print(f"Current enum values: {current_values}")
            
            # Check if ready_for_review exists
            if 'ready_for_review' in current_values:
                print("✅ ready_for_review found in enum - this is the issue!")
                print("2. Removing ready_for_review from enum...")
                
                # First update any data using ready_for_review
                db.session.execute(text("""
                    UPDATE patients 
                    SET profile_status = 'pending_review' 
                    WHERE profile_status = 'ready_for_review';
                """))
                
                # Remove the invalid enum value
                db.session.execute(text("DROP TYPE profile_status CASCADE;"))
                db.session.execute(text("CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');"))
                
                # Restore the column
                db.session.execute(text("""
                    ALTER TABLE patients 
                    ADD COLUMN profile_status profile_status DEFAULT 'pending_review';
                """))
                
                db.session.commit()
                print("✅ Fixed: ready_for_review removed from enum")
                
            elif 'pending_review' not in current_values:
                print("❌ Missing pending_review - recreating enum...")
                
                # Recreate proper enum
                db.session.execute(text("DROP TYPE IF EXISTS profile_status CASCADE;"))
                db.session.execute(text("CREATE TYPE profile_status AS ENUM ('pending_review', 'approved');"))
                
                # Restore the column
                db.session.execute(text("""
                    ALTER TABLE patients 
                    ADD COLUMN profile_status profile_status DEFAULT 'pending_review';
                """))
                
                db.session.commit()
                print("✅ Enum recreated with correct values")
                
            else:
                print("✅ Enum looks correct")
            
            print("\n3. Verifying fix...")
            result = db.session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            final_values = [row[0] for row in result.fetchall()]
            print(f"Final enum values: {final_values}")
            
            if set(final_values) == {'pending_review', 'approved'}:
                print("\n🎉 ENUM FIXED SUCCESSFULLY!")
                print("You can now run your application without the ready_for_review error.")
                return True
            else:
                print(f"\n❌ Still have issues. Expected ['pending_review', 'approved'], got {final_values}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        return False

if __name__ == "__main__":
    success = emergency_enum_fix()
    
    if success:
        print("\n🚀 READY TO RUN!")
        print("Your application should now work without enum errors.")
        print("Run: ./start_dev.sh")
    else:
        print("\n💔 MANUAL INTERVENTION NEEDED")
        print("Please check the database and enum definitions manually.")
    
    sys.exit(0 if success else 1)
