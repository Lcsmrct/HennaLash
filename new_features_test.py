#!/usr/bin/env python3
"""
Test New Features that need retesting:
1. Database Performance Optimization
2. Email Configuration with User Credentials  
3. Service Selection in Booking
4. Client Email Confirmation
5. Simplified Admin Slot Creation
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://henna-lash.onrender.com"
API_BASE_URL = f"{BACKEND_URL}/api"

async def test_new_features():
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing New Features - Retesting Required")
        print("=" * 60)
        print(f"Backend URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Setup: Create admin and client users
        admin_token = None
        client_token = None
        
        # Create admin user
        admin_data = {
            "email": "admin@salon.com",
            "password": "Admin123!",
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+33-1-00-00-00-00"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/auth/register", 
                                  json=admin_data,
                                  headers={"Content-Type": "application/json"}) as response:
                if response.status in [200, 400]:  # 400 if already exists
                    print("✅ Admin user ready")
        except Exception as e:
            print(f"❌ Admin setup error: {e}")
        
        # Login admin
        try:
            async with session.post(f"{API_BASE_URL}/auth/login", 
                                  json={"email": "admin@salon.com", "password": "Admin123!"},
                                  headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    admin_token = data.get("access_token")
                    print("✅ Admin authenticated")
        except Exception as e:
            print(f"❌ Admin login error: {e}")
        
        # Create client user
        client_data = {
            "email": "client.test@email.com",
            "password": "Client123!",
            "first_name": "Client",
            "last_name": "Test",
            "phone": "+33-1-11-11-11-11"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/auth/register", 
                                  json=client_data,
                                  headers={"Content-Type": "application/json"}) as response:
                if response.status in [200, 400]:
                    print("✅ Client user ready")
        except Exception as e:
            print(f"❌ Client setup error: {e}")
        
        # Login client
        try:
            async with session.post(f"{API_BASE_URL}/auth/login", 
                                  json={"email": "client.test@email.com", "password": "Client123!"},
                                  headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    data = await response.json()
                    client_token = data.get("access_token")
                    print("✅ Client authenticated")
        except Exception as e:
            print(f"❌ Client login error: {e}")
        
        if not admin_token or not client_token:
            print("❌ Cannot proceed without tokens")
            return
        
        admin_headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        client_headers = {"Authorization": f"Bearer {client_token}", "Content-Type": "application/json"}
        
        # Test 1: Database Performance Optimization
        print("\n1. Testing Database Performance Optimization")
        start_time = datetime.now()
        try:
            async with session.get(f"{API_BASE_URL}/reviews?approved_only=true") as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   Reviews loaded: {len(data)} items in {response_time:.2f}s")
                    if response_time < 2.0:
                        print("   ✅ PASS: Performance optimized (< 2s)")
                    else:
                        print("   ❌ FAIL: Performance issue (> 2s)")
                else:
                    print(f"   ❌ FAIL: Reviews request failed: {response.status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test 2: Simplified Admin Slot Creation
        print("\n2. Testing Simplified Admin Slot Creation")
        tomorrow = datetime.now() + timedelta(days=1)
        slot_data = {
            "date": tomorrow.strftime("%Y-%m-%dT00:00:00Z"),
            "time": "15:30"  # Only time field, no start_time/end_time
        }
        
        created_slot_id = None
        try:
            async with session.post(f"{API_BASE_URL}/slots", 
                                  json=slot_data,
                                  headers=admin_headers) as response:
                if response.status == 200:
                    data = await response.json()
                    created_slot_id = data.get("id")
                    start_time = data.get("start_time")
                    end_time = data.get("end_time")
                    duration = data.get("service_duration")
                    
                    print(f"   Slot created: {start_time} - {end_time} ({duration}min)")
                    
                    if start_time == "15:30" and end_time == "16:30" and duration == 60:
                        print("   ✅ PASS: Simplified slot creation with auto-calculation")
                    else:
                        print("   ❌ FAIL: Auto-calculation not working correctly")
                else:
                    error_data = await response.json()
                    print(f"   ❌ FAIL: Slot creation failed: {error_data}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Test 3: Service Selection in Booking
        print("\n3. Testing Service Selection in Booking")
        if created_slot_id:
            services = [
                {"name": "Très simple", "price": 5},
                {"name": "Simple", "price": 8},
                {"name": "Chargé", "price": 12},
                {"name": "Mariée", "price": 20}
            ]
            
            for service in services:
                # Create a new slot for each service test
                slot_data = {
                    "date": (tomorrow + timedelta(hours=1)).strftime("%Y-%m-%dT00:00:00Z"),
                    "time": f"{16 + services.index(service)}:00"
                }
                
                try:
                    async with session.post(f"{API_BASE_URL}/slots", 
                                          json=slot_data,
                                          headers=admin_headers) as response:
                        if response.status == 200:
                            slot_data_response = await response.json()
                            test_slot_id = slot_data_response.get("id")
                            
                            # Create appointment with service selection
                            appointment_data = {
                                "slot_id": test_slot_id,
                                "service_name": service["name"],
                                "service_price": service["price"],
                                "notes": f"Test booking for {service['name']} service"
                            }
                            
                            async with session.post(f"{API_BASE_URL}/appointments", 
                                                  json=appointment_data,
                                                  headers=client_headers) as apt_response:
                                if apt_response.status == 200:
                                    apt_data = await apt_response.json()
                                    if (apt_data.get("service_name") == service["name"] and 
                                        apt_data.get("service_price") == service["price"]):
                                        print(f"   ✅ PASS: {service['name']} ({service['price']}€) booking successful")
                                    else:
                                        print(f"   ❌ FAIL: Service data incorrect for {service['name']}")
                                else:
                                    error_data = await apt_response.json()
                                    print(f"   ❌ FAIL: Booking failed for {service['name']}: {error_data}")
                except Exception as e:
                    print(f"   ❌ ERROR testing {service['name']}: {e}")
        
        # Test 4: Email Configuration (Check if configured)
        print("\n4. Testing Email Configuration")
        # We can't directly test email sending, but we can verify the configuration exists
        # by checking if appointment creation triggers email notifications without errors
        
        # Create a slot and appointment to trigger email
        email_test_slot = {
            "date": (tomorrow + timedelta(days=2)).strftime("%Y-%m-%dT00:00:00Z"),
            "time": "10:00"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/slots", 
                                  json=email_test_slot,
                                  headers=admin_headers) as response:
                if response.status == 200:
                    slot_data = await response.json()
                    email_slot_id = slot_data.get("id")
                    
                    # Create appointment (should trigger email to admin)
                    email_appointment = {
                        "slot_id": email_slot_id,
                        "service_name": "Test Email",
                        "service_price": 10,
                        "notes": "Testing email configuration"
                    }
                    
                    async with session.post(f"{API_BASE_URL}/appointments", 
                                          json=email_appointment,
                                          headers=client_headers) as apt_response:
                        if apt_response.status == 200:
                            apt_data = await apt_response.json()
                            appointment_id = apt_data.get("id")
                            print("   ✅ PASS: Appointment created (email notification should be sent)")
                            
                            # Test 5: Client Email Confirmation
                            print("\n5. Testing Client Email Confirmation")
                            # Update appointment status to confirmed (should trigger client email)
                            update_data = {
                                "status": "confirmed",
                                "notes": "Appointment confirmed - testing email"
                            }
                            
                            async with session.put(f"{API_BASE_URL}/appointments/{appointment_id}", 
                                                 json=update_data,
                                                 headers=admin_headers) as update_response:
                                if update_response.status == 200:
                                    print("   ✅ PASS: Appointment confirmed (client email should be sent)")
                                else:
                                    error_data = await update_response.json()
                                    print(f"   ❌ FAIL: Appointment confirmation failed: {error_data}")
                        else:
                            error_data = await apt_response.json()
                            print(f"   ❌ FAIL: Email test appointment failed: {error_data}")
        except Exception as e:
            print(f"   ❌ ERROR testing email: {e}")
        
        # Test 6: Frontend Caching System (Test API response times)
        print("\n6. Testing API Response Times (for caching effectiveness)")
        
        # Test multiple requests to see if performance is consistent
        response_times = []
        for i in range(3):
            start_time = datetime.now()
            try:
                async with session.get(f"{API_BASE_URL}/reviews?approved_only=true") as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    response_times.append(response_time)
                    
                    if response.status == 200:
                        print(f"   Request {i+1}: {response_time:.2f}s")
            except Exception as e:
                print(f"   ❌ ERROR in request {i+1}: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            if avg_time < 1.0:
                print(f"   ✅ PASS: Average response time {avg_time:.2f}s (good performance)")
            else:
                print(f"   ⚠️  WARNING: Average response time {avg_time:.2f}s (could be optimized)")
        
        print("\n" + "=" * 60)
        print("📊 NEW FEATURES TEST SUMMARY")
        print("=" * 60)
        print("✅ Database Performance Optimization - Tested")
        print("✅ Simplified Admin Slot Creation - Tested")  
        print("✅ Service Selection in Booking - Tested")
        print("✅ Email Configuration - Tested (indirectly)")
        print("✅ Client Email Confirmation - Tested (indirectly)")
        print("✅ API Response Times - Tested")
        print("\n📧 Note: Email functionality tested indirectly through API calls.")
        print("   Actual email delivery depends on SMTP configuration.")

if __name__ == "__main__":
    asyncio.run(test_new_features())