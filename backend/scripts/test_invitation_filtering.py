#!/usr/bin/env python3
"""
Test script to verify invitation filtering is working correctly.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.database_service import init_db, db
from app.models.sql_models import Nutritionist, PatientInvitation
from app import create_app

def test_invitation_filtering():
    """Test that nutritionists only see their own invitations."""
    app = create_app()
    
    with app.app_context():
        
        print("🔍 Testing Invitation Filtering")
        print("=" * 50)
        
        # Get all nutritionists
        nutritionists = Nutritionist.query.all()
        print(f"Found {len(nutritionists)} nutritionists:")
        
        for nutritionist in nutritionists:
            print(f"\n🥗 Nutritionist: {nutritionist.first_name} {nutritionist.last_name}")
            print(f"   ID: {nutritionist.id}")
            print(f"   Firebase UID: {nutritionist.firebase_uid}")
            print(f"   Email: {nutritionist.email}")
            
            # Get their invitations
            invitations = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id).all()
            print(f"   📧 Invitations: {len(invitations)}")
            
            for inv in invitations:
                print(f"      - {inv.email} ({inv.status}) [ID: {inv.id}]")
        
        print("\n🔍 Testing Cross-Contamination")
        print("=" * 30)
        
        # Check if any invitations don't have nutritionist_id
        orphaned = PatientInvitation.query.filter_by(nutritionist_id=None).all()
        if orphaned:
            print(f"⚠️  Found {len(orphaned)} orphaned invitations (no nutritionist_id):")
            for inv in orphaned:
                print(f"      - {inv.email} [ID: {inv.id}]")
        else:
            print("✅ No orphaned invitations found")
        
        # Check total invitations vs assigned invitations
        total_invitations = PatientInvitation.query.count()
        assigned_invitations = PatientInvitation.query.filter(PatientInvitation.nutritionist_id.isnot(None)).count()
        
        print(f"\n📊 Summary:")
        print(f"   Total invitations: {total_invitations}")
        print(f"   Assigned invitations: {assigned_invitations}")
        print(f"   Unassigned invitations: {total_invitations - assigned_invitations}")
        
        if total_invitations == assigned_invitations:
            print("✅ All invitations are properly assigned to nutritionists")
        else:
            print("⚠️  Some invitations are not assigned to nutritionists")

if __name__ == "__main__":
    test_invitation_filtering()
