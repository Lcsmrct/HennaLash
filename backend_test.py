#!/usr/bin/env python3
"""
Backend API Testing Suite for HennaLash Salon
Testing priority corrections for Render deployment
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
import sys

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test data
ADMIN_CREDENTIALS = {
    "email": "newadmin@salon.com",
    "password": "admin123"
}

CLIENT_CREDENTIALS = {
    "email": "client@test.com", 
    "password": "password123"
}

class BackendTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": f"{response_time:.3f}s" if response_time > 0 else "N/A"
        }
        self.test_results.append(result)
        print(f"{status} {test_name} ({response_time:.3f}s) - {details}")
    
    async def make_request(self, method: str, url: str, headers: Dict = None, json_data: Dict = None, timeout: int = 10) -> tuple:
        """Make HTTP request and return (success, response_data, response_time)"""
        start_time = time.time()
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_time = time.time() - start_time
                
                if response.content_type == 'application/json':
                    data = await response.json()
                else:
                    data = await response.text()
                
                return response.status, data, response_time
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            return 408, {"error": "Request timeout"}, response_time
        except Exception as e:
            response_time = time.time() - start_time
            return 500, {"error": str(e)}, response_time
    
    async def authenticate(self, credentials: Dict, user_type: str) -> Optional[str]:
        """Authenticate and return token"""
        status, data, response_time = await self.make_request(
            "POST", 
            f"{API_BASE}/login",
            json_data=credentials
        )
        
        if status == 200 and "access_token" in data:
            token = data["access_token"]
            self.log_test(f"Authentication {user_type}", True, f"Token obtained", response_time)
            return token
        else:
            self.log_test(f"Authentication {user_type}", False, f"Status: {status}, Data: {data}", response_time)
            return None

    # ==========================================
    # PRIORITY TESTS - RENDER DEPLOYMENT FIXES
    # ==========================================
    
    async def test_root_routes(self):
        """Test 1: Root routes GET / and HEAD / (must return 200)"""
        print("\n🎯 TESTING ROOT ROUTES (Render deployment fix)")
        
        # Test GET /
        status, data, response_time = await self.make_request("GET", BACKEND_URL)
        success = status == 200 and isinstance(data, dict) and data.get("status") == "ok"
        self.log_test("Root GET /", success, f"Status: {status}, Response: {data}", response_time)
        
        # Test HEAD /
        status, data, response_time = await self.make_request("HEAD", BACKEND_URL)
        success = status == 200
        self.log_test("Root HEAD /", success, f"Status: {status}", response_time)
    
    async def test_health_check(self):
        """Test 2: Health check GET /health (must confirm DB connected)"""
        print("\n🎯 TESTING HEALTH CHECK (DB connection verification)")
        
        status, data, response_time = await self.make_request("GET", f"{BACKEND_URL}/health")
        
        if status == 200 and isinstance(data, dict):
            db_connected = data.get("database") == "connected"
            has_status = data.get("status") == "healthy"
            success = db_connected and has_status
            details = f"Status: {data.get('status')}, DB: {data.get('database')}"
        else:
            success = False
            details = f"Status: {status}, Data: {data}"
        
        self.log_test("Health Check /health", success, details, response_time)
    
    async def test_maintenance_endpoint(self):
        """Test 3: Maintenance endpoint GET /api/maintenance (must work without 400 error)"""
        print("\n🎯 TESTING MAINTENANCE ENDPOINT (No 400 error)")
        
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/maintenance")
        
        if status == 200 and isinstance(data, dict):
            has_maintenance_field = "is_maintenance" in data
            has_message_field = "message" in data
            success = has_maintenance_field and has_message_field
            details = f"is_maintenance: {data.get('is_maintenance')}, message present: {has_message_field}"
        else:
            success = False
            details = f"Status: {status}, Data: {data}"
        
        self.log_test("Maintenance GET /api/maintenance", success, details, response_time)
    
    async def test_authentication_no_regression(self):
        """Test 4: Authentication admin/client (verify no regression)"""
        print("\n🎯 TESTING AUTHENTICATION (No regression)")
        
        # Test admin login
        self.admin_token = await self.authenticate(ADMIN_CREDENTIALS, "Admin")
        
        # Create a test client user first
        client_user_data = {
            "email": CLIENT_CREDENTIALS["email"],
            "password": CLIENT_CREDENTIALS["password"],
            "first_name": "Test",
            "last_name": "Client",
            "phone": "1234567890"
        }
        
        # Try to register the client (ignore if already exists)
        status, data, response_time = await self.make_request(
            "POST", 
            f"{API_BASE}/register",
            json_data=client_user_data
        )
        
        if status == 201:
            self.log_test("Client Registration", True, "Test client created", response_time)
        elif status == 400 and "already registered" in str(data):
            self.log_test("Client Registration", True, "Test client already exists", response_time)
        else:
            self.log_test("Client Registration", False, f"Status: {status}, Data: {data}", response_time)
        
        # Test client login  
        self.client_token = await self.authenticate(CLIENT_CREDENTIALS, "Client")
        
        # Test /api/me endpoint with admin token
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            status, data, response_time = await self.make_request("GET", f"{API_BASE}/me", headers=headers)
            success = status == 200 and isinstance(data, dict) and "email" in data
            self.log_test("Admin /api/me", success, f"Status: {status}, Email: {data.get('email') if isinstance(data, dict) else 'N/A'}", response_time)
    
    async def test_critical_apis(self):
        """Test 5: Critical APIs - Slots, Appointments, Reviews (functionality preserved)"""
        print("\n🎯 TESTING CRITICAL APIS (Functionality preserved)")
        
        if not self.admin_token:
            self.log_test("Critical APIs", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/slots
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/slots", headers=headers)
        success = status == 200 and isinstance(data, list)
        self.log_test("GET /api/slots", success, f"Status: {status}, Slots count: {len(data) if isinstance(data, list) else 'N/A'}", response_time)
        
        # Test GET /api/appointments
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/appointments", headers=headers)
        success = status == 200 and isinstance(data, list)
        self.log_test("GET /api/appointments", success, f"Status: {status}, Appointments count: {len(data) if isinstance(data, list) else 'N/A'}", response_time)
        
        # Test GET /api/reviews (admin)
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/reviews", headers=headers)
        success = status == 200 and isinstance(data, list)
        self.log_test("GET /api/reviews (admin)", success, f"Status: {status}, Reviews count: {len(data) if isinstance(data, list) else 'N/A'}", response_time)
        
        # Test GET /api/reviews?approved_only=true (public)
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/reviews?approved_only=true")
        success = status == 200 and isinstance(data, list)
        self.log_test("GET /api/reviews (public)", success, f"Status: {status}, Public reviews count: {len(data) if isinstance(data, list) else 'N/A'}", response_time)
    
    # ==========================================
    # ADDITIONAL COMPREHENSIVE TESTS
    # ==========================================
    
    async def test_ping_endpoints(self):
        """Test ping endpoints (health check)"""
        print("\n📡 TESTING PING ENDPOINTS")
        
        # Test GET /api/ping
        status, data, response_time = await self.make_request("GET", f"{API_BASE}/ping")
        success = status == 200 and isinstance(data, dict) and data.get("status") == "Ok"
        self.log_test("GET /api/ping", success, f"Status: {status}, Response: {data}", response_time)
        
        # Test HEAD /api/ping
        status, data, response_time = await self.make_request("HEAD", f"{API_BASE}/ping")
        success = status == 200
        self.log_test("HEAD /api/ping", success, f"Status: {status}", response_time)
    
    async def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🌐 TESTING CORS CONFIGURATION")
        
        # Test OPTIONS request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        status, data, response_time = await self.make_request("OPTIONS", f"{API_BASE}/login", headers=headers)
        success = status in [200, 204]
        self.log_test("CORS OPTIONS", success, f"Status: {status}", response_time)
    
    async def test_slot_creation_simplified(self):
        """Test simplified slot creation (single time field + auto end_time)"""
        print("\n⏰ TESTING SIMPLIFIED SLOT CREATION")
        
        if not self.admin_token:
            self.log_test("Slot Creation", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a test slot
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "14:30"  # Single time field
        }
        
        status, data, response_time = await self.make_request(
            "POST", 
            f"{API_BASE}/slots",
            headers=headers,
            json_data=slot_data
        )
        
        if status == 200 and isinstance(data, dict):  # Changed from 201 to 200
            has_start_time = "start_time" in data
            has_end_time = "end_time" in data
            correct_times = data.get("start_time") == "14:30" and data.get("end_time") == "15:30"
            success = has_start_time and has_end_time and correct_times
            details = f"Start: {data.get('start_time')}, End: {data.get('end_time')}"
        else:
            success = False
            details = f"Status: {status}, Data: {data}"
        
        self.log_test("Simplified Slot Creation", success, details, response_time)
    
    async def test_email_service_configuration(self):
        """Test email service configuration (check if credentials are set)"""
        print("\n📧 TESTING EMAIL SERVICE CONFIGURATION")
        
        # Check if email environment variables are set by reading .env file
        try:
            with open("/app/backend/.env", "r") as f:
                env_content = f.read()
                gmail_username = "GMAIL_USERNAME=" in env_content
                gmail_password = "GMAIL_PASSWORD=" in env_content
                
            if gmail_username and gmail_password:
                success = True
                details = "Gmail credentials configured in .env file"
            else:
                success = False
                details = "Gmail credentials not found in .env file"
        except Exception as e:
            success = False
            details = f"Could not read .env file: {str(e)}"
        
        self.log_test("Email Configuration", success, details)
    
    async def test_performance_optimization(self):
        """Test performance optimization (background tasks)"""
        print("\n⚡ TESTING PERFORMANCE OPTIMIZATION")
        
        if not self.client_token:
            self.log_test("Performance Test", False, "No client token available")
            return
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        
        # Test appointment creation performance (should be fast with background tasks)
        # First get available slots
        status, slots_data, _ = await self.make_request("GET", f"{API_BASE}/slots?available_only=true")
        
        if status != 200 or not isinstance(slots_data, list) or len(slots_data) == 0:
            self.log_test("Performance Test", False, "No available slots for testing")
            return
        
        # Use first available slot
        slot = slots_data[0]
        appointment_data = {
            "slot_id": slot["id"],
            "service_name": "Très simple",
            "service_price": 5,
            "notes": "Test appointment for performance"
        }
        
        start_time = time.time()
        status, data, response_time = await self.make_request(
            "POST",
            f"{API_BASE}/appointments",
            headers=headers,
            json_data=appointment_data
        )
        
        # Performance should be under 2 seconds (background email tasks)
        performance_good = response_time < 2.0
        success = status == 201 and performance_good
        
        details = f"Status: {status}, Time: {response_time:.3f}s, Performance: {'Good' if performance_good else 'Slow'}"
        self.log_test("Appointment Creation Performance", success, details, response_time)
    
    async def run_all_tests(self):
        """Run all tests in priority order"""
        print("🚀 STARTING BACKEND API TESTS - RENDER DEPLOYMENT CORRECTIONS")
        print("=" * 80)
        
        # Priority tests for Render deployment
        await self.test_root_routes()
        await self.test_health_check()
        await self.test_maintenance_endpoint()
        await self.test_authentication_no_regression()
        await self.test_critical_apis()
        
        # Additional comprehensive tests
        await self.test_ping_endpoints()
        await self.test_cors_configuration()
        await self.test_slot_creation_simplified()
        await self.test_email_service_configuration()
        await self.test_performance_optimization()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 PRIORITY RENDER DEPLOYMENT TESTS:")
        priority_tests = [
            "Root GET /", "Root HEAD /", "Health Check /health", 
            "Maintenance GET /api/maintenance", "Authentication Admin", "Authentication Client"
        ]
        
        priority_results = [r for r in self.test_results if any(p in r["test"] for p in priority_tests)]
        priority_passed = sum(1 for r in priority_results if r["success"])
        
        print(f"Priority Tests Passed: {priority_passed}/{len(priority_results)}")
        
        if priority_passed == len(priority_results):
            print("🎉 ALL PRIORITY RENDER DEPLOYMENT FIXES WORKING!")
        else:
            print("🚨 SOME PRIORITY RENDER DEPLOYMENT FIXES NEED ATTENTION!")
        
        return passed_tests, failed_tests

async def main():
    """Main test runner"""
    async with BackendTester() as tester:
        passed, failed = await tester.run_all_tests()
        
        # Exit with appropriate code
        if failed > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())