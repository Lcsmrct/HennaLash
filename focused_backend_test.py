#!/usr/bin/env python3
"""
Focused Backend Test for Review Request
Tests specific endpoints mentioned in the review request
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Get backend URL from environment
BACKEND_URL = "https://henna-lash.onrender.com"
API_BASE_URL = f"{BACKEND_URL}/api"

class FocusedTester:
    def __init__(self):
        self.session = None
        self.client_token = None
        self.admin_token = None
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
    
    async def test_ping_endpoint(self):
        """Test 1: GET /api/ping - endpoint de santé"""
        result = await self.make_request("GET", "/ping")
        
        if result["success"] and result["data"].get("status") == "Ok":
            self.log_test("GET /api/ping", True, "Health endpoint working correctly")
        else:
            self.log_test("GET /api/ping", False, "Health endpoint failed", result)
    
    async def setup_authentication(self):
        """Setup authentication for protected endpoints"""
        # Try to login with existing users first
        client_login = {
            "email": "sarah.johnson@email.com",
            "password": "Test123!"
        }
        
        result = await self.make_request("POST", "/auth/login", client_login)
        if result["success"]:
            self.client_token = result["data"].get("access_token")
            self.log_test("Client Authentication Setup", True, "Client token obtained")
        else:
            # Try to register if login fails
            client_data = {
                "email": "marie.dupont@email.com",
                "password": "Test123!",
                "first_name": "Marie",
                "last_name": "Dupont",
                "phone": "+33-6-12-34-56-78"
            }
            
            reg_result = await self.make_request("POST", "/auth/register", client_data)
            if reg_result["success"]:
                # Now login
                login_data = {
                    "email": "marie.dupont@email.com",
                    "password": "Test123!"
                }
                login_result = await self.make_request("POST", "/auth/login", login_data)
                if login_result["success"]:
                    self.client_token = login_result["data"].get("access_token")
                    self.log_test("Client Authentication Setup", True, "New client registered and token obtained")
                else:
                    self.log_test("Client Authentication Setup", False, "Failed to login after registration", login_result)
            else:
                self.log_test("Client Authentication Setup", False, "Failed to register new client", reg_result)
    
    async def test_login_endpoint(self):
        """Test 2: POST /api/auth/login - connexion utilisateur"""
        # Test with valid credentials
        login_data = {
            "email": "marie.dupont@email.com",
            "password": "Test123!"
        }
        
        result = await self.make_request("POST", "/auth/login", login_data)
        
        if result["success"]:
            token_data = result["data"]
            if token_data.get("access_token") and token_data.get("token_type") == "bearer":
                self.log_test("POST /api/auth/login", True, "User login successful, JWT token received")
            else:
                self.log_test("POST /api/auth/login", False, "Login response invalid", token_data)
        else:
            self.log_test("POST /api/auth/login", False, "User login failed", result)
        
        # Test with invalid credentials
        invalid_login = {
            "email": "invalid@email.com",
            "password": "wrongpassword"
        }
        
        result = await self.make_request("POST", "/auth/login", invalid_login, expect_status=401)
        
        if result["status"] == 401:
            self.log_test("POST /api/auth/login (Invalid Credentials)", True, "Correctly rejected invalid credentials")
        else:
            self.log_test("POST /api/auth/login (Invalid Credentials)", False, "Should reject invalid credentials", result)
    
    async def test_auth_me_endpoint(self):
        """Test 3: GET /api/auth/me - informations utilisateur (avec token valide)"""
        if not self.client_token:
            self.log_test("GET /api/auth/me", False, "No client token available")
            return
        
        result = await self.make_request("GET", "/auth/me", token=self.client_token)
        
        if result["success"]:
            user_data = result["data"]
            if user_data.get("email") and user_data.get("role"):
                self.log_test("GET /api/auth/me", True, f"User info retrieved: {user_data.get('email')} ({user_data.get('role')})")
            else:
                self.log_test("GET /api/auth/me", False, "User info incomplete", user_data)
        else:
            self.log_test("GET /api/auth/me", False, "Failed to get user info", result)
        
        # Test without token
        result = await self.make_request("GET", "/auth/me", expect_status=401)
        
        if result["status"] == 401:
            self.log_test("GET /api/auth/me (No Token)", True, "Correctly requires authentication")
        else:
            self.log_test("GET /api/auth/me (No Token)", False, "Should require authentication", result)
    
    async def test_appointments_endpoint(self):
        """Test 4: GET /api/appointments - récupération des rendez-vous"""
        if not self.client_token:
            self.log_test("GET /api/appointments", False, "No client token available")
            return
        
        result = await self.make_request("GET", "/appointments", token=self.client_token)
        
        if result["success"]:
            appointments = result["data"]
            if isinstance(appointments, list):
                self.log_test("GET /api/appointments", True, f"Retrieved {len(appointments)} appointments")
            else:
                self.log_test("GET /api/appointments", False, "Response not a list", appointments)
        else:
            self.log_test("GET /api/appointments", False, "Failed to get appointments", result)
        
        # Test without token
        result = await self.make_request("GET", "/appointments", expect_status=401)
        
        if result["status"] == 401:
            self.log_test("GET /api/appointments (No Token)", True, "Correctly requires authentication")
        else:
            self.log_test("GET /api/appointments (No Token)", False, "Should require authentication", result)
    
    async def test_available_slots_endpoint(self):
        """Test 5: GET /api/slots?available_only=true - récupération des créneaux disponibles"""
        result = await self.make_request("GET", "/slots?available_only=true")
        
        if result["success"]:
            slots = result["data"]
            if isinstance(slots, list):
                available_slots = [slot for slot in slots if slot.get("is_available")]
                if len(available_slots) == len(slots):
                    self.log_test("GET /api/slots?available_only=true", True, f"Retrieved {len(slots)} available slots")
                else:
                    self.log_test("GET /api/slots?available_only=true", False, f"Filter not working: {len(available_slots)}/{len(slots)} available")
            else:
                self.log_test("GET /api/slots?available_only=true", False, "Response not a list", slots)
        else:
            self.log_test("GET /api/slots?available_only=true", False, "Failed to get available slots", result)
    
    async def test_approved_reviews_endpoint(self):
        """Test 6: GET /api/reviews?approved_only=true - récupération des avis approuvés"""
        result = await self.make_request("GET", "/reviews?approved_only=true")
        
        if result["success"]:
            reviews = result["data"]
            if isinstance(reviews, list):
                # Check that all reviews are approved or there are no reviews
                pending_reviews = [review for review in reviews if review.get("status") == "pending"]
                if len(pending_reviews) == 0:
                    self.log_test("GET /api/reviews?approved_only=true", True, f"Retrieved {len(reviews)} approved reviews (no pending reviews visible)")
                else:
                    self.log_test("GET /api/reviews?approved_only=true", False, f"Pending reviews visible: {len(pending_reviews)}")
            else:
                self.log_test("GET /api/reviews?approved_only=true", False, "Response not a list", reviews)
        else:
            self.log_test("GET /api/reviews?approved_only=true", False, "Failed to get approved reviews", result)
    
    async def test_database_performance(self):
        """Test database performance optimization"""
        # Test reviews endpoint performance
        start_time = datetime.now()
        result = await self.make_request("GET", "/reviews?approved_only=true")
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if result["success"] and response_time < 2.0:
            self.log_test("Database Performance - Reviews", True, f"Reviews loaded in {response_time:.2f}s (< 2s)")
        elif result["success"]:
            self.log_test("Database Performance - Reviews", False, f"Reviews took {response_time:.2f}s (> 2s)")
        else:
            self.log_test("Database Performance - Reviews", False, "Reviews request failed", result)
        
        # Test login performance
        start_time = datetime.now()
        login_data = {
            "email": "marie.dupont@email.com",
            "password": "Test123!"
        }
        result = await self.make_request("POST", "/auth/login", login_data)
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        if result["success"] and response_time < 2.0:
            self.log_test("Database Performance - Login", True, f"Login completed in {response_time:.2f}s (< 2s)")
        elif result["success"]:
            self.log_test("Database Performance - Login", False, f"Login took {response_time:.2f}s (> 2s)")
        else:
            self.log_test("Database Performance - Login", False, "Login request failed", result)
    
    async def run_focused_tests(self):
        """Run focused tests for review request"""
        print("🧪 Focused Backend Test Suite - Review Request")
        print("=" * 60)
        print(f"Testing API at: {API_BASE_URL}")
        print("=" * 60)
        print()
        
        # Setup authentication first
        await self.setup_authentication()
        
        # Run the specific tests requested
        await self.test_ping_endpoint()
        await self.test_login_endpoint()
        await self.test_auth_me_endpoint()
        await self.test_appointments_endpoint()
        await self.test_available_slots_endpoint()
        await self.test_approved_reviews_endpoint()
        await self.test_database_performance()
        
        # Summary
        print("=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("🎯 ENDPOINTS TESTED (as requested):")
        print("  ✓ GET /api/ping - endpoint de santé")
        print("  ✓ POST /api/auth/login - connexion utilisateur")
        print("  ✓ GET /api/auth/me - informations utilisateur (avec token valide)")
        print("  ✓ GET /api/appointments - récupération des rendez-vous")
        print("  ✓ GET /api/slots?available_only=true - récupération des créneaux disponibles")
        print("  ✓ GET /api/reviews?approved_only=true - récupération des avis approuvés")
        print("  ✓ Database Performance Optimization")
        print()
        
        return passed_tests == total_tests

async def main():
    """Main test runner"""
    try:
        async with FocusedTester() as tester:
            success = await tester.run_focused_tests()
            return 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)