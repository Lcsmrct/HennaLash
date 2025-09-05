#!/usr/bin/env python3
"""
Specific Bug Fixes Test Suite for Salon Booking System
Tests the 3 specific bug fixes mentioned in the review request:
1. Logout Redirection
2. Reviews Display (approved reviews without authentication)
3. Slot Availability Bug
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://client-booking-2.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class BugFixesTester:
    def __init__(self):
        self.session = None
        self.client_token = None
        self.admin_token = None
        self.test_slot_id = None
        self.test_review_id = None
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
    
    async def setup_test_data(self):
        """Setup test data for bug fix tests"""
        print("🔧 Setting up test data...")
        
        # Login as existing users
        client_login = {
            "email": "sarah.johnson@email.com",
            "password": "Test123!"
        }
        
        result = await self.make_request("POST", "/auth/login", client_login)
        if result["success"]:
            self.client_token = result["data"]["access_token"]
            print("✅ Client login successful")
        else:
            print("❌ Client login failed")
            return False
        
        admin_login = {
            "email": "admin@salon.com",
            "password": "Admin123!"
        }
        
        result = await self.make_request("POST", "/auth/login", admin_login)
        if result["success"]:
            self.admin_token = result["data"]["access_token"]
            print("✅ Admin login successful")
        else:
            print("❌ Admin login failed")
            return False
        
        return True
    
    async def test_logout_redirection_fix(self):
        """Test 1: Logout Redirection Fix"""
        print("🔍 Testing Logout Redirection Fix...")
        
        # This is a frontend test, but we can verify the backend logout endpoint works
        # and that the frontend code has the correct redirection
        
        # Check if logout function in frontend includes window.location.href = '/'
        try:
            with open('/app/frontend/src/context/AuthContext.jsx', 'r') as f:
                auth_context_content = f.read()
                
            if 'window.location.href = \'/\';' in auth_context_content:
                self.log_test("Logout Redirection Code Check", True, 
                             "Frontend logout function includes window.location.href = '/'")
            else:
                self.log_test("Logout Redirection Code Check", False, 
                             "Frontend logout function missing redirection code")
        except Exception as e:
            self.log_test("Logout Redirection Code Check", False, 
                         f"Could not check frontend code: {str(e)}")
        
        # Test that auth/me endpoint works (validates token functionality)
        if self.client_token:
            result = await self.make_request("GET", "/auth/me", token=self.client_token)
            if result["success"]:
                self.log_test("Auth Token Validation", True, 
                             "Auth tokens work correctly for logout functionality")
            else:
                self.log_test("Auth Token Validation", False, 
                             "Auth token validation failed", result)
    
    async def test_reviews_display_fix(self):
        """Test 2: Reviews Display Fix - Approved reviews should be accessible without authentication"""
        print("🔍 Testing Reviews Display Fix...")
        
        # First, create a review and approve it
        if self.client_token and self.admin_token:
            # Create a review as client
            review_data = {
                "rating": 5,
                "comment": "Excellent service for bug fix testing! Very professional and clean salon."
            }
            
            result = await self.make_request("POST", "/reviews", review_data, token=self.client_token)
            if result["success"]:
                self.test_review_id = result["data"]["id"]
                print(f"✅ Test review created with ID: {self.test_review_id}")
                
                # Approve the review as admin
                update_data = {"status": "approved"}
                result = await self.make_request("PUT", f"/reviews/{self.test_review_id}", 
                                               update_data, token=self.admin_token)
                if result["success"]:
                    print("✅ Test review approved by admin")
                else:
                    print("❌ Failed to approve test review")
                    return
            else:
                print("❌ Failed to create test review")
                return
        
        # Test 1: GET /api/reviews?approved_only=true WITHOUT authentication
        result = await self.make_request("GET", "/reviews?approved_only=true")
        
        if result["success"]:
            reviews = result["data"]
            if isinstance(reviews, list):
                # Check if we have approved reviews
                approved_reviews = [r for r in reviews if r.get("status") == "approved"]
                if len(approved_reviews) > 0:
                    self.log_test("Public Approved Reviews Access", True, 
                                 f"Successfully retrieved {len(approved_reviews)} approved reviews without authentication")
                else:
                    self.log_test("Public Approved Reviews Access", False, 
                                 "No approved reviews found in public endpoint")
            else:
                self.log_test("Public Approved Reviews Access", False, 
                             "Invalid response format from reviews endpoint", reviews)
        else:
            self.log_test("Public Approved Reviews Access", False, 
                         "Failed to access approved reviews without authentication", result)
        
        # Test 2: Verify that pending reviews are NOT visible in public endpoint
        result = await self.make_request("GET", "/reviews?approved_only=true")
        
        if result["success"]:
            reviews = result["data"]
            pending_reviews = [r for r in reviews if r.get("status") == "pending"]
            if len(pending_reviews) == 0:
                self.log_test("Public Reviews Security", True, 
                             "Pending reviews correctly hidden from public endpoint")
            else:
                self.log_test("Public Reviews Security", False, 
                             f"Found {len(pending_reviews)} pending reviews in public endpoint - security issue!")
        
        # Test 3: Verify admin can still see all reviews
        if self.admin_token:
            result = await self.make_request("GET", "/reviews?approved_only=false", token=self.admin_token)
            
            if result["success"]:
                all_reviews = result["data"]
                if isinstance(all_reviews, list) and len(all_reviews) > 0:
                    self.log_test("Admin Reviews Access", True, 
                                 f"Admin can access all {len(all_reviews)} reviews including pending ones")
                else:
                    self.log_test("Admin Reviews Access", False, 
                                 "Admin cannot access all reviews")
            else:
                self.log_test("Admin Reviews Access", False, 
                             "Admin reviews access failed", result)
    
    async def test_slot_availability_fix(self):
        """Test 3: Slot Availability Bug Fix"""
        print("🔍 Testing Slot Availability Bug Fix...")
        
        if not self.admin_token or not self.client_token:
            self.log_test("Slot Availability Test Setup", False, "Missing required tokens")
            return
        
        # Step 1: Admin creates a new slot
        tomorrow = datetime.now() + timedelta(days=2)
        slot_data = {
            "date": tomorrow.strftime("%Y-%m-%dT%H:%M:%S"),
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "service_name": "Bug Fix Test Service",
            "service_duration": 60,
            "price": 75.00
        }
        
        result = await self.make_request("POST", "/slots", slot_data, token=self.admin_token)
        
        if result["success"]:
            self.test_slot_id = result["data"]["id"]
            if result["data"]["is_available"]:
                self.log_test("Admin Creates Available Slot", True, 
                             f"Admin created available slot with ID: {self.test_slot_id}")
            else:
                self.log_test("Admin Creates Available Slot", False, 
                             "Newly created slot is not available")
                return
        else:
            self.log_test("Admin Creates Available Slot", False, 
                         "Failed to create test slot", result)
            return
        
        # Step 2: Verify slot appears in available slots list
        result = await self.make_request("GET", "/slots?available_only=true")
        
        if result["success"]:
            available_slots = result["data"]
            test_slot = next((s for s in available_slots if s["id"] == self.test_slot_id), None)
            if test_slot:
                self.log_test("Slot Appears in Available List", True, 
                             "New slot correctly appears in available slots list")
            else:
                self.log_test("Slot Appears in Available List", False, 
                             "New slot does not appear in available slots list")
        else:
            self.log_test("Slot Appears in Available List", False, 
                         "Failed to get available slots", result)
        
        # Step 3: Client books the slot
        appointment_data = {
            "slot_id": self.test_slot_id,
            "notes": "Bug fix test appointment"
        }
        
        result = await self.make_request("POST", "/appointments", appointment_data, token=self.client_token)
        
        if result["success"]:
            appointment_id = result["data"]["id"]
            self.log_test("Client Books Available Slot", True, 
                         f"Client successfully booked slot, appointment ID: {appointment_id}")
        else:
            self.log_test("Client Books Available Slot", False, 
                         "Client failed to book available slot", result)
            return
        
        # Step 4: Verify slot is immediately marked as unavailable
        result = await self.make_request("GET", "/slots")
        
        if result["success"]:
            all_slots = result["data"]
            booked_slot = next((s for s in all_slots if s["id"] == self.test_slot_id), None)
            if booked_slot and not booked_slot["is_available"]:
                self.log_test("Slot Marked Unavailable After Booking", True, 
                             "Slot correctly marked as unavailable immediately after booking")
            else:
                self.log_test("Slot Marked Unavailable After Booking", False, 
                             "Slot still available after booking - BUG!", booked_slot)
        else:
            self.log_test("Slot Marked Unavailable After Booking", False, 
                         "Failed to check slot status after booking", result)
        
        # Step 5: Verify slot no longer appears in available slots list
        result = await self.make_request("GET", "/slots?available_only=true")
        
        if result["success"]:
            available_slots = result["data"]
            test_slot = next((s for s in available_slots if s["id"] == self.test_slot_id), None)
            if not test_slot:
                self.log_test("Booked Slot Removed from Available List", True, 
                             "Booked slot correctly removed from available slots list")
            else:
                self.log_test("Booked Slot Removed from Available List", False, 
                             "Booked slot still appears in available slots list - BUG!")
        else:
            self.log_test("Booked Slot Removed from Available List", False, 
                         "Failed to check available slots list", result)
        
        # Step 6: Test concurrent booking protection (another client tries to book same slot)
        # Create another client for this test
        another_client_data = {
            "email": "test.concurrent@email.com",
            "password": "Test123!",
            "first_name": "Test",
            "last_name": "Concurrent",
            "phone": "+1-555-9999"
        }
        
        # Register another client (might fail if already exists, that's ok)
        await self.make_request("POST", "/auth/register", another_client_data)
        
        # Login as another client
        another_client_login = {
            "email": "test.concurrent@email.com",
            "password": "Test123!"
        }
        
        result = await self.make_request("POST", "/auth/login", another_client_login)
        if result["success"]:
            another_client_token = result["data"]["access_token"]
            
            # Try to book the same slot
            result = await self.make_request("POST", "/appointments", appointment_data, 
                                           token=another_client_token, expect_status=404)
            
            if result["status"] in [400, 404] and "not available" in str(result.get("data", {})):
                self.log_test("Concurrent Booking Protection", True, 
                             "Second client correctly prevented from booking already booked slot")
            else:
                self.log_test("Concurrent Booking Protection", False, 
                             "Second client was able to book already booked slot - BUG!", result)
        else:
            self.log_test("Concurrent Booking Protection", False, 
                         "Could not test concurrent booking - login failed")
    
    async def run_bug_fixes_tests(self):
        """Run all bug fix tests"""
        print("🐛 Starting Bug Fixes Test Suite for Salon Booking System")
        print("=" * 80)
        print(f"Testing API at: {API_BASE_URL}")
        print("Testing 3 specific bug fixes:")
        print("1. Logout Redirection (window.location.href = '/')")
        print("2. Reviews Display (GET /api/reviews?approved_only=true without auth)")
        print("3. Slot Availability Bug (slots marked unavailable after booking)")
        print("=" * 80)
        print()
        
        # Setup test data
        if not await self.setup_test_data():
            print("❌ Failed to setup test data")
            return False
        
        print()
        
        # Run specific bug fix tests
        await self.test_logout_redirection_fix()
        await self.test_reviews_display_fix()
        await self.test_slot_availability_fix()
        
        # Summary
        print("=" * 80)
        print("🐛 BUG FIXES TEST SUMMARY")
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
        
        print("🎯 BUG FIXES TESTED:")
        print("  1. ✓ Logout Redirection Fix")
        print("  2. ✓ Reviews Display Fix (Public Access)")
        print("  3. ✓ Slot Availability Bug Fix")
        print()
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    try:
        async with BugFixesTester() as tester:
            success = await tester.run_bug_fixes_tests()
            return 0 if success else 1
    except Exception as e:
        print(f"❌ Bug fixes test suite failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)