#!/usr/bin/env python3
"""
Script to add a nutritionist to the database.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.database_service import init_db, db
from app.models.sql_models import Nutritionist
from app import create_app
from datetime import datetime

def add_nutritionist(firebase_uid, email, first_name, last_name):
    """Add a nutritionist to the database."""
    try:
        # Check if nutritionist already exists
        existing = Nutritionist.query.filter_by(firebase_uid=firebase_uid).first()
        if existing:
            print(f"Nutritionist with Firebase UID {firebase_uid} already exists")
            return existing
        
        # Check if email already exists
        existing_email = Nutritionist.query.filter_by(email=email).first()
        if existing_email:
            print(f"Nutritionist with email {email} already exists")
            return existing_email
        
        # Create new nutritionist
        nutritionist = Nutritionist(
            firebase_uid=firebase_uid,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True,
            verification_date=datetime.utcnow()
        )
        
        db.session.add(nutritionist)
        db.session.commit()
        
        print(f"✅ Nutritionist added successfully:")
        print(f"   ID: {nutritionist.id}")
        print(f"   Firebase UID: {nutritionist.firebase_uid}")
        print(f"   Email: {nutritionist.email}")
        print(f"   Name: {nutritionist.first_name} {nutritionist.last_name}")
        
        return nutritionist
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding nutritionist: {e}")
        return None

def main():
    """Main function."""
    app = create_app()
    
    with app.app_context():
        init_db(app)
        
        # Add rafael@techdojo.pro as a nutritionist
        # We need to find out their Firebase UID first
        # For now, let's create them with a placeholder UID
        
        firebase_uid = input("Enter Firebase UID for rafael@techdojo.pro: ").strip()
        if not firebase_uid:
            print("Firebase UID is required")
            return
        
        nutritionist = add_nutritionist(
            firebase_uid=firebase_uid,
            email="rafael@techdojo.pro",
            first_name="Rafael",
            last_name="Castillo"
        )
        
        if nutritionist:
            print("\n✅ Nutritionist registration complete!")
        else:
            print("\n❌ Failed to register nutritionist")

if __name__ == "__main__":
    main()
