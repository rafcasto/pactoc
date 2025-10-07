#!/usr/bin/env python3
"""
Debug script to check invitation token validation issues.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from app.services.database_service import db
from app.models.sql_models import PatientInvitation

def debug_invitation_token(token=None):
    """Debug invitation token validation."""
    app = create_app()
    
    with app.app_context():
        print("=== INVITATION TOKEN DEBUG ===")
        print(f"Current time: {datetime.utcnow()}")
        print()
        
        if token:
            print(f"Debugging specific token: {token}")
            invitation = PatientInvitation.query.filter_by(token=token).first()
            
            if invitation:
                print(f"Found invitation:")
                print(f"  ID: {invitation.id}")
                print(f"  Email: {invitation.email}")
                print(f"  Status: {invitation.status}")
                print(f"  Expires at: {invitation.expires_at}")
                print(f"  Created at: {invitation.created_at}")
                print(f"  Updated at: {invitation.updated_at}")
                print(f"  Is valid: {invitation.is_valid}")
                
                # Check individual conditions
                print("\nValidation checks:")
                print(f"  Status is 'pending': {invitation.status == 'pending'}")
                print(f"  Not expired: {invitation.expires_at > datetime.utcnow()}")
                print(f"  Time until expiry: {invitation.expires_at - datetime.utcnow()}")
            else:
                print("Invitation not found!")
        else:
            print("All invitations in database:")
            invitations = PatientInvitation.query.all()
            
            if not invitations:
                print("No invitations found!")
                return
            
            for inv in invitations:
                print(f"\nID: {inv.id}")
                print(f"  Email: {inv.email}")
                print(f"  Token: {inv.token[:20]}...")
                print(f"  Status: {inv.status}")
                print(f"  Expires: {inv.expires_at}")
                print(f"  Is valid: {inv.is_valid}")

if __name__ == "__main__":
    # Get token from command line if provided
    token = sys.argv[1] if len(sys.argv) > 1 else None
    debug_invitation_token(token)
