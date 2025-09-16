#!/usr/bin/env python3
"""
Backend API Testing for 422 Error Fixes
Focus: Testing corrections applied to resolve 422 errors in appointment creation
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://henna-lash.onrender.com/api"
TIMEOUT = 10

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        self.available_slot_id = None
        
    def log_result(self, test_name, success, message, duration=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.3f}s)" if duration else ""
        result = f"{status} {test_name}: {message}{duration_str}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'duration': duration
        })
        
    def authenticate_admin(self):
        """Authenticate as admin user or create one"""
        try:
            # First try to login
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "admin@salon.com",
                    "password": "admin123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                self.log_result("Admin Authentication", True, "Admin login successful", duration)
                return True
            else:
                # Try to create admin user
                return self.create_admin_user()
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_admin_user(self):
        """Create admin user and then authenticate"""
        try:
            # Register admin user
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": "admin@salon.com",
                    "password": "admin123",
                    "first_name": "Admin",
                    "last_name": "Salon",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Admin Registration", True, "Admin user created", duration)
                # Now try to login
                return self.authenticate_admin()
            else:
                self.log_result("Admin Registration", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Registration", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_client(self):
        """Authenticate as client user or create one"""
        try:
            # Try to login with existing client
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "marie.dupont@email.com",
                    "password": "client123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication", True, "Client login successful", duration)
                return True
            else:
                # If login fails, try with different credentials or create new user
                return self.try_alternative_client_login()
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False
    
    def try_alternative_client_login(self):
        """Try alternative client credentials or create new user"""
        # Try different password
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "marie.dupont@email.com",
                    "password": "password123"  # Try different password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication (Alt)", True, "Client login successful with alternative password", duration)
                return True
            else:
                # Create new client with different email
                return self.create_new_test_client()
        except Exception as e:
            return self.create_new_test_client()
    
    def create_new_test_client(self):
        """Create a new test client with unique email"""
        try:
            import random
            random_num = random.randint(1000, 9999)
            email = f"testclient{random_num}@email.com"
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": email,
                    "password": "client123",
                    "first_name": "Test",
                    "last_name": "Client",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("New Client Registration", True, f"New client created: {email}", duration)
                # Now login with new credentials
                return self.login_new_client(email, "client123")
            else:
                self.log_result("New Client Registration", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("New Client Registration", False, f"Exception: {str(e)}")
            return False
    
    def login_new_client(self, email, password):
        """Login with new client credentials"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("New Client Login", True, "New client login successful", duration)
                return True
            else:
                self.log_result("New Client Login", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("New Client Login", False, f"Exception: {str(e)}")
            return False

    
    def get_available_slot(self):
        """Get an available slot for testing"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/slots?available_only=true",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slots = response.json()
                if slots:
                    self.available_slot_id = slots[0]["id"]
                    self.log_result("Get Available Slots", True, f"Found {len(slots)} available slots, using slot {self.available_slot_id}", duration)
                    return True
                else:
                    self.log_result("Get Available Slots", False, "No available slots found", duration)
                    return False
            else:
                self.log_result("Get Available Slots", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Get Available Slots", False, f"Exception: {str(e)}")
            return False
    
    def create_test_slot(self):
        """Create a test slot for booking"""
        if not self.admin_token:
            self.log_result("Create Test Slot", False, "Missing admin token")
            return False
            
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create slot for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            slot_data = {
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "14:30"  # 2:30 PM
            }
            
            response = requests.post(
                f"{BASE_URL}/slots",
                json=slot_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slot = response.json()
                self.log_result("Create Test Slot", True, f"Test slot created: {slot.get('id', 'N/A')}", duration)
                return True
            else:
                self.log_result("Create Test Slot", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Create Test Slot", False, f"Exception: {str(e)}")
            return False
        """Get an available slot for testing"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/slots?available_only=true",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slots = response.json()
                if slots:
                    self.available_slot_id = slots[0]["id"]
                    self.log_result("Get Available Slots", True, f"Found {len(slots)} available slots, using slot {self.available_slot_id}", duration)
                    return True
                else:
                    self.log_result("Get Available Slots", False, "No available slots found", duration)
                    return False
            else:
                self.log_result("Get Available Slots", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Get Available Slots", False, f"Exception: {str(e)}")
            return False
    
    def create_multiple_test_slots(self, count=5):
        """Create multiple test slots for comprehensive testing"""
        if not self.admin_token:
            self.log_result("Create Multiple Slots", False, "Missing admin token")
            return False
            
        created_count = 0
        for i in range(count):
            try:
                start_time = time.time()
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                # Create slots for different times tomorrow
                tomorrow = datetime.now() + timedelta(days=1)
                times = ["10:00", "11:00", "14:00", "15:00", "16:00"]
                slot_data = {
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "time": times[i % len(times)]
                }
                
                response = requests.post(
                    f"{BASE_URL}/slots",
                    json=slot_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    created_count += 1
                else:
                    # Slot might already exist, continue
                    pass
            except Exception as e:
                pass
        
        if created_count > 0:
            self.log_result("Create Multiple Slots", True, f"Created {created_count} additional slots")
            return True
        else:
            self.log_result("Create Multiple Slots", False, "No additional slots created")
            return False
        """CRITICAL TEST: Test POST /api/appointments with proper Authorization token"""
        if not self.client_token or not self.available_slot_id:
            self.log_result("Appointment Creation (With Token)", False, "Missing client token or available slot")
            return False
            
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Test with "Très simple" service (5€)
            appointment_data = {
                "slot_id": self.available_slot_id,
                "service_name": "Très simple",
                "service_price": 5.0,
                "notes": "Test appointment with proper token"
            }
            
            response = requests.post(
                f"{BASE_URL}/appointments",
                json=appointment_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointment = response.json()
                self.log_result("Appointment Creation (With Token)", True, 
                              f"Appointment created successfully - ID: {appointment.get('id', 'N/A')}, Service: {appointment.get('service_name', 'N/A')}", 
                              duration)
                return True
            elif response.status_code == 422:
                self.log_result("Appointment Creation (With Token)", False, 
                              f"422 ERROR STILL PRESENT: {response.text}", duration)
                return False
            else:
                self.log_result("Appointment Creation (With Token)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Appointment Creation (With Token)", False, f"Exception: {str(e)}")
            return False
    
    def test_appointment_creation_without_token(self):
        """Test POST /api/appointments without Authorization token (should fail with 401)"""
        if not self.available_slot_id:
            self.log_result("Appointment Creation (No Token)", False, "Missing available slot")
            return False
            
        try:
            start_time = time.time()
            
            appointment_data = {
                "slot_id": self.available_slot_id,
                "service_name": "Simple",
                "service_price": 8.0,
                "notes": "Test without token"
            }
            
            response = requests.post(
                f"{BASE_URL}/appointments",
                json=appointment_data,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Appointment Creation (No Token)", True, 
                              "Correctly rejected with 401 Unauthorized", duration)
                return True
            else:
                self.log_result("Appointment Creation (No Token)", False, 
                              f"Expected 401, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Appointment Creation (No Token)", False, f"Exception: {str(e)}")
            return False
    
    def test_client_appointments_with_slot_info(self):
        """IMPORTANT TEST: Verify clients receive slot_info in GET /api/appointments"""
        if not self.client_token:
            self.log_result("Client Appointments (Slot Info)", False, "Missing client token")
            return False
            
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointments = response.json()
                if appointments:
                    # Check if appointments have slot_info
                    has_slot_info = any(apt.get('slot_info') for apt in appointments)
                    if has_slot_info:
                        sample_apt = next((apt for apt in appointments if apt.get('slot_info')), appointments[0])
                        slot_info = sample_apt.get('slot_info', {})
                        self.log_result("Client Appointments (Slot Info)", True, 
                                      f"Found {len(appointments)} appointments with slot_info. Sample slot: date={slot_info.get('date', 'N/A')}, time={slot_info.get('start_time', 'N/A')}", 
                                      duration)
                        return True
                    else:
                        self.log_result("Client Appointments (Slot Info)", False, 
                                      f"Found {len(appointments)} appointments but NO slot_info field", duration)
                        return False
                else:
                    self.log_result("Client Appointments (Slot Info)", True, 
                                  "No appointments found (expected for new client)", duration)
                    return True
            else:
                self.log_result("Client Appointments (Slot Info)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Client Appointments (Slot Info)", False, f"Exception: {str(e)}")
            return False
    
    def test_password_reset_request(self):
        """NEW TEST: Test password reset request endpoint"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/auth/password-reset/request",
                json={"email": "marie.dupont@email.com"},
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Password Reset Request", True, 
                              f"Request successful: {result.get('message', 'N/A')}", duration)
                return True
            else:
                self.log_result("Password Reset Request", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Request", False, f"Exception: {str(e)}")
            return False
    
    def test_password_reset_confirm_invalid(self):
        """NEW TEST: Test password reset confirm with invalid code"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/auth/password-reset/confirm",
                json={
                    "email": "marie.dupont@email.com",
                    "code": "000000",  # Invalid code
                    "new_password": "newpassword123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 400:
                self.log_result("Password Reset Confirm (Invalid)", True, 
                              "Correctly rejected invalid code with 400", duration)
                return True
            else:
                self.log_result("Password Reset Confirm (Invalid)", False, 
                              f"Expected 400, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Confirm (Invalid)", False, f"Exception: {str(e)}")
            return False
    
    def test_appointment_creation_performance(self):
        """PERFORMANCE TEST: Measure POST /api/appointments speed with background tasks"""
        if not self.client_token:
            self.log_result("Appointment Performance", False, "Missing client token")
            return False
        
        # Get a fresh available slot
        if not self.get_available_slot():
            self.log_result("Appointment Performance", False, "No available slot for performance test")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Test with "Chargé" service (12€)
            appointment_data = {
                "slot_id": self.available_slot_id,
                "service_name": "Chargé",
                "service_price": 12.0,
                "notes": "Performance test appointment"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/appointments",
                json=appointment_data,
                headers=headers,
                timeout=15  # Longer timeout for performance test
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                if duration < 2.0:
                    self.log_result("Appointment Performance", True, 
                                  f"EXCELLENT performance - Response in {duration:.3f}s (< 2s target)", duration)
                elif duration < 3.0:
                    self.log_result("Appointment Performance", True, 
                                  f"GOOD performance - Response in {duration:.3f}s (< 3s)", duration)
                elif duration < 5.0:
                    self.log_result("Appointment Performance", True, 
                                  f"ACCEPTABLE performance - Response in {duration:.3f}s (< 5s)", duration)
                else:
                    self.log_result("Appointment Performance", False, 
                                  f"SLOW performance - Response in {duration:.3f}s (> 5s)", duration)
                return True
            else:
                self.log_result("Appointment Performance", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Appointment Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_all_services_booking(self):
        """Test booking with all 4 available services"""
        if not self.client_token:
            self.log_result("All Services Booking", False, "Missing client token")
            return False
        
        services = [
            {"name": "Très simple", "price": 5.0},
            {"name": "Simple", "price": 8.0},
            {"name": "Chargé", "price": 12.0},
            {"name": "Mariée", "price": 20.0}
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        successful_bookings = 0
        
        for service in services:
            # Get fresh slot for each service
            if not self.get_available_slot():
                continue
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.available_slot_id,
                    "service_name": service["name"],
                    "service_price": service["price"],
                    "notes": f"Test booking for {service['name']} service"
                }
                
                response = requests.post(
                    f"{BASE_URL}/appointments",
                    json=appointment_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    successful_bookings += 1
                    self.log_result(f"Service Booking ({service['name']})", True, 
                                  f"Successfully booked {service['name']} for {service['price']}€", duration)
                else:
                    self.log_result(f"Service Booking ({service['name']})", False, 
                                  f"Status {response.status_code}: {response.text}", duration)
            except Exception as e:
                self.log_result(f"Service Booking ({service['name']})", False, f"Exception: {str(e)}")
        
        # Overall result
        if successful_bookings == len(services):
            self.log_result("All Services Booking", True, f"All {successful_bookings}/{len(services)} services work correctly")
            return True
        else:
            self.log_result("All Services Booking", False, f"Only {successful_bookings}/{len(services)} services work")
            return False
    
    def run_tests(self):
        """Run all tests focusing on 422 error fixes"""
        print("🎯 BACKEND TESTING - FOCUS: 422 ERROR FIXES")
        print("=" * 60)
        
        # Authentication setup
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.authenticate_client():
            print("❌ Cannot proceed without client authentication")
            return
        
        # Get available slots or create multiple ones
        if not self.get_available_slot():
            print("⚠️ No available slots found, creating multiple test slots...")
            self.create_multiple_test_slots(5)
            if not self.get_available_slot():
                print("❌ Still no available slots after creation")
                return
        else:
            # Create additional slots for comprehensive testing
            print("✅ Available slots found, creating additional slots for comprehensive testing...")
            self.create_multiple_test_slots(4)
        
        print("\n🔥 CRITICAL TESTS - 422 ERROR FIXES:")
        print("-" * 40)
        
        # CRITICAL: Test the main 422 fix
        self.test_appointment_creation_with_token()
        self.test_appointment_creation_without_token()
        
        print("\n📋 IMPORTANT TESTS - SLOT INFO FIX:")
        print("-" * 40)
        
        # IMPORTANT: Test slot_info in appointments
        self.test_client_appointments_with_slot_info()
        
        print("\n🔐 NEW TESTS - PASSWORD RESET SYSTEM:")
        print("-" * 40)
        
        # NEW: Test password reset system
        self.test_password_reset_request()
        self.test_password_reset_confirm_invalid()
        
        print("\n⚡ PERFORMANCE TESTS - BACKGROUND TASKS:")
        print("-" * 40)
        
        # PERFORMANCE: Test appointment creation speed
        self.test_appointment_creation_performance()
        
        print("\n🎯 SERVICE TESTS - ALL 4 SERVICES:")
        print("-" * 40)
        
        # Test all services
        self.test_all_services_booking()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}/{total} tests")
        print(f"❌ FAILED: {total - passed}/{total} tests")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 FAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        
        # Show critical results
        print("\n🎯 CRITICAL RESULTS (422 Error Fixes):")
        critical_tests = [
            "Appointment Creation (With Token)",
            "Appointment Creation (No Token)",
            "Client Appointments (Slot Info)"
        ]
        
        for test_name in critical_tests:
            result = next((r for r in self.test_results if r['test'] == test_name), None)
            if result:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {test_name}: {result['message']}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_tests()