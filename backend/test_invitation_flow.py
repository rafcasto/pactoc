#!/usr/bin/env python3
"""
Test script for invitation creation flow
"""
import os
import sys
import requests
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_invitation_flow():
    print("🧪 TESTING INVITATION CREATION FLOW")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Test basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Backend responding: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend not responding: {e}")
        return
    
    # 2. Test public endpoints
    print("\n2. Testing public endpoints...")
    try:
        response = requests.get(f"{base_url}/api/public/catalogs")
        print(f"   ✅ Public catalogs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Public catalogs failed: {e}")
    
    # 3. Test unauthenticated invitation endpoint (should fail)
    print("\n3. Testing unauthenticated invitation endpoint...")
    try:
        response = requests.get(f"{base_url}/api/invitations")
        if response.status_code == 401:
            print(f"   ✅ Correctly rejected unauthenticated request: {response.status_code}")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # 4. Test with fake token (should fail with proper error)
    print("\n4. Testing with invalid token...")
    try:
        headers = {
            'Authorization': 'Bearer fake-token',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{base_url}/api/invitations", headers=headers)
        print(f"   Response: {response.status_code}")
        if response.status_code == 401:
            try:
                error_data = response.json()
                print(f"   ✅ Proper error response: {error_data.get('message', 'No message')}")
            except:
                print(f"   ✅ Authentication properly rejected")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # 5. Test POST invitation with fake token
    print("\n5. Testing POST invitation with invalid token...")
    try:
        headers = {
            'Authorization': 'Bearer fake-token',
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = requests.post(f"{base_url}/api/invitations", 
                               headers=headers, 
                               json=data)
        print(f"   Response: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✅ POST correctly rejected invalid token")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n✅ INVITATION FLOW TEST COMPLETED")
    print("\n📋 NEXT STEPS:")
    print("1. Register a test user in the frontend")
    print("2. Login and get a valid Firebase token")
    print("3. Test invitation creation with valid token")
    print("4. Check browser console for frontend debugging")
    
    print(f"\n🌐 Frontend URL: http://localhost:3000/login")
    print(f"🔧 Backend URL: {base_url}")

if __name__ == "__main__":
    test_invitation_flow()
