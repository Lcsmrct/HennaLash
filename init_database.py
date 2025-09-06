#!/usr/bin/env python3
"""
Database Initialization Script for HennaLash Salon
Clears existing data and creates initial setup
"""

import asyncio
import aiohttp
import json
from datetime import datetime, time, timedelta

# Backend API URL
API_BASE_URL = "https://cache-debug-fixes.preview.emergentagent.com/api"

class DatabaseInitializer:
    def __init__(self):
        self.admin_token = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method, endpoint, data=None, token=None):
        """Make HTTP request to API"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            async with self.session.request(method, url, json=data if data else None, headers=headers) as response:
                response_data = {}
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                return {
                    "success": response.status < 400,
                    "status": response.status,
                    "data": response_data
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_admin_user(self):
        """Create admin user for HennaLash salon"""
        print("🔧 Creating admin user...")
        
        admin_data = {
            "email": "admin@salon.com",
            "password": "Admin123!",
            "first_name": "Alicia",
            "last_name": "Admin",
            "phone": "+33 6 12 34 56 78"
        }
        
        # Try to register admin
        result = await self.make_request("POST", "/auth/register", admin_data)
        
        if result["success"] or result["status"] == 400:  # 400 if user already exists
            print("✅ Admin user ready")
            
            # Login to get token
            login_result = await self.make_request("POST", "/auth/login", {
                "email": admin_data["email"],
                "password": admin_data["password"]
            })
            
            if login_result["success"]:
                self.admin_token = login_result["data"]["access_token"]
                print("✅ Admin logged in successfully")
                return True
            else:
                print(f"❌ Admin login failed: {login_result}")
                return False
        else:
            print(f"❌ Admin creation failed: {result}")
            return False
    
    async def create_sample_time_slots(self):
        """Create sample time slots for the salon"""
        print("🕐 Creating sample time slots...")
        
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        # Create slots for the next 7 days
        base_date = datetime.now() + timedelta(days=1)
        services = [
            {"name": "Henné Simple", "duration": 30, "price": 8.0},
            {"name": "Henné Chargé", "duration": 60, "price": 12.0},
            {"name": "Henné Mariée", "duration": 90, "price": 20.0},
            {"name": "Henné Traditionnel", "duration": 45, "price": 15.0}
        ]
        
        time_slots = [
            ("09:00:00", "09:30:00"), ("09:30:00", "10:00:00"),
            ("10:00:00", "10:30:00"), ("10:30:00", "11:00:00"),
            ("11:00:00", "11:30:00"), ("11:30:00", "12:00:00"),
            ("14:00:00", "14:30:00"), ("14:30:00", "15:00:00"),
            ("15:00:00", "15:30:00"), ("15:30:00", "16:00:00"),
            ("16:00:00", "16:30:00"), ("16:30:00", "17:00:00"),
            ("17:00:00", "17:30:00"), ("17:30:00", "18:00:00")
        ]
        
        created_count = 0
        
        for day_offset in range(7):  # Next 7 days
            slot_date = base_date + timedelta(days=day_offset)
            # Skip Sundays (weekday 6)
            if slot_date.weekday() == 6:
                continue
                
            for start_time, end_time in time_slots:
                # Randomly assign services (simulate variety)
                service = services[day_offset % len(services)]
                
                slot_data = {
                    "date": slot_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    "start_time": start_time,
                    "end_time": end_time,
                    "service_name": service["name"],
                    "service_duration": service["duration"],
                    "price": service["price"]
                }
                
                result = await self.make_request("POST", "/slots", slot_data, token=self.admin_token)
                
                if result["success"]:
                    created_count += 1
                else:
                    print(f"Failed to create slot: {result}")
        
        print(f"✅ Created {created_count} time slots")
        return created_count > 0
    
    async def create_sample_client_and_data(self):
        """Create sample client user with appointments and reviews"""
        print("👤 Creating sample client user...")
        
        # Create client user
        client_data = {
            "email": "sarah.martin@email.com",
            "password": "Client123!",
            "first_name": "Sarah",
            "last_name": "Martin",
            "phone": "+33 6 98 76 54 32"
        }
        
        result = await self.make_request("POST", "/auth/register", client_data)
        
        if result["success"] or result["status"] == 400:  # 400 if user already exists
            print("✅ Sample client user created")
            
            # Login client to get token
            login_result = await self.make_request("POST", "/auth/login", {
                "email": client_data["email"],
                "password": client_data["password"]
            })
            
            if login_result["success"]:
                client_token = login_result["data"]["access_token"]
                print("✅ Client logged in successfully")
                
                # Get available slots
                slots_result = await self.make_request("GET", "/slots?available_only=true")
                
                if slots_result["success"] and len(slots_result["data"]) > 0:
                    # Book first available slot
                    slot_id = slots_result["data"][0]["id"]
                    
                    appointment_result = await self.make_request("POST", "/appointments", {
                        "slot_id": slot_id,
                        "notes": "Première fois, je suis très excitée !"
                    }, token=client_token)
                    
                    if appointment_result["success"]:
                        print("✅ Sample appointment created")
                    
                # Create a sample review
                review_result = await self.make_request("POST", "/reviews", {
                    "rating": 5,
                    "comment": "Service exceptionnel ! Les motifs au henné étaient magnifiques et ont duré très longtemps. Je recommande vivement !"
                }, token=client_token)
                
                if review_result["success"]:
                    print("✅ Sample review created")
                    
                    # Admin approves the review
                    if review_result["success"]:
                        review_id = review_result["data"]["id"]
                        approve_result = await self.make_request("PUT", f"/reviews/{review_id}", {
                            "status": "approved"
                        }, token=self.admin_token)
                        
                        if approve_result["success"]:
                            print("✅ Sample review approved")
                
                return True
            
        return False
    
    async def verify_setup(self):
        """Verify the database setup"""
        print("🔍 Verifying database setup...")
        
        # Check appointments
        appointments_result = await self.make_request("GET", "/appointments", token=self.admin_token)
        if appointments_result["success"]:
            print(f"✅ {len(appointments_result['data'])} appointments in database")
        
        # Check slots
        slots_result = await self.make_request("GET", "/slots")
        if slots_result["success"]:
            print(f"✅ {len(slots_result['data'])} time slots in database")
        
        # Check reviews
        reviews_result = await self.make_request("GET", "/reviews?approved_only=false", token=self.admin_token)
        if reviews_result["success"]:
            print(f"✅ {len(reviews_result['data'])} reviews in database")
        
        print("✅ Database verification complete")
    
    async def initialize_database(self):
        """Initialize the complete database"""
        print("🚀 Initializing HennaLash Salon Database")
        print("=" * 50)
        
        success = True
        
        # Step 1: Create admin user
        if not await self.create_admin_user():
            success = False
        
        # Step 2: Create time slots
        if success and not await self.create_sample_time_slots():
            success = False
        
        # Step 3: Create sample client and data
        if success and not await self.create_sample_client_and_data():
            success = False
        
        # Step 4: Verify setup
        if success:
            await self.verify_setup()
        
        print("=" * 50)
        if success:
            print("🎉 Database initialization completed successfully!")
            print()
            print("📋 ADMIN CREDENTIALS:")
            print("   Email: admin@salon.com")
            print("   Password: Admin123!")
            print()
            print("📋 SAMPLE CLIENT CREDENTIALS:")
            print("   Email: sarah.martin@email.com")
            print("   Password: Client123!")
            print()
            print("🌐 Access your admin dashboard at:")
            print("   https://cache-debug-fixes.preview.emergentagent.com/connexion")
        else:
            print("❌ Database initialization failed!")
        
        return success

async def main():
    """Main initialization function"""
    async with DatabaseInitializer() as initializer:
        await initializer.initialize_database()

if __name__ == "__main__":
    asyncio.run(main())