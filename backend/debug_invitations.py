#!/usr/bin/env python3
"""
Debug script to inspect invitation system status
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.services.database_service import db, test_connection
from app.models.sql_models import PatientInvitation
from sqlalchemy import text
from datetime import datetime

def debug_invitation_system():
    print("🔍 INVITATION SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        # 1. Test database connection
        print("1. Testing database connection...")
        if test_connection():
            print("   ✅ PostgreSQL connection successful")
        else:
            print("   ❌ PostgreSQL connection failed")
            return
        
        # 2. Check table existence
        print("\n2. Checking database tables...")
        try:
            result = db.session.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='public' AND table_name LIKE '%invitation%'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"   Tables found: {tables}")
        except Exception as e:
            print(f"   ❌ Error checking tables: {e}")
        
        # 3. Count invitations
        print("\n3. Checking invitation counts...")
        try:
            total = PatientInvitation.query.count()
            pending = PatientInvitation.query.filter_by(status='pending').count()
            completed = PatientInvitation.query.filter_by(status='completed').count()
            
            print(f"   Total invitations: {total}")
            print(f"   Pending: {pending}")
            print(f"   Completed: {completed}")
        except Exception as e:
            print(f"   ❌ Error counting invitations: {e}")
        
        # 4. Show recent invitations
        print("\n4. Recent invitations (last 5)...")
        try:
            recent = PatientInvitation.query.order_by(
                PatientInvitation.created_at.desc()
            ).limit(5).all()
            
            if not recent:
                print("   📭 No invitations found")
            else:
                for inv in recent:
                    print(f"   • {inv.email} | {inv.status} | {inv.created_at}")
                    print(f"     Token: {inv.token[:20]}...")
        except Exception as e:
            print(f"   ❌ Error fetching invitations: {e}")
        
        # 5. Test invitation creation
        print("\n5. Testing invitation creation...")
        try:
            test_invitation = PatientInvitation(
                email='test-debug@example.com',
                first_name='Debug',
                last_name='Test',
                invited_by_uid='debug-test-uid'
            )
            
            db.session.add(test_invitation)
            db.session.commit()
            
            print(f"   ✅ Test invitation created with token: {test_invitation.token[:20]}...")
            
            # Clean up test invitation
            db.session.delete(test_invitation)
            db.session.commit()
            print("   🧹 Test invitation cleaned up")
            
        except Exception as e:
            print(f"   ❌ Error creating test invitation: {e}")
            db.session.rollback()

if __name__ == "__main__":
    debug_invitation_system()
