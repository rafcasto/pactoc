#!/usr/bin/env python3
"""
Test script for profile status enum handling.
This tests the actual workflow to ensure no enum errors occur.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.services.database_service import db
from app.models.sql_models import PatientInvitation, Patient
from app.services.meal_plan_workflow_service import MealPlanWorkflowService
from datetime import datetime, timedelta

def test_workflow_enum_handling():
    """Test the complete workflow to ensure enum values work correctly."""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING PROFILE STATUS ENUM HANDLING")
        print("=" * 50)
        
        try:
            # Clean up any existing test data
            print("1. Cleaning up test data...")
            test_email = "test.enum@pactoc.com"
            existing_invitation = PatientInvitation.query.filter_by(email=test_email).first()
            if existing_invitation:
                if existing_invitation.patient:
                    db.session.delete(existing_invitation.patient)
                db.session.delete(existing_invitation)
                db.session.commit()
            print("   ✅ Test data cleaned")
            
            # Test 1: Create workflow invitation
            print("\n2. Creating workflow invitation...")
            success, invitation_data, error = MealPlanWorkflowService.create_workflow_invitation(
                email=test_email,
                patient_name="Test User",
                invited_by_uid="test_nutritionist_123"
            )
            
            if not success:
                print(f"   ❌ Failed to create invitation: {error}")
                return False
            
            token = invitation_data['token']
            print(f"   ✅ Invitation created with token: {token[:20]}...")
            
            # Test 2: Submit patient form
            print("\n3. Testing patient form submission...")
            form_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'date_of_birth': '1990-01-15',
                'gender': 'male',
                'email': test_email,
                'phone': '+503 7777-1234',
                'medical_conditions': [],
                'intolerances': [],
                'dietary_preferences': [],
                'additional_notes': 'Test patient for enum validation'
            }
            
            success, result, error = MealPlanWorkflowService.submit_patient_form(token, form_data)
            
            if not success:
                print(f"   ❌ Failed to submit form: {error}")
                return False
            
            patient_id = result['patient_id']
            print(f"   ✅ Patient created with ID: {patient_id}")
            
            # Test 3: Verify patient status
            print("\n4. Verifying patient status...")
            patient = Patient.query.get(patient_id)
            
            if not patient:
                print("   ❌ Patient not found in database")
                return False
            
            print(f"   ✅ Patient status: '{patient.profile_status}'")
            
            if patient.profile_status not in ['pending_review', 'approved']:
                print(f"   ❌ Invalid status value: '{patient.profile_status}'")
                return False
            
            # Test 4: Get dynamic link content
            print("\n5. Testing dynamic link content...")
            success, content_data, error = MealPlanWorkflowService.get_dynamic_link_content(token)
            
            if not success:
                print(f"   ❌ Failed to get dynamic content: {error}")
                return False
            
            print(f"   ✅ Content type: {content_data['content_type']}")
            print(f"   ✅ Status: {content_data['status']}")
            
            # Test 5: Clean up
            print("\n6. Cleaning up test data...")
            db.session.delete(patient)
            invitation = PatientInvitation.query.filter_by(email=test_email).first()
            if invitation:
                db.session.delete(invitation)
            db.session.commit()
            print("   ✅ Test data cleaned up")
            
            print("\n🎉 ALL ENUM TESTS PASSED!")
            print("The workflow correctly handles profile status enums.")
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            
            # Clean up on error
            try:
                db.session.rollback()
                test_invitation = PatientInvitation.query.filter_by(email=test_email).first()
                if test_invitation:
                    if test_invitation.patient:
                        db.session.delete(test_invitation.patient)
                    db.session.delete(test_invitation)
                    db.session.commit()
            except:
                pass
            
            return False

if __name__ == "__main__":
    success = test_workflow_enum_handling()
    sys.exit(0 if success else 1)
