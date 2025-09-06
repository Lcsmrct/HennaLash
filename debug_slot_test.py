#!/usr/bin/env python3
"""
Debug test for slot availability issue
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BACKEND_URL = "http://localhost:8001"
API_BASE_URL = f"{BACKEND_URL}/api"

async def debug_slot_availability():
    async with aiohttp.ClientSession() as session:
        # Login as admin
        admin_login = {
            "email": "admin@salon.com",
            "password": "Admin123!"
        }
        
        async with session.post(f"{API_BASE_URL}/auth/login", json=admin_login) as response:
            admin_data = await response.json()
            admin_token = admin_data.get("access_token")
        
        # Login as client
        client_login = {
            "email": "sarah.johnson@email.com",
            "password": "Test123!"
        }
        
        async with session.post(f"{API_BASE_URL}/auth/login", json=client_login) as response:
            client_data = await response.json()
            client_token = client_data.get("access_token")
        
        print(f"Admin token: {admin_token[:20]}...")
        print(f"Client token: {client_token[:20]}...")
        
        # Create a new slot
        tomorrow = datetime.now() + timedelta(days=1)
        slot_data = {
            "date": tomorrow.strftime("%Y-%m-%dT00:00:00Z"),
            "time": "18:00"
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        async with session.post(f"{API_BASE_URL}/slots", json=slot_data, headers=headers) as response:
            slot_result = await response.json()
            slot_id = slot_result.get("id")
            print(f"Created slot ID: {slot_id}")
            print(f"Slot is_available: {slot_result.get('is_available')}")
        
        # Check slot availability before booking
        async with session.get(f"{API_BASE_URL}/slots") as response:
            slots = await response.json()
            test_slot = next((s for s in slots if s["id"] == slot_id), None)
            print(f"Before booking - Slot available: {test_slot.get('is_available') if test_slot else 'NOT FOUND'}")
        
        # Create appointment
        appointment_data = {
            "slot_id": slot_id,
            "service_name": "Debug Test",
            "service_price": 10.0,
            "notes": "Testing slot availability"
        }
        
        headers = {"Authorization": f"Bearer {client_token}"}
        async with session.post(f"{API_BASE_URL}/appointments", json=appointment_data, headers=headers) as response:
            appointment_result = await response.json()
            appointment_id = appointment_result.get("id")
            print(f"Created appointment ID: {appointment_id}")
            print(f"Response status: {response.status}")
        
        # Check slot availability after booking
        async with session.get(f"{API_BASE_URL}/slots") as response:
            slots = await response.json()
            test_slot = next((s for s in slots if s["id"] == slot_id), None)
            print(f"After booking - Slot available: {test_slot.get('is_available') if test_slot else 'NOT FOUND'}")
        
        # Check available slots only
        async with session.get(f"{API_BASE_URL}/slots?available_only=true") as response:
            available_slots = await response.json()
            test_slot_in_available = next((s for s in available_slots if s["id"] == slot_id), None)
            print(f"Slot in available_only list: {'YES' if test_slot_in_available else 'NO'}")

if __name__ == "__main__":
    asyncio.run(debug_slot_availability())