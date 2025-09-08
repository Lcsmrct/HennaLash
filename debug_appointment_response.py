#!/usr/bin/env python3
"""
Debug script to check the appointment response structure
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://henna-lash.onrender.com/api"
ADMIN_EMAIL = "admin@salon.com"
ADMIN_PASSWORD = "testadmin123"
CLIENT_EMAIL = "marie.dupont@email.com"
CLIENT_PASSWORD = "marie123"

def make_request(method, endpoint, data=None, headers=None, auth_token=None):
    """Make HTTP request with proper error handling"""
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=15)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=15)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=15)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except Exception as e:
        print(f"Request error: {str(e)}")
        return None

def main():
    # Login as admin
    admin_login = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = make_request("POST", "/login", admin_login)
    if not response or response.status_code != 200:
        print("Failed to login as admin")
        return
    
    admin_token = response.json()["access_token"]
    print("✅ Admin login successful")
    
    # Login as client
    client_login = {"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}
    response = make_request("POST", "/login", client_login)
    if not response or response.status_code != 200:
        print("Failed to login as client")
        return
    
    client_token = response.json()["access_token"]
    print("✅ Client login successful")
    
    # Create a test slot
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    slot_data = {"date": tomorrow, "time": "16:00"}
    
    response = make_request("POST", "/slots", slot_data, auth_token=admin_token)
    if not response or response.status_code != 200:
        print("Failed to create slot")
        return
    
    slot_id = response.json()["id"]
    print(f"✅ Slot created: {slot_id}")
    
    # Create appointment
    appointment_data = {
        "slot_id": slot_id,
        "service_name": "Test Service",
        "service_price": 15.0,
        "notes": "Test notes with detailed information"
    }
    
    response = make_request("POST", "/appointments", appointment_data, auth_token=client_token)
    if not response or response.status_code != 200:
        print("Failed to create appointment")
        return
    
    appointment_id = response.json()["id"]
    print(f"✅ Appointment created: {appointment_id}")
    
    # Update appointment status and capture the response
    update_data = {"status": "confirmed", "notes": "Admin confirmation"}
    
    response = make_request("PUT", f"/appointments/{appointment_id}/status", update_data, auth_token=admin_token)
    if response and response.status_code == 200:
        print("✅ Appointment status updated")
        print("\n📋 RESPONSE STRUCTURE:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2, default=str))
        
        # Check specific fields
        print(f"\n🔍 FIELD ANALYSIS:")
        print(f"Notes present: {'notes' in response_data}")
        print(f"User name present: {'user_name' in response_data}")
        print(f"User email present: {'user_email' in response_data}")
        print(f"Slot info present: {'slot_info' in response_data}")
        
        if 'slot_info' in response_data:
            slot_info = response_data['slot_info']
            print(f"Slot info type: {type(slot_info)}")
            if slot_info:
                print(f"Slot info keys: {list(slot_info.keys()) if isinstance(slot_info, dict) else 'Not a dict'}")
    else:
        print(f"❌ Failed to update appointment: {response.status_code if response else 'No response'}")
        if response:
            print(f"Error: {response.text}")
    
    # Cleanup
    make_request("DELETE", f"/appointments/{appointment_id}", auth_token=admin_token)
    make_request("DELETE", f"/slots/{slot_id}", auth_token=admin_token)
    print("✅ Cleanup completed")

if __name__ == "__main__":
    main()