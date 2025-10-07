#!/usr/bin/env python3
"""
Test script to verify nutritionist filtering is working properly.
"""
import os
os.environ['DATABASE_URL'] = 'postgres://default:mh2MyezF6ZiE@ep-empty-recipe-a4b2qte1-pooler.us-east-1.aws.neon.tech/verceldb?sslmode=require'

from app import create_app
from app.services.database_service import db
from app.models.sql_models import PatientInvitation, Nutritionist, MealPlan, Patient

def test_filtering():
    app = create_app()
    with app.app_context():
        print("=== TESTING NUTRITIONIST FILTERING ===\n")
        
        # Get all nutritionists
        nutritionists = Nutritionist.query.all()
        print(f"Total Nutritionists: {len(nutritionists)}")
        
        for i, nutritionist in enumerate(nutritionists, 1):
            print(f"\n--- Nutritionist {i} ---")
            print(f"ID: {nutritionist.id}")
            print(f"Firebase UID: {nutritionist.firebase_uid}")
            print(f"Email: {nutritionist.email}")
            
            # Get invitations for this nutritionist
            invitations = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id).all()
            print(f"Invitations: {len(invitations)}")
            
            # Get patients for this nutritionist (through invitations)
            patients = db.session.query(Patient)\
                .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
                .filter(PatientInvitation.nutritionist_id == nutritionist.id).all()
            print(f"Patients: {len(patients)}")
            
            # Get meal plans for this nutritionist
            meal_plans = MealPlan.query.filter_by(nutritionist_id=nutritionist.id).all()
            print(f"Meal Plans: {len(meal_plans)}")
            
            # Test the dashboard data for this nutritionist
            from app.services.meal_plan_workflow_service import MealPlanWorkflowService
            success, dashboard_data, error = MealPlanWorkflowService.get_nutritionist_dashboard_data(nutritionist.firebase_uid)
            
            if success:
                print(f"Dashboard Data:")
                print(f"  - Pending Review: {len(dashboard_data['pending_review'])}")
                print(f"  - Approved Plans: {len(dashboard_data['approved_plans'])}")
                print(f"  - Pending Invitations: {len(dashboard_data['pending_invitations'])}")
            else:
                print(f"Dashboard Error: {error}")
        
        print("\n=== TESTING COMPLETE ===")

if __name__ == '__main__':
    test_filtering()
