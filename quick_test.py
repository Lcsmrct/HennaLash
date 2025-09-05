#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://henna-lash.onrender.com"
API_BASE_URL = f"{BACKEND_URL}/api"

async def test_slot_creation():
    async with aiohttp.ClientSession() as session:
        # First login as admin
        admin_login = {
            "email": "admin@salon.com",
            "password": "Admin123!"
        }
        
        async with session.post(f"{API_BASE_URL}/auth/login", json=admin_login) as response:
            if response.status == 200:
                token_data = await response.json()
                admin_token = token_data.get("access_token")
                print(f"✅ Admin login successful")
            else:
                print(f"❌ Admin login failed: {response.status}")
                return
        
        # Test simplified slot creation
        tomorrow = datetime.now() + timedelta(days=1)
        slot_data = {
            "date": tomorrow.strftime("%Y-%m-%dT00:00:00Z"),
            "time": "14:00"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {admin_token}"
        }
        
        print(f"Testing slot creation with data: {slot_data}")
        
        async with session.post(f"{API_BASE_URL}/slots", json=slot_data, headers=headers) as response:
            response_text = await response.text()
            print(f"Response status: {response.status}")
            print(f"Response: {response_text}")
            
            if response.status == 200:
                slot_response = await response.json()
                print(f"✅ Slot created successfully!")
                print(f"   Start time: {slot_response.get('start_time')}")
                print(f"   End time: {slot_response.get('end_time')}")
                print(f"   Duration: {slot_response.get('service_duration')}")
            else:
                print(f"❌ Slot creation failed")

if __name__ == "__main__":
    asyncio.run(test_slot_creation())