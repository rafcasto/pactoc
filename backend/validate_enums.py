#!/usr/bin/env python3
"""
Enum Validation Script - Ensures all enum values are consistent across the system.
Run this after any database changes or when experiencing enum errors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.services.database_service import db
from sqlalchemy import text

def validate_profile_status_enum():
    """Validate profile_status enum consistency."""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 PROFILE STATUS ENUM VALIDATION")
        print("=" * 50)
        
        try:
            # 1. Check enum definition
            print("\n1. Checking enum definition...")
            result = db.session.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'profile_status'
                )
                ORDER BY enumsortorder;
            """))
            
            valid_values = []
            for row in result.fetchall():
                valid_values.append(row[0])
                print(f"   ✅ '{row[0]}'")
            
            expected_values = ['pending_review', 'approved']
            if set(valid_values) == set(expected_values):
                print("   ✅ Enum definition is correct!")
            else:
                print(f"   ❌ Expected: {expected_values}")
                print(f"   ❌ Found: {valid_values}")
                return False
            
            # 2. Check actual data
            print("\n2. Checking patient data...")
            result = db.session.execute(text("""
                SELECT DISTINCT profile_status, COUNT(*) 
                FROM patients 
                GROUP BY profile_status;
            """))
            
            data_found = False
            for row in result.fetchall():
                data_found = True
                status, count = row[0], row[1]
                if status in valid_values:
                    print(f"   ✅ '{status}': {count} patients")
                else:
                    print(f"   ❌ INVALID '{status}': {count} patients")
                    return False
            
            if not data_found:
                print("   ℹ️  No patient data found (empty table)")
            
            # 3. Check for NULL values
            print("\n3. Checking for NULL values...")
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM patients WHERE profile_status IS NULL;
            """))
            null_count = result.fetchone()[0]
            
            if null_count > 0:
                print(f"   ❌ Found {null_count} patients with NULL status")
                return False
            else:
                print("   ✅ No NULL values found")
            
            print("\n🎉 VALIDATION PASSED - All enum values are consistent!")
            return True
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False

def fix_invalid_statuses():
    """Fix any invalid status values found."""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔧 FIXING INVALID STATUS VALUES")
        print("=" * 50)
        
        try:
            # Find invalid statuses
            result = db.session.execute(text("""
                SELECT id, first_name, last_name, profile_status 
                FROM patients 
                WHERE profile_status NOT IN ('pending_review', 'approved') 
                   OR profile_status IS NULL;
            """))
            
            invalid_patients = result.fetchall()
            
            if not invalid_patients:
                print("✅ No invalid statuses found!")
                return True
            
            print(f"Found {len(invalid_patients)} patients with invalid status:")
            
            for patient in invalid_patients:
                patient_id, first_name, last_name, current_status = patient
                print(f"  - Patient {patient_id}: {first_name} {last_name} (Status: {current_status})")
            
            # Ask for confirmation
            response = input("\nDo you want to fix these by setting status to 'pending_review'? (y/N): ")
            
            if response.lower() == 'y':
                # Update invalid statuses
                db.session.execute(text("""
                    UPDATE patients 
                    SET profile_status = 'pending_review', 
                        updated_at = NOW()
                    WHERE profile_status NOT IN ('pending_review', 'approved') 
                       OR profile_status IS NULL;
                """))
                
                db.session.commit()
                print(f"✅ Fixed {len(invalid_patients)} patient records!")
                return True
            else:
                print("❌ No changes made.")
                return False
                
        except Exception as e:
            print(f"❌ Error fixing statuses: {e}")
            db.session.rollback()
            return False

def validate_other_enums():
    """Validate other enums in the system."""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔍 OTHER ENUM VALIDATION")
        print("=" * 50)
        
        enums_to_check = [
            ('invitation_status', ['pending', 'completed', 'expired']),
            ('gender_type', ['male', 'female', 'other']),
            ('meal_plan_status', ['draft', 'approved', 'sent']),
            ('severity_level', ['low', 'medium', 'high', 'critical']),
            ('intolerance_severity', ['mild', 'moderate', 'severe']),
            ('meal_type', ['breakfast', 'lunch', 'dinner', 'snack']),
            ('difficulty_level', ['easy', 'medium', 'hard']),
            ('day_of_week', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        ]
        
        all_valid = True
        
        for enum_name, expected_values in enums_to_check:
            try:
                result = db.session.execute(text(f"""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = '{enum_name}'
                    )
                    ORDER BY enumsortorder;
                """))
                
                actual_values = [row[0] for row in result.fetchall()]
                
                if set(actual_values) == set(expected_values):
                    print(f"   ✅ {enum_name}: OK")
                else:
                    print(f"   ❌ {enum_name}: Expected {expected_values}, Got {actual_values}")
                    all_valid = False
                    
            except Exception as e:
                print(f"   ❌ {enum_name}: Error checking - {e}")
                all_valid = False
        
        return all_valid

if __name__ == "__main__":
    print("🚀 PACTOC ENUM VALIDATION TOOL")
    print("=" * 50)
    
    # Run validations
    status_valid = validate_profile_status_enum()
    
    if not status_valid:
        print("\n❌ Profile status validation failed!")
        fix_result = fix_invalid_statuses()
        if fix_result:
            # Re-validate after fixing
            status_valid = validate_profile_status_enum()
    
    other_enums_valid = validate_other_enums()
    
    print("\n" + "=" * 50 + "\n")
    
    if status_valid and other_enums_valid:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("Your database enums are consistent and ready to use.")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED!")
        print("Please review and fix the issues above.")
        sys.exit(1)
