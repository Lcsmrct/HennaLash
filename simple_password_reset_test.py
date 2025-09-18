#!/usr/bin/env python3
"""
Simple Password Reset Test with Debug Logging
"""

import requests
import time
import random

BASE_URL = "https://cancel-appt-fix.preview.emergentagent.com/api"
TIMEOUT = 15

def test_password_reset_with_debug():
    # Create unique test user
    test_email = f"debugtest{random.randint(1000, 9999)}@test.com"
    original_password = "original123"
    new_password = "newpassword456"
    
    print(f"🧪 Testing password reset for: {test_email}")
    
    # Step 1: Create user
    print("\n1. Creating test user...")
    response = requests.post(
        f"{BASE_URL}/register",
        json={
            "email": test_email,
            "password": original_password,
            "first_name": "Debug",
            "last_name": "Test",
            "phone": "0123456789"
        },
        timeout=TIMEOUT
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")
        return
    
    print("✅ User created successfully")
    
    # Step 2: Verify login works
    print("\n2. Verifying initial login...")
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "email": test_email,
            "password": original_password
        },
        timeout=TIMEOUT
    )
    
    if response.status_code != 200:
        print(f"❌ Initial login failed: {response.status_code} - {response.text}")
        return
    
    print("✅ Initial login successful")
    
    # Step 3: Request password reset
    print("\n3. Requesting password reset...")
    response = requests.post(
        f"{BASE_URL}/auth/password-reset/request",
        json={"email": test_email},
        timeout=TIMEOUT
    )
    
    if response.status_code != 200:
        print(f"❌ Password reset request failed: {response.status_code} - {response.text}")
        return
    
    print("✅ Password reset request successful")
    print("📋 Check backend logs for the generated code!")
    print("   Command: tail -n 10 /var/log/supervisor/backend.out.log")
    
    return test_email, new_password

if __name__ == "__main__":
    test_password_reset_with_debug()