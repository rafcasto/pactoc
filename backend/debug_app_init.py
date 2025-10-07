#!/usr/bin/env python3
"""
Debug script to see what's happening during app initialization.
"""
import os
import sys

def debug_app_init():
    """Debug the app initialization process."""
    try:
        # Add backend to path
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, backend_dir)
        
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['VERCEL'] = '1'
        
        print("🔍 Starting app initialization debug...")
        
        # Try importing the main app first
        try:
            from app import create_app
            print("✅ Main app module imported successfully")
            
            # Try creating the app
            flask_app = create_app('production')
            print("✅ Flask app created successfully")
            
            # Check registered routes
            print("\n📍 Registered routes:")
            for rule in flask_app.url_map.iter_rules():
                print(f"   {rule.endpoint}: {rule.rule} ({rule.methods})")
            
            return flask_app
            
        except Exception as e:
            print(f"❌ Error creating main app: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    app = debug_app_init()
    
    if app:
        print("\n🧪 Testing routes...")
        with app.test_client() as client:
            test_routes = ['/', '/health', '/api/health']
            for route in test_routes:
                try:
                    response = client.get(route)
                    print(f"   {route}: {response.status_code}")
                    if response.status_code == 200:
                        data = response.get_json()
                        if data:
                            print(f"      Data: {data}")
                except Exception as e:
                    print(f"   {route}: ERROR - {e}")
        
        print("\n✅ Debug completed!")
    else:
        print("\n❌ Could not create app for testing")
