#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for Salon Booking System
Tests all API endpoints, authentication, and database operations
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, time, timedelta
from typing import Dict, Any, Optional
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-service-hub.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class SalonBookingTester:
    def __init__(self):
        self.session = None
        self.client_token = None
        self.admin_token = None
        self.client_user_id = None
        self.admin_user_id = None
        self.created_slot_id = None
        self.created_appointment_id = None
        self.created_review_id = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if not success and details:
            print(f"    Details: {details}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                          token: str = None, expect_status: int = 200) -> Dict:
        """Make HTTP request to API"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            async with self.session.request(
                method, url, 
                json=data if data else None, 
                headers=headers
            ) as response:
                response_data = {}
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                if response.status != expect_status:
                    return {
                        "success": False,
                        "status": response.status,
                        "data": response_data,
                        "expected_status": expect_status
                    }
                
                return {
                    "success": True,
                    "status": response.status,
                    "data": response_data
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": 0
            }
    
    async def test_api_health_check(self):
        """Test 1: API Health Check"""
        result = await self.make_request("GET", "/")
        
        if result["success"] and result["data"].get("message") == "Salon Booking API":
            self.log_test("API Health Check", True, "API is running and responding correctly")
        else:
            self.log_test("API Health Check", False, "API health check failed", result)
    
    async def test_ping_endpoint(self):
        """Test 2: Ping Endpoint (GET and HEAD methods)"""
        # Test GET /api/ping
        result = await self.make_request("GET", "/ping")
        
        if result["success"] and result["data"].get("status") == "Ok":
            self.log_test("Ping Endpoint (GET)", True, "GET /api/ping responds with status 'Ok'")
        else:
            self.log_test("Ping Endpoint (GET)", False, "GET /api/ping failed or incorrect response", result)
        
        # Test HEAD /api/ping
        try:
            url = f"{API_BASE_URL}/ping"
            headers = {"Content-Type": "application/json"}
            
            async with self.session.head(url, headers=headers) as response:
                if response.status == 200:
                    self.log_test("Ping Endpoint (HEAD)", True, "HEAD /api/ping responds correctly with status 200")
                else:
                    self.log_test("Ping Endpoint (HEAD)", False, f"HEAD /api/ping returned status {response.status}", {"status": response.status})
        except Exception as e:
            self.log_test("Ping Endpoint (HEAD)", False, "HEAD /api/ping request failed", {"error": str(e)})
    
    async def test_user_registration(self):
        """Test 3: User Registration"""
        # Register client user
        client_data = {
            "email": "sarah.johnson@email.com",
            "password": "Test123!",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "phone": "+1-555-0123"
        }
        
        result = await self.make_request("POST", "/auth/register", client_data, expect_status=200)
        
        if result["success"]:
            user_data = result["data"]
            self.client_user_id = user_data.get("id")
            if user_data.get("role") == "client" and user_data.get("email") == client_data["email"]:
                self.log_test("Client User Registration", True, f"Client user registered successfully with ID: {self.client_user_id}")
            else:
                self.log_test("Client User Registration", False, "Client user data incorrect", user_data)
        else:
            self.log_test("Client User Registration", False, "Client registration failed", result)
        
        # Register admin user (should already exist)
        admin_data = {
            "email": "admin@salon.com",
            "password": "Admin123!",
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+1-555-0100"
        }
        
        result = await self.make_request("POST", "/auth/register", admin_data, expect_status=200)
        
        if result["success"]:
            user_data = result["data"]
            self.admin_user_id = user_data.get("id")
            if user_data.get("role") == "admin" and user_data.get("email") == admin_data["email"]:
                self.log_test("Admin User Registration", True, f"Admin user registered successfully with ID: {self.admin_user_id}")
            else:
                self.log_test("Admin User Registration", False, "Admin user data incorrect", user_data)
        else:
            self.log_test("Admin User Registration", False, "Admin registration failed", result)
    
    async def test_user_login(self):
        """Test 4: User Login & JWT Tokens"""
        # Login client user
        client_login = {
            "email": "sarah.johnson@email.com",
            "password": "Test123!"
        }
        
        result = await self.make_request("POST", "/auth/login", client_login, expect_status=200)
        
        if result["success"]:
            token_data = result["data"]
            self.client_token = token_data.get("access_token")
            if self.client_token and token_data.get("token_type") == "bearer":
                self.log_test("Client User Login", True, "Client login successful, JWT token received")
            else:
                self.log_test("Client User Login", False, "Client login token invalid", token_data)
        else:
            self.log_test("Client User Login", False, "Client login failed", result)
        
        # Login admin user
        admin_login = {
            "email": "admin@salon.com",
            "password": "Admin123!"
        }
        
        result = await self.make_request("POST", "/auth/login", admin_login, expect_status=200)
        
        if result["success"]:
            token_data = result["data"]
            self.admin_token = token_data.get("access_token")
            if self.admin_token and token_data.get("token_type") == "bearer":
                self.log_test("Admin User Login", True, "Admin login successful, JWT token received")
            else:
                self.log_test("Admin User Login", False, "Admin login token invalid", token_data)
        else:
            self.log_test("Admin User Login", False, "Admin login failed", result)
    
    async def test_auth_me_endpoint(self):
        """Test 5: /auth/me endpoint with valid tokens"""
        # Test client token
        if self.client_token:
            result = await self.make_request("GET", "/auth/me", token=self.client_token)
            
            if result["success"]:
                user_data = result["data"]
                if user_data.get("email") == "sarah.johnson@email.com" and user_data.get("role") == "client":
                    self.log_test("Client Auth Me Endpoint", True, "Client user info retrieved correctly")
                else:
                    self.log_test("Client Auth Me Endpoint", False, "Client user info incorrect", user_data)
            else:
                self.log_test("Client Auth Me Endpoint", False, "Client auth/me failed", result)
        
        # Test admin token
        if self.admin_token:
            result = await self.make_request("GET", "/auth/me", token=self.admin_token)
            
            if result["success"]:
                user_data = result["data"]
                if user_data.get("email") == "admin@salon.com" and user_data.get("role") == "admin":
                    self.log_test("Admin Auth Me Endpoint", True, "Admin user info retrieved correctly")
                else:
                    self.log_test("Admin Auth Me Endpoint", False, "Admin user info incorrect", user_data)
            else:
                self.log_test("Admin Auth Me Endpoint", False, "Admin auth/me failed", result)
    
    async def test_time_slots_management(self):
        """Test 5: Time Slots Management (Admin only)"""
        if not self.admin_token:
            self.log_test("Time Slots Management", False, "No admin token available")
            return
        
        # Create time slot
        tomorrow = datetime.now() + timedelta(days=1)
        slot_data = {
            "date": tomorrow.strftime("%Y-%m-%dT%H:%M:%S"),
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "service_name": "Hair Cut & Style",
            "service_duration": 60,
            "price": 85.00
        }
        
        result = await self.make_request("POST", "/slots", slot_data, token=self.admin_token)
        
        if result["success"]:
            slot_response = result["data"]
            self.created_slot_id = slot_response.get("id")
            if slot_response.get("service_name") == "Hair Cut & Style" and slot_response.get("is_available"):
                self.log_test("Create Time Slot", True, f"Time slot created successfully with ID: {self.created_slot_id}")
            else:
                self.log_test("Create Time Slot", False, "Time slot data incorrect", slot_response)
        else:
            self.log_test("Create Time Slot", False, "Time slot creation failed", result)
        
        # Create another slot for testing
        slot_data2 = {
            "date": (tomorrow + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            "start_time": "14:00:00",
            "end_time": "15:30:00",
            "service_name": "Manicure & Pedicure",
            "service_duration": 90,
            "price": 65.00
        }
        
        await self.make_request("POST", "/slots", slot_data2, token=self.admin_token)
        
        # Get all time slots
        result = await self.make_request("GET", "/slots")
        
        if result["success"]:
            slots = result["data"]
            if isinstance(slots, list) and len(slots) >= 2:
                self.log_test("Get All Time Slots", True, f"Retrieved {len(slots)} time slots")
            else:
                self.log_test("Get All Time Slots", False, "Insufficient slots retrieved", slots)
        else:
            self.log_test("Get All Time Slots", False, "Get slots failed", result)
        
        # Update slot availability
        if self.created_slot_id:
            result = await self.make_request("PUT", f"/slots/{self.created_slot_id}?is_available=false", 
                                           token=self.admin_token)
            
            if result["success"]:
                updated_slot = result["data"]
                if not updated_slot.get("is_available"):
                    self.log_test("Update Slot Availability", True, "Slot availability updated successfully")
                else:
                    self.log_test("Update Slot Availability", False, "Slot availability not updated", updated_slot)
            else:
                self.log_test("Update Slot Availability", False, "Update slot failed", result)
        
        # Test admin endpoint access with client token
        result = await self.make_request("POST", "/slots", slot_data, token=self.client_token, expect_status=403)
        
        if result["success"] or result["status"] == 403:
            self.log_test("Admin Endpoint Access Control", True, "Client token correctly denied admin access")
        else:
            self.log_test("Admin Endpoint Access Control", False, "Access control failed", result)
    
    async def test_appointments_system(self):
        """Test 6: Appointments System"""
        if not self.client_token or not self.created_slot_id:
            self.log_test("Appointments System", False, "Missing client token or slot ID")
            return
        
        # First, make the slot available again for booking
        if self.admin_token:
            await self.make_request("PUT", f"/slots/{self.created_slot_id}?is_available=true", 
                                  token=self.admin_token)
        
        # Create appointment as client
        appointment_data = {
            "slot_id": self.created_slot_id,
            "notes": "First time customer, please call to confirm"
        }
        
        result = await self.make_request("POST", "/appointments", appointment_data, token=self.client_token)
        
        if result["success"]:
            appointment = result["data"]
            self.created_appointment_id = appointment.get("id")
            if appointment.get("slot_id") == self.created_slot_id and appointment.get("status") == "pending":
                self.log_test("Create Appointment", True, f"Appointment created successfully with ID: {self.created_appointment_id}")
            else:
                self.log_test("Create Appointment", False, "Appointment data incorrect", appointment)
        else:
            self.log_test("Create Appointment", False, "Appointment creation failed", result)
        
        # Verify slot becomes unavailable after booking
        result = await self.make_request("GET", "/slots")
        if result["success"]:
            slots = result["data"]
            booked_slot = next((s for s in slots if s["id"] == self.created_slot_id), None)
            if booked_slot and not booked_slot.get("is_available"):
                self.log_test("Slot Availability After Booking", True, "Slot correctly marked as unavailable")
            else:
                self.log_test("Slot Availability After Booking", False, "Slot still available after booking", booked_slot)
        
        # Get appointments as client
        result = await self.make_request("GET", "/appointments", token=self.client_token)
        
        if result["success"]:
            appointments = result["data"]
            if isinstance(appointments, list) and len(appointments) >= 1:
                client_appointment = appointments[0]
                if client_appointment.get("user_name") and client_appointment.get("slot_info"):
                    self.log_test("Get Client Appointments", True, f"Client retrieved {len(appointments)} appointments with populated data")
                else:
                    self.log_test("Get Client Appointments", False, "Appointment data not properly populated", client_appointment)
            else:
                self.log_test("Get Client Appointments", False, "No appointments retrieved for client", appointments)
        else:
            self.log_test("Get Client Appointments", False, "Get client appointments failed", result)
        
        # Get appointments as admin
        if self.admin_token:
            result = await self.make_request("GET", "/appointments", token=self.admin_token)
            
            if result["success"]:
                appointments = result["data"]
                if isinstance(appointments, list) and len(appointments) >= 1:
                    self.log_test("Get Admin Appointments", True, f"Admin retrieved {len(appointments)} appointments")
                else:
                    self.log_test("Get Admin Appointments", False, "No appointments retrieved for admin", appointments)
            else:
                self.log_test("Get Admin Appointments", False, "Get admin appointments failed", result)
        
        # Update appointment status as admin
        if self.admin_token and self.created_appointment_id:
            update_data = {
                "status": "confirmed",
                "notes": "Appointment confirmed by admin"
            }
            
            result = await self.make_request("PUT", f"/appointments/{self.created_appointment_id}", 
                                           update_data, token=self.admin_token)
            
            if result["success"]:
                updated_appointment = result["data"]
                if updated_appointment.get("status") == "confirmed":
                    self.log_test("Update Appointment Status", True, "Appointment status updated successfully")
                else:
                    self.log_test("Update Appointment Status", False, "Appointment status not updated", updated_appointment)
            else:
                self.log_test("Update Appointment Status", False, "Update appointment failed", result)
    
    async def test_reviews_system(self):
        """Test 7: Reviews System"""
        if not self.client_token:
            self.log_test("Reviews System", False, "No client token available")
            return
        
        # Create review as client
        review_data = {
            "rating": 5,
            "comment": "Excellent service! Sarah did an amazing job with my hair. The salon is clean and professional. Highly recommend!"
        }
        
        result = await self.make_request("POST", "/reviews", review_data, token=self.client_token)
        
        if result["success"]:
            review = result["data"]
            self.created_review_id = review.get("id")
            if review.get("rating") == 5 and review.get("status") == "pending":
                self.log_test("Create Review", True, f"Review created successfully with ID: {self.created_review_id}")
            else:
                self.log_test("Create Review", False, "Review data incorrect", review)
        else:
            self.log_test("Create Review", False, "Review creation failed", result)
        
        # Get reviews (public - should only show approved)
        result = await self.make_request("GET", "/reviews?approved_only=true")
        
        if result["success"]:
            reviews = result["data"]
            # Should be empty or only approved reviews
            pending_reviews = [r for r in reviews if r.get("status") == "pending"]
            if len(pending_reviews) == 0:
                self.log_test("Get Public Reviews", True, "Public reviews endpoint correctly filters pending reviews")
            else:
                self.log_test("Get Public Reviews", False, "Pending reviews visible in public endpoint", reviews)
        else:
            self.log_test("Get Public Reviews", False, "Get public reviews failed", result)
        
        # Get all reviews as admin
        if self.admin_token:
            result = await self.make_request("GET", "/reviews?approved_only=false", token=self.admin_token)
            
            if result["success"]:
                reviews = result["data"]
                if isinstance(reviews, list) and len(reviews) >= 1:
                    admin_review = reviews[0]
                    if admin_review.get("user_name"):
                        self.log_test("Get Admin Reviews", True, f"Admin retrieved {len(reviews)} reviews with user names")
                    else:
                        self.log_test("Get Admin Reviews", False, "Review user names not populated", admin_review)
                else:
                    self.log_test("Get Admin Reviews", False, "No reviews retrieved for admin", reviews)
            else:
                self.log_test("Get Admin Reviews", False, "Get admin reviews failed", result)
        
        # Update review status as admin
        if self.admin_token and self.created_review_id:
            update_data = {
                "status": "approved"
            }
            
            result = await self.make_request("PUT", f"/reviews/{self.created_review_id}", 
                                           update_data, token=self.admin_token)
            
            if result["success"]:
                updated_review = result["data"]
                if updated_review.get("status") == "approved":
                    self.log_test("Update Review Status", True, "Review status updated to approved")
                else:
                    self.log_test("Update Review Status", False, "Review status not updated", updated_review)
            else:
                self.log_test("Update Review Status", False, "Update review failed", result)
    
    async def test_database_operations(self):
        """Test 8: Database Operations & Data Persistence"""
        # Test data persistence by retrieving created data
        persistence_tests = []
        
        # Check user persistence
        if self.client_token:
            result = await self.make_request("GET", "/auth/me", token=self.client_token)
            if result["success"] and result["data"].get("email") == "sarah.johnson@email.com":
                persistence_tests.append("User data persisted")
            else:
                persistence_tests.append("User data NOT persisted")
        
        # Check slots persistence
        result = await self.make_request("GET", "/slots")
        if result["success"] and len(result["data"]) >= 2:
            persistence_tests.append("Time slots persisted")
        else:
            persistence_tests.append("Time slots NOT persisted")
        
        # Check appointments persistence
        if self.client_token:
            result = await self.make_request("GET", "/appointments", token=self.client_token)
            if result["success"] and len(result["data"]) >= 1:
                persistence_tests.append("Appointments persisted")
            else:
                persistence_tests.append("Appointments NOT persisted")
        
        # Check reviews persistence
        if self.admin_token:
            result = await self.make_request("GET", "/reviews?approved_only=false", token=self.admin_token)
            if result["success"] and len(result["data"]) >= 1:
                persistence_tests.append("Reviews persisted")
            else:
                persistence_tests.append("Reviews NOT persisted")
        
        # Test duplicate email registration (should fail)
        duplicate_user = {
            "email": "sarah.johnson@email.com",
            "password": "AnotherPass123!",
            "first_name": "Another",
            "last_name": "User"
        }
        
        result = await self.make_request("POST", "/auth/register", duplicate_user, expect_status=400)
        if result["status"] == 400:
            persistence_tests.append("Email uniqueness constraint working")
        else:
            persistence_tests.append("Email uniqueness constraint NOT working")
        
        success = all("NOT" not in test for test in persistence_tests)
        self.log_test("Database Operations & Persistence", success, 
                     f"Persistence tests: {', '.join(persistence_tests)}")
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🧪 Starting Comprehensive Backend Test Suite for Salon Booking System")
        print("=" * 80)
        print(f"Testing API at: {API_BASE_URL}")
        print("=" * 80)
        print()
        
        # Run tests in sequence
        await self.test_api_health_check()
        await self.test_ping_endpoint()
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_auth_me_endpoint()
        await self.test_time_slots_management()
        await self.test_appointments_system()
        await self.test_reviews_system()
        await self.test_database_operations()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['message']}")
            print()
        
        print("🎯 KEY FUNCTIONALITY TESTED:")
        print("  ✓ API Health Check")
        print("  ✓ User Registration (Client & Admin)")
        print("  ✓ JWT Authentication & Login")
        print("  ✓ Protected Endpoints (/auth/me)")
        print("  ✓ Time Slots Management (Admin Only)")
        print("  ✓ Role-based Access Control")
        print("  ✓ Appointments CRUD Operations")
        print("  ✓ Slot Availability Management")
        print("  ✓ Reviews System")
        print("  ✓ Database Persistence & Constraints")
        print()
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    try:
        async with SalonBookingTester() as tester:
            success = await tester.run_all_tests()
            return 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)