#!/usr/bin/env python3
"""
Test script to verify Vercel deployment configuration.
Run this locally to test if the API entry point works correctly.
"""
import os
import sys

def test_api_import():
    """Test if the API can be imported successfully."""
    try:
        # Add backend to path
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, backend_dir)
        
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['VERCEL'] = '1'
        
        # Import and test the API
        from api.index import app
        
        print("✅ API import successful")
        
        # Test basic routes
        with app.test_client() as client:
            # Test root route (health check)
            response = client.get('/')
            print(f"✅ Root route status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.get_json()}")
            
            # Test API status route
            response = client.get('/api')
            print(f"✅ API status route status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.get_json()}")
            
            # Test health route
            response = client.get('/health')
            print(f"✅ Health route status: {response.status_code}")
            
            # Test API health route  
            response = client.get('/api/health')
            print(f"✅ API health route status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Vercel deployment configuration...")
    success = test_api_import()
    
    if success:
        print("\n✅ Vercel deployment test passed!")
        print("You can now deploy to Vercel using: vercel --prod")
    else:
        print("\n❌ Vercel deployment test failed!")
        print("Please fix the issues above before deploying.")
    
    sys.exit(0 if success else 1)
