#!/usr/bin/env python3
"""
Script para crear una invitación de prueba.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DATABASE_URL', 'sqlite:///pactoc_dev.db')

from app import create_app
from app.services.database_service import db
from app.models.sql_models import PatientInvitation

def create_test_invitation():
    """Crear una invitación de prueba."""
    app = create_app('development')
    
    with app.app_context():
        # Crear invitación de prueba
        invitation = PatientInvitation(
            email='paciente@test.com',
            first_name='Juan',
            last_name='Pérez',
            invited_by_uid='test-admin-uid',
            status='pending',
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(invitation)
        db.session.commit()
        
        print("✅ Invitación de prueba creada exitosamente!")
        print(f"📧 Email: {invitation.email}")
        print(f"🔑 Token: {invitation.token}")
        print(f"🌐 URL de prueba: http://localhost:3000/complete-profile/{invitation.token}")
        print(f"📅 Expira: {invitation.expires_at}")
        
        return invitation.token

if __name__ == '__main__':
    token = create_test_invitation()
