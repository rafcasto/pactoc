#!/usr/bin/env python3
"""
Simple backend server test to verify invitation endpoints
"""
import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from flask import Flask

def test_backend_routes():
    print("🧪 TESTING BACKEND ROUTES")
    print("=" * 40)
    
    try:
        app = create_app()
        
        # Test that app can be created
        print("✅ Flask app created successfully")
        
        # List all registered routes
        print("\n📋 Registered routes:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"   {methods:10} {rule.rule}")
        
        print("\n🎯 Key invitation routes to check:")
        invitation_routes = [rule for rule in app.url_map.iter_rules() 
                           if 'invitation' in rule.rule.lower()]
        
        if invitation_routes:
            for route in invitation_routes:
                methods = ','.join(route.methods - {'HEAD', 'OPTIONS'})
                print(f"   ✅ {methods:10} {route.rule}")
        else:
            print("   ❌ No invitation routes found!")
            
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_routes()
