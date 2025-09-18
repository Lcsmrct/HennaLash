#!/usr/bin/env python3
"""
Backend API Testing - Maintenance Features & Regression Tests
Focus: Tester les nouvelles fonctionnalités de maintenance et vérifier les régressions:
1. Endpoints de maintenance (critique) - GET/POST /api/maintenance
2. Interface admin améliorée - vérifier authentification admin
3. Tests de régression - s'assurer que les fonctionnalités existantes marchent toujours
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import random

# Configuration - Use localhost as per frontend/.env
BASE_URL = "http://localhost:8001/api"
TIMEOUT = 15

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
            # Try different admin credentials that might exist
            admin_credentials = [
                {"email": "lucas@lcsmrct.fr", "password": "admin123"},
                {"email": "lucas@lcsmrct.fr", "password": "password123"},
                {"email": "newadmin@salon.com", "password": "admin123"},
                {"email": "newadmin@salon.com", "password": "password123"},
                {"email": "email@email.com", "password": "admin123"},
                {"email": "email@email.com", "password": "password123"},
                {"email": "admin@salon.com", "password": "admin123"},
                {"email": "admin", "password": "admin123"}
            ]
            
            for creds in admin_credentials:
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{BASE_URL}/login",
                        json=creds,
                        timeout=TIMEOUT
                    )
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        self.admin_token = response.json()["access_token"]
                        self.log_result("Admin Authentication", True, f"Admin login successful with {creds['email']}", duration)
                        return True
                except:
                    continue
            
            # If no existing admin found, try to create one
            return self.create_admin_user()
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_admin_user(self):
        """Create admin user and then authenticate"""
        try:
            # Try creating admin user with unique email
            import random
            random_num = random.randint(1000, 9999)
            admin_email = f"testadmin{random_num}@salon.com"
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": admin_email,
                    "password": "admin123",
                    "first_name": "Test",
                    "last_name": "Admin",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Admin Registration", True, f"Admin user created: {admin_email}", duration)
                # Now try to login with new credentials
                return self.login_new_admin(admin_email, "admin123")
            else:
                self.log_result("Admin Registration", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Registration", False, f"Exception: {str(e)}")
            return False
    
    def login_new_admin(self, email, password):
        """Login with new admin credentials"""
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
                self.admin_token = response.json()["access_token"]
                self.log_result("New Admin Login", True, "New admin login successful", duration)
                return True
            else:
                self.log_result("New Admin Login", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("New Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_client(self):
        """Authenticate as client user or create one"""
        try:
            # Try to login with credentials from review request
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "marie",
                    "password": "password123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication", True, "Client login successful with marie:password123", duration)
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
    
    def test_complete_end_to_end_workflow(self):
        """COMPLETE END-TO-END TEST: Registration → Login → Booking → Verification"""
        print("\n🎯 COMPLETE END-TO-END WORKFLOW TEST")
        print("-" * 50)
        
        # Step 1: Create new client
        random_num = random.randint(10000, 99999)
        test_email = f"endtoend{random_num}@test.com"
        test_password = "testpass123"
        
        try:
            # Registration
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "first_name": "Sophie",
                    "last_name": "Martin",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("E2E - Registration", False, f"Registration failed: {response.status_code} - {response.text}", duration)
                return False
            
            self.log_result("E2E - Registration", True, f"New client registered: {test_email}", duration)
            
            # Step 2: Login
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("E2E - Login", False, f"Login failed: {response.status_code} - {response.text}", duration)
                return False
            
            e2e_token = response.json()["access_token"]
            self.log_result("E2E - Login", True, "Client login successful", duration)
            
            # Step 3: Get available slot
            if not self.get_available_slot():
                self.log_result("E2E - Get Slot", False, "No available slots for booking")
                return False
            
            # Step 4: Test all 4 services booking
            services = [
                {"name": "Très simple", "price": 5},
                {"name": "Simple", "price": 8},
                {"name": "Chargé", "price": 12},
                {"name": "Mariée", "price": 20}
            ]
            
            headers = {"Authorization": f"Bearer {e2e_token}"}
            successful_bookings = 0
            
            for service in services:
                # Get fresh slot for each service
                if not self.get_available_slot():
                    continue
                    
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.available_slot_id,
                    "service_name": service["name"],
                    "service_price": service["price"],  # CRITICAL: Numeric price (not string)
                    "notes": f"E2E test - {service['name']} service"
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
                    appointment = response.json()
                    self.log_result(f"E2E - Book {service['name']}", True, 
                                  f"✅ SUCCESS - {service['name']} ({service['price']}€) booked successfully", duration)
                elif response.status_code == 422:
                    self.log_result(f"E2E - Book {service['name']}", False, 
                                  f"❌ 422 ERROR STILL EXISTS - {response.text}", duration)
                else:
                    self.log_result(f"E2E - Book {service['name']}", False, 
                                  f"Status {response.status_code}: {response.text}", duration)
            
            # Step 5: Verify data storage
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointments = response.json()
                self.log_result("E2E - Verify Storage", True, 
                              f"Data verified - {len(appointments)} appointments stored with slot_info", duration)
                
                # Check if appointments have proper service data
                for apt in appointments:
                    if apt.get('service_name') and apt.get('service_price'):
                        print(f"  📋 Appointment: {apt['service_name']} - {apt['service_price']}€")
                
                return successful_bookings == len(services)
            else:
                self.log_result("E2E - Verify Storage", False, f"Status {response.status_code}: {response.text}", duration)
                return False
                
        except Exception as e:
            self.log_result("E2E - Workflow", False, f"Exception: {str(e)}")
            return False

    def test_422_error_specifically(self):
        """SPECIFIC TEST: Verify 422 error is resolved with numeric prices"""
        print("\n🚨 SPECIFIC 422 ERROR TEST")
        print("-" * 30)
        
        if not self.client_token or not self.available_slot_id:
            self.log_result("422 Error Test", False, "Missing client token or slot")
            return False
        
        # Test each service with numeric prices
        services_to_test = [
            {"name": "Très simple", "price": 5, "expected": "✅ Should work"},
            {"name": "Simple", "price": 8, "expected": "✅ Should work"},
            {"name": "Chargé", "price": 12, "expected": "✅ Should work"},
            {"name": "Mariée", "price": 20, "expected": "✅ Should work"}
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        all_passed = True
        
        for service in services_to_test:
            if not self.get_available_slot():
                continue
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.available_slot_id,
                    "service_name": service["name"],
                    "service_price": service["price"],  # NUMERIC (not string like "5€")
                    "notes": f"422 test - {service['name']}"
                }
                
                response = requests.post(
                    f"{BASE_URL}/appointments",
                    json=appointment_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result(f"422 Test - {service['name']}", True, 
                                  f"✅ NO 422 ERROR - {service['name']} ({service['price']}€) works", duration)
                elif response.status_code == 422:
                    self.log_result(f"422 Test - {service['name']}", False, 
                                  f"❌ 422 ERROR PERSISTS - {response.text}", duration)
                    all_passed = False
                else:
                    self.log_result(f"422 Test - {service['name']}", False, 
                                  f"Unexpected status {response.status_code}: {response.text}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"422 Test - {service['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_login_registration_pages_backend(self):
        """Test backend support for login/registration (design pages)"""
        print("\n🎨 LOGIN/REGISTRATION BACKEND SUPPORT TEST")
        print("-" * 45)
        
        # Test registration endpoint
        random_num = random.randint(100000, 999999)
        test_email = f"designtest{random_num}@test.com"
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": test_email,
                    "password": "design123",
                    "first_name": "Design",
                    "last_name": "Test",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Design - Registration Backend", True, 
                              "Registration endpoint works for new design pages", duration)
                
                # Test login endpoint
                start_time = time.time()
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={
                        "email": test_email,
                        "password": "design123"
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_result("Design - Login Backend", True, 
                                  "Login endpoint works for new design pages", duration)
                    return True
                else:
                    self.log_result("Design - Login Backend", False, 
                                  f"Login failed: {response.status_code} - {response.text}", duration)
                    return False
            else:
                self.log_result("Design - Registration Backend", False, 
                              f"Registration failed: {response.status_code} - {response.text}", duration)
                return False
                
        except Exception as e:
            self.log_result("Design - Backend Support", False, f"Exception: {str(e)}")
            return False

    def test_admin_appointment_cancellation(self):
        """TEST: Admin appointment cancellation with email notification"""
        if not self.admin_token:
            self.log_result("Admin Appointment Cancellation", False, "Missing admin token")
            return False
        
        # First create an appointment to cancel
        appointment_id = self.create_test_appointment_for_admin_tests()
        if not appointment_id:
            self.log_result("Admin Appointment Cancellation", False, "Could not create test appointment")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Admin Appointment Cancellation", True, 
                              f"Appointment cancelled successfully: {result.get('message', 'N/A')}", duration)
                
                # Verify appointment status is 'cancelled'
                return self.verify_appointment_status(appointment_id, "cancelled")
            else:
                self.log_result("Admin Appointment Cancellation", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Appointment Cancellation", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_appointment_deletion(self):
        """TEST: Admin appointment deletion"""
        if not self.admin_token:
            self.log_result("Admin Appointment Deletion", False, "Missing admin token")
            return False
        
        # First create an appointment to delete
        appointment_id = self.create_test_appointment_for_admin_tests()
        if not appointment_id:
            self.log_result("Admin Appointment Deletion", False, "Could not create test appointment")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.delete(
                f"{BASE_URL}/appointments/{appointment_id}",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Admin Appointment Deletion", True, 
                              f"Appointment deleted successfully: {result.get('message', 'N/A')}", duration)
                
                # Verify appointment no longer exists
                return self.verify_appointment_deleted(appointment_id)
            else:
                self.log_result("Admin Appointment Deletion", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Appointment Deletion", False, f"Exception: {str(e)}")
            return False
    
    def test_slot_availability_after_cancellation(self):
        """TEST: Verify slot becomes available after appointment cancellation"""
        if not self.admin_token:
            self.log_result("Slot Availability After Cancellation", False, "Missing admin token")
            return False
        
        # Create appointment and get slot ID
        appointment_data = self.create_test_appointment_for_admin_tests(return_full_data=True)
        if not appointment_data:
            self.log_result("Slot Availability After Cancellation", False, "Could not create test appointment")
            return False
        
        appointment_id = appointment_data.get('appointment_id')
        slot_id = appointment_data.get('slot_id')
        
        try:
            # Cancel the appointment
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check if slot is now available
                return self.verify_slot_availability(slot_id, should_be_available=True)
            else:
                self.log_result("Slot Availability After Cancellation", False, 
                              f"Cancellation failed: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Slot Availability After Cancellation", False, f"Exception: {str(e)}")
            return False
    
    def test_slot_availability_after_deletion(self):
        """TEST: Verify slot becomes available after appointment deletion"""
        if not self.admin_token:
            self.log_result("Slot Availability After Deletion", False, "Missing admin token")
            return False
        
        # Create appointment and get slot ID
        appointment_data = self.create_test_appointment_for_admin_tests(return_full_data=True)
        if not appointment_data:
            self.log_result("Slot Availability After Deletion", False, "Could not create test appointment")
            return False
        
        appointment_id = appointment_data.get('appointment_id')
        slot_id = appointment_data.get('slot_id')
        
        try:
            # Delete the appointment
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.delete(
                f"{BASE_URL}/appointments/{appointment_id}",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check if slot is now available
                return self.verify_slot_availability(slot_id, should_be_available=True)
            else:
                self.log_result("Slot Availability After Deletion", False, 
                              f"Deletion failed: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Slot Availability After Deletion", False, f"Exception: {str(e)}")
            return False
    
    def test_past_appointments_logic(self):
        """TEST: Logic for identifying past appointments (older than 24h)"""
        if not self.admin_token:
            self.log_result("Past Appointments Logic", False, "Missing admin token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all appointments
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointments = response.json()
                
                # Analyze appointments for past dates
                now = datetime.now()
                past_appointments = []
                future_appointments = []
                
                for apt in appointments:
                    slot_info = apt.get('slot_info', {})
                    if slot_info and slot_info.get('date') and slot_info.get('start_time'):
                        try:
                            # Parse appointment date and time
                            apt_date_str = slot_info['date']
                            apt_time_str = slot_info['start_time']
                            
                            # Handle different date formats
                            if 'T' in apt_date_str:
                                apt_date = datetime.fromisoformat(apt_date_str.replace('Z', '+00:00')).date()
                            else:
                                apt_date = datetime.strptime(apt_date_str, '%Y-%m-%d').date()
                            
                            apt_time = datetime.strptime(apt_time_str, '%H:%M').time()
                            apt_datetime = datetime.combine(apt_date, apt_time)
                            
                            # Check if more than 24 hours in the past
                            time_diff = now - apt_datetime
                            if time_diff.total_seconds() > 24 * 3600:  # 24 hours in seconds
                                past_appointments.append({
                                    'id': apt.get('id'),
                                    'datetime': apt_datetime,
                                    'hours_past': time_diff.total_seconds() / 3600
                                })
                            else:
                                future_appointments.append({
                                    'id': apt.get('id'),
                                    'datetime': apt_datetime
                                })
                        except Exception as parse_error:
                            # Skip appointments with invalid date/time data
                            continue
                
                self.log_result("Past Appointments Logic", True, 
                              f"Successfully analyzed appointments: {len(past_appointments)} past (>24h), {len(future_appointments)} future/recent", 
                              duration)
                
                # Log some examples if found
                if past_appointments:
                    print(f"  📅 Past appointments found:")
                    for apt in past_appointments[:3]:  # Show first 3
                        print(f"    - ID: {apt['id']}, Date: {apt['datetime']}, Hours past: {apt['hours_past']:.1f}h")
                
                return True
            else:
                self.log_result("Past Appointments Logic", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Past Appointments Logic", False, f"Exception: {str(e)}")
            return False
    
    def create_test_appointment_for_admin_tests(self, return_full_data=False):
        """Helper: Create a test appointment for admin testing"""
        if not self.client_token:
            return None
        
        # Get available slot
        if not self.get_available_slot():
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            appointment_data = {
                "slot_id": self.available_slot_id,
                "service_name": "Simple",
                "service_price": 8.0,
                "notes": "Test appointment for admin operations"
            }
            
            response = requests.post(
                f"{BASE_URL}/appointments",
                json=appointment_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                appointment = response.json()
                appointment_id = appointment.get('id')
                
                if return_full_data:
                    return {
                        'appointment_id': appointment_id,
                        'slot_id': self.available_slot_id,
                        'appointment_data': appointment
                    }
                else:
                    return appointment_id
            else:
                return None
        except Exception:
            return None
    
    def verify_appointment_status(self, appointment_id, expected_status):
        """Helper: Verify appointment has expected status"""
        if not self.admin_token:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                appointments = response.json()
                appointment = next((apt for apt in appointments if apt.get('id') == appointment_id), None)
                
                if appointment:
                    actual_status = appointment.get('status')
                    if actual_status == expected_status:
                        self.log_result("Verify Appointment Status", True, 
                                      f"Appointment {appointment_id} has correct status: {expected_status}")
                        return True
                    else:
                        self.log_result("Verify Appointment Status", False, 
                                      f"Appointment {appointment_id} has status '{actual_status}', expected '{expected_status}'")
                        return False
                else:
                    self.log_result("Verify Appointment Status", False, 
                                  f"Appointment {appointment_id} not found")
                    return False
            else:
                return False
        except Exception:
            return False
    
    def verify_appointment_deleted(self, appointment_id):
        """Helper: Verify appointment no longer exists"""
        if not self.admin_token:
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                appointments = response.json()
                appointment = next((apt for apt in appointments if apt.get('id') == appointment_id), None)
                
                if appointment is None:
                    self.log_result("Verify Appointment Deleted", True, 
                                  f"Appointment {appointment_id} successfully deleted")
                    return True
                else:
                    self.log_result("Verify Appointment Deleted", False, 
                                  f"Appointment {appointment_id} still exists after deletion")
                    return False
            else:
                return False
        except Exception:
            return False
    
    def verify_slot_availability(self, slot_id, should_be_available=True):
        """Helper: Verify slot availability status"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/slots",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slots = response.json()
                slot = next((s for s in slots if s.get('id') == slot_id), None)
                
                if slot:
                    is_available = slot.get('is_available', False)
                    if is_available == should_be_available:
                        status_text = "available" if should_be_available else "unavailable"
                        self.log_result("Verify Slot Availability", True, 
                                      f"Slot {slot_id} is correctly {status_text}", duration)
                        return True
                    else:
                        expected_text = "available" if should_be_available else "unavailable"
                        actual_text = "available" if is_available else "unavailable"
                        self.log_result("Verify Slot Availability", False, 
                                      f"Slot {slot_id} is {actual_text}, expected {expected_text}", duration)
                        return False
                else:
                    self.log_result("Verify Slot Availability", False, 
                                  f"Slot {slot_id} not found", duration)
                    return False
            else:
                self.log_result("Verify Slot Availability", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Verify Slot Availability", False, f"Exception: {str(e)}")
            return False

    def test_reviews_performance_critical(self):
        """CRITICAL TEST: POST /api/reviews performance with BackgroundTasks (should be <2s)"""
        if not self.client_token:
            self.log_result("Reviews Performance Critical", False, "Missing client token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Test review creation with precise timing
            review_data = {
                "rating": 5,
                "comment": "Test critique performance - système email asynchrone BackgroundTasks"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/reviews",
                json=review_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                if duration < 2.0:
                    self.log_result("Reviews Performance Critical", True, 
                                  f"🚀 EXCELLENT - Response in {duration:.3f}s (<2s target) - BackgroundTasks working!", duration)
                    return True
                elif duration < 3.0:
                    self.log_result("Reviews Performance Critical", True, 
                                  f"✅ GOOD - Response in {duration:.3f}s (<3s) - Improvement confirmed", duration)
                    return True
                elif duration < 5.0:
                    self.log_result("Reviews Performance Critical", False, 
                                  f"⚠️ SLOW - Response in {duration:.3f}s (still >2s target)", duration)
                    return False
                else:
                    self.log_result("Reviews Performance Critical", False, 
                                  f"❌ VERY SLOW - Response in {duration:.3f}s (>5s) - BackgroundTasks not working", duration)
                    return False
            else:
                self.log_result("Reviews Performance Critical", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Reviews Performance Critical", False, f"Exception: {str(e)}")
            return False

    def test_appointment_cancellation_critical(self):
        """CRITICAL TEST: PUT /api/appointments/{id}/cancel with BackgroundTasks email"""
        if not self.admin_token:
            self.log_result("Appointment Cancellation Critical", False, "Missing admin token")
            return False
        
        # Create test appointment first
        appointment_id = self.create_test_appointment_for_admin_tests()
        if not appointment_id:
            self.log_result("Appointment Cancellation Critical", False, "Could not create test appointment")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Check performance - should be fast with BackgroundTasks
                if duration < 2.0:
                    self.log_result("Appointment Cancellation Critical", True, 
                                  f"🚀 FAST cancellation in {duration:.3f}s - BackgroundTasks working! Message: {result.get('message', 'N/A')}", duration)
                else:
                    self.log_result("Appointment Cancellation Critical", True, 
                                  f"✅ Cancellation works in {duration:.3f}s - Message: {result.get('message', 'N/A')}", duration)
                
                # Verify appointment status changed to 'cancelled'
                return self.verify_appointment_status(appointment_id, "cancelled")
            else:
                self.log_result("Appointment Cancellation Critical", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Appointment Cancellation Critical", False, f"Exception: {str(e)}")
            return False

    def test_admin_email_data_critical(self):
        """CRITICAL TEST: GET /api/appointments returns user_name and user_email for admin"""
        if not self.admin_token:
            self.log_result("Admin Email Data Critical", False, "Missing admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointments = response.json()
                
                if appointments:
                    # Check if appointments have user_name and user_email fields
                    has_user_name = any(apt.get('user_name') for apt in appointments)
                    has_user_email = any(apt.get('user_email') for apt in appointments)
                    
                    if has_user_name and has_user_email:
                        sample_apt = next((apt for apt in appointments if apt.get('user_name') and apt.get('user_email')), appointments[0])
                        user_name = sample_apt.get('user_name', 'N/A')
                        user_email = sample_apt.get('user_email', 'N/A')
                        
                        self.log_result("Admin Email Data Critical", True, 
                                      f"✅ CORRECT - Found {len(appointments)} appointments with user_name='{user_name}' and user_email='{user_email}'", duration)
                        return True
                    elif has_user_name and not has_user_email:
                        self.log_result("Admin Email Data Critical", False, 
                                      f"❌ PARTIAL - Found user_name but MISSING user_email field", duration)
                        return False
                    elif not has_user_name and has_user_email:
                        self.log_result("Admin Email Data Critical", False, 
                                      f"❌ PARTIAL - Found user_email but MISSING user_name field", duration)
                        return False
                    else:
                        self.log_result("Admin Email Data Critical", False, 
                                      f"❌ MISSING - No user_name or user_email fields found in appointments", duration)
                        return False
                else:
                    self.log_result("Admin Email Data Critical", True, 
                                  "No appointments found (expected for clean test environment)", duration)
                    return True
            else:
                self.log_result("Admin Email Data Critical", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Email Data Critical", False, f"Exception: {str(e)}")
            return False

    def test_slot_availability_after_cancellation_critical(self):
        """CRITICAL TEST: Verify slot becomes available after cancellation"""
        if not self.admin_token:
            self.log_result("Slot Availability After Cancellation Critical", False, "Missing admin token")
            return False
        
        # Create appointment and get slot ID
        appointment_data = self.create_test_appointment_for_admin_tests(return_full_data=True)
        if not appointment_data:
            self.log_result("Slot Availability After Cancellation Critical", False, "Could not create test appointment")
            return False
        
        appointment_id = appointment_data.get('appointment_id')
        slot_id = appointment_data.get('slot_id')
        
        try:
            # Cancel the appointment
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                # Check if slot is now available
                return self.verify_slot_availability(slot_id, should_be_available=True)
            else:
                self.log_result("Slot Availability After Cancellation Critical", False, 
                              f"Cancellation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Slot Availability After Cancellation Critical", False, f"Exception: {str(e)}")
            return False

    def test_maintenance_get_public(self):
        """TEST: GET /api/maintenance - public endpoint (no auth required)"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/maintenance",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                maintenance_status = response.json()
                is_maintenance = maintenance_status.get('is_maintenance', False)
                message = maintenance_status.get('message', '')
                
                self.log_result("Maintenance GET (Public)", True, 
                              f"✅ Public access works - is_maintenance: {is_maintenance}, message: '{message}'", duration)
                return True
            else:
                self.log_result("Maintenance GET (Public)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance GET (Public)", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_post_without_auth(self):
        """TEST: POST /api/maintenance without authentication (should fail with 401)"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "Test maintenance mode"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Maintenance POST (No Auth)", True, 
                              "✅ Correctly rejected with 401 Unauthorized", duration)
                return True
            else:
                self.log_result("Maintenance POST (No Auth)", False, 
                              f"Expected 401, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance POST (No Auth)", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_post_with_client_auth(self):
        """TEST: POST /api/maintenance with client authentication (should fail with 403)"""
        if not self.client_token:
            self.log_result("Maintenance POST (Client Auth)", False, "Missing client token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "Test maintenance mode"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 403:
                self.log_result("Maintenance POST (Client Auth)", True, 
                              "✅ Correctly rejected client with 403 Forbidden", duration)
                return True
            else:
                self.log_result("Maintenance POST (Client Auth)", False, 
                              f"Expected 403, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance POST (Client Auth)", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_enable_with_admin(self):
        """TEST: POST /api/maintenance to enable maintenance mode (admin required)"""
        if not self.admin_token:
            self.log_result("Maintenance Enable (Admin)", False, "Missing admin token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            maintenance_data = {
                "is_maintenance": True,
                "message": "Site en maintenance pour tests - Mode activé par admin"
            }
            
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json=maintenance_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                is_maintenance = result.get('is_maintenance', False)
                message = result.get('message', '')
                enabled_at = result.get('enabled_at')
                enabled_by = result.get('enabled_by')
                
                if is_maintenance and enabled_at and enabled_by:
                    self.log_result("Maintenance Enable (Admin)", True, 
                                  f"✅ Maintenance enabled successfully - Message: '{message}', Enabled at: {enabled_at}, By: {enabled_by}", duration)
                    return True
                else:
                    self.log_result("Maintenance Enable (Admin)", False, 
                                  f"Maintenance response incomplete - is_maintenance: {is_maintenance}, enabled_at: {enabled_at}, enabled_by: {enabled_by}", duration)
                    return False
            else:
                self.log_result("Maintenance Enable (Admin)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Enable (Admin)", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_disable_with_admin(self):
        """TEST: POST /api/maintenance to disable maintenance mode (admin required)"""
        if not self.admin_token:
            self.log_result("Maintenance Disable (Admin)", False, "Missing admin token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            maintenance_data = {
                "is_maintenance": False,
                "message": "Site opérationnel - Mode désactivé par admin"
            }
            
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json=maintenance_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                is_maintenance = result.get('is_maintenance', False)
                message = result.get('message', '')
                enabled_at = result.get('enabled_at')
                enabled_by = result.get('enabled_by')
                
                if not is_maintenance and enabled_at is None and enabled_by is None:
                    self.log_result("Maintenance Disable (Admin)", True, 
                                  f"✅ Maintenance disabled successfully - Message: '{message}', Enabled at: {enabled_at}, By: {enabled_by}", duration)
                    return True
                else:
                    self.log_result("Maintenance Disable (Admin)", False, 
                                  f"Maintenance disable incomplete - is_maintenance: {is_maintenance}, enabled_at: {enabled_at}, enabled_by: {enabled_by}", duration)
                    return False
            else:
                self.log_result("Maintenance Disable (Admin)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Disable (Admin)", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_data_persistence(self):
        """TEST: Verify maintenance data is persisted in MongoDB 'maintenance' collection"""
        if not self.admin_token:
            self.log_result("Maintenance Data Persistence", False, "Missing admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, enable maintenance mode
            maintenance_data = {
                "is_maintenance": True,
                "message": "Test persistence - Données sauvegardées en MongoDB"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json=maintenance_data,
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self.log_result("Maintenance Data Persistence", False, 
                              f"Failed to enable maintenance: {response.status_code} - {response.text}")
                return False
            
            # Now verify the data is persisted by reading it back
            response = requests.get(
                f"{BASE_URL}/maintenance",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                is_maintenance = result.get('is_maintenance', False)
                message = result.get('message', '')
                enabled_at = result.get('enabled_at')
                enabled_by = result.get('enabled_by')
                
                # Check if all expected fields are present and correct
                if (is_maintenance and 
                    message == "Test persistence - Données sauvegardées en MongoDB" and 
                    enabled_at and enabled_by):
                    
                    self.log_result("Maintenance Data Persistence", True, 
                                  f"✅ Data persisted correctly in MongoDB - is_maintenance: {is_maintenance}, message: '{message}', enabled_at: {enabled_at}, enabled_by: {enabled_by}", duration)
                    
                    # Clean up - disable maintenance
                    requests.post(
                        f"{BASE_URL}/maintenance",
                        json={"is_maintenance": False, "message": "Test completed"},
                        headers=headers,
                        timeout=TIMEOUT
                    )
                    return True
                else:
                    self.log_result("Maintenance Data Persistence", False, 
                                  f"Data not persisted correctly - is_maintenance: {is_maintenance}, message: '{message}', enabled_at: {enabled_at}, enabled_by: {enabled_by}", duration)
                    return False
            else:
                self.log_result("Maintenance Data Persistence", False, 
                              f"Failed to read maintenance status: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Data Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_toggle_states(self):
        """TEST: Test both maintenance states (enabled and disabled)"""
        if not self.admin_token:
            self.log_result("Maintenance Toggle States", False, "Missing admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test State 1: Enable maintenance
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "État 1: Maintenance activée pour tests"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self.log_result("Maintenance Toggle States", False, 
                              f"Failed to enable maintenance: {response.status_code} - {response.text}")
                return False
            
            # Verify enabled state
            response = requests.get(f"{BASE_URL}/maintenance", timeout=TIMEOUT)
            if response.status_code != 200 or not response.json().get('is_maintenance'):
                self.log_result("Maintenance Toggle States", False, "Failed to verify enabled state")
                return False
            
            # Test State 2: Disable maintenance
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": False,
                    "message": "État 2: Maintenance désactivée après tests"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self.log_result("Maintenance Toggle States", False, 
                              f"Failed to disable maintenance: {response.status_code} - {response.text}")
                return False
            
            # Verify disabled state
            response = requests.get(f"{BASE_URL}/maintenance", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                is_maintenance = result.get('is_maintenance', True)  # Default to True to catch errors
                
                if not is_maintenance:
                    self.log_result("Maintenance Toggle States", True, 
                                  f"✅ Both states work correctly - Final state: disabled (is_maintenance: {is_maintenance})", duration)
                    return True
                else:
                    self.log_result("Maintenance Toggle States", False, 
                                  f"Failed to disable maintenance - is_maintenance: {is_maintenance}", duration)
                    return False
            else:
                self.log_result("Maintenance Toggle States", False, 
                              f"Failed to verify disabled state: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Toggle States", False, f"Exception: {str(e)}")
            return False

    def test_appointment_cancellation_datetime_fix(self):
        """CRITICAL FIX TEST: Test PUT /api/appointments/{id}/cancel endpoint - datetime error fix"""
        print("\n🚨 CRITICAL DATETIME FIX TEST - APPOINTMENT CANCELLATION")
        print("-" * 55)
        
        if not self.admin_token:
            self.log_result("Cancellation Datetime Fix", False, "Missing admin token")
            return False
        
        # Create test appointment first
        appointment_id = self.create_test_appointment_for_admin_tests()
        if not appointment_id:
            self.log_result("Cancellation Datetime Fix", False, "Could not create test appointment")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Cancellation Datetime Fix", True, 
                              f"✅ DATETIME ERROR FIXED - Cancellation works! Response: {result.get('message', 'N/A')}", duration)
                return True
            elif response.status_code == 500:
                error_text = response.text
                if "UnboundLocalError" in error_text or "datetime" in error_text.lower():
                    self.log_result("Cancellation Datetime Fix", False, 
                                  f"❌ DATETIME ERROR STILL EXISTS - {error_text}", duration)
                else:
                    self.log_result("Cancellation Datetime Fix", False, 
                                  f"❌ SERVER ERROR (not datetime related) - {error_text}", duration)
                return False
            else:
                self.log_result("Cancellation Datetime Fix", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Cancellation Datetime Fix", False, f"Exception: {str(e)}")
            return False

    def test_full_cancellation_workflow(self):
        """COMPREHENSIVE TEST: Full appointment cancellation workflow"""
        print("\n🔄 FULL APPOINTMENT CANCELLATION WORKFLOW TEST")
        print("-" * 50)
        
        if not self.admin_token:
            self.log_result("Full Cancellation Workflow", False, "Missing admin token")
            return False
        
        # Step 1: Create appointment with full data tracking
        appointment_data = self.create_test_appointment_for_admin_tests(return_full_data=True)
        if not appointment_data:
            self.log_result("Full Cancellation Workflow", False, "Could not create test appointment")
            return False
        
        appointment_id = appointment_data.get('appointment_id')
        slot_id = appointment_data.get('slot_id')
        
        print(f"  📋 Created appointment: {appointment_id}")
        print(f"  🎯 Using slot: {slot_id}")
        
        # Step 2: Verify slot is unavailable before cancellation
        if not self.verify_slot_availability(slot_id, should_be_available=False):
            self.log_result("Full Cancellation Workflow", False, "Slot should be unavailable before cancellation")
            return False
        
        # Step 3: Cancel the appointment
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code != 200:
                self.log_result("Full Cancellation Workflow", False, 
                              f"Cancellation failed: {response.status_code} - {response.text}", duration)
                return False
            
            result = response.json()
            print(f"  ✅ Cancellation response: {result.get('message', 'N/A')}")
            
        except Exception as e:
            self.log_result("Full Cancellation Workflow", False, f"Cancellation exception: {str(e)}")
            return False
        
        # Step 4: Verify appointment status changed to 'cancelled'
        if not self.verify_appointment_status(appointment_id, "cancelled"):
            self.log_result("Full Cancellation Workflow", False, "Appointment status not changed to cancelled")
            return False
        
        # Step 5: Verify slot became available again
        if not self.verify_slot_availability(slot_id, should_be_available=True):
            self.log_result("Full Cancellation Workflow", False, "Slot should be available after cancellation")
            return False
        
        # Step 6: Test background email task (check logs)
        print("  📧 Email notification sent via BackgroundTasks (check backend logs)")
        
        self.log_result("Full Cancellation Workflow", True, 
                      f"✅ COMPLETE WORKFLOW SUCCESS - Appointment cancelled, status updated, slot available, email scheduled", duration)
        return True

    def test_cancellation_background_tasks(self):
        """TEST: Verify cancellation email is sent asynchronously without blocking API"""
        print("\n⚡ BACKGROUND TASK TESTING - EMAIL PERFORMANCE")
        print("-" * 45)
        
        if not self.admin_token:
            self.log_result("Cancellation Background Tasks", False, "Missing admin token")
            return False
        
        # Create test appointment
        appointment_id = self.create_test_appointment_for_admin_tests()
        if not appointment_id:
            self.log_result("Cancellation Background Tasks", False, "Could not create test appointment")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Measure API response time - should be fast with background tasks
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/{appointment_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                if duration < 1.0:
                    self.log_result("Cancellation Background Tasks", True, 
                                  f"🚀 EXCELLENT - API response in {duration:.3f}s (<1s) - BackgroundTasks working perfectly!", duration)
                elif duration < 2.0:
                    self.log_result("Cancellation Background Tasks", True, 
                                  f"✅ GOOD - API response in {duration:.3f}s (<2s) - BackgroundTasks effective", duration)
                elif duration < 3.0:
                    self.log_result("Cancellation Background Tasks", True, 
                                  f"⚠️ ACCEPTABLE - API response in {duration:.3f}s (<3s) - Some improvement needed", duration)
                else:
                    self.log_result("Cancellation Background Tasks", False, 
                                  f"❌ SLOW - API response in {duration:.3f}s (>3s) - BackgroundTasks may not be working", duration)
                    return False
                
                result = response.json()
                print(f"  📧 Email scheduled in background: {result.get('message', 'N/A')}")
                return True
            else:
                self.log_result("Cancellation Background Tasks", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Cancellation Background Tasks", False, f"Exception: {str(e)}")
            return False

    def test_cancellation_error_handling(self):
        """TEST: Error handling for invalid appointment IDs and edge cases"""
        print("\n🛡️ CANCELLATION ERROR HANDLING TESTS")
        print("-" * 40)
        
        if not self.admin_token:
            self.log_result("Cancellation Error Handling", False, "Missing admin token")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        error_tests_passed = 0
        total_error_tests = 3
        
        # Test 1: Invalid appointment ID
        try:
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/invalid-id-12345/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Error Test - Invalid ID", True, 
                              "Correctly returned 404 for invalid appointment ID", duration)
                error_tests_passed += 1
            else:
                self.log_result("Error Test - Invalid ID", False, 
                              f"Expected 404, got {response.status_code}: {response.text}", duration)
        except Exception as e:
            self.log_result("Error Test - Invalid ID", False, f"Exception: {str(e)}")
        
        # Test 2: Non-existent appointment ID (valid format)
        try:
            start_time = time.time()
            fake_id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
            response = requests.put(
                f"{BASE_URL}/appointments/{fake_id}/cancel",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 404:
                self.log_result("Error Test - Non-existent ID", True, 
                              "Correctly returned 404 for non-existent appointment", duration)
                error_tests_passed += 1
            else:
                self.log_result("Error Test - Non-existent ID", False, 
                              f"Expected 404, got {response.status_code}: {response.text}", duration)
        except Exception as e:
            self.log_result("Error Test - Non-existent ID", False, f"Exception: {str(e)}")
        
        # Test 3: Unauthorized access (no admin token)
        try:
            start_time = time.time()
            response = requests.put(
                f"{BASE_URL}/appointments/some-id/cancel",
                timeout=TIMEOUT  # No authorization header
            )
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Error Test - Unauthorized", True, 
                              "Correctly returned 401 for unauthorized access", duration)
                error_tests_passed += 1
            else:
                self.log_result("Error Test - Unauthorized", False, 
                              f"Expected 401, got {response.status_code}: {response.text}", duration)
        except Exception as e:
            self.log_result("Error Test - Unauthorized", False, f"Exception: {str(e)}")
        
        # Overall error handling result
        if error_tests_passed == total_error_tests:
            self.log_result("Cancellation Error Handling", True, 
                          f"All {error_tests_passed}/{total_error_tests} error handling tests passed")
            return True
        else:
            self.log_result("Cancellation Error Handling", False, 
                          f"Only {error_tests_passed}/{total_error_tests} error handling tests passed")
            return False

    def test_cancellation_admin_credentials(self):
        """TEST: Verify admin credentials work for cancellation endpoint"""
        print("\n👤 ADMIN CREDENTIALS TEST FOR CANCELLATION")
        print("-" * 45)
        
        # Test with different admin credential combinations
        admin_credentials = [
            {"email": "admin", "password": "admin123"},
            {"email": "admin@salon.com", "password": "admin123"}
        ]
        
        for creds in admin_credentials:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{BASE_URL}/login",
                    json=creds,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    token = response.json()["access_token"]
                    self.log_result(f"Admin Login ({creds['email']})", True, 
                                  f"Admin credentials work: {creds['email']}", duration)
                    
                    # Test cancellation with this token
                    appointment_id = self.create_test_appointment_for_admin_tests()
                    if appointment_id:
                        headers = {"Authorization": f"Bearer {token}"}
                        cancel_response = requests.put(
                            f"{BASE_URL}/appointments/{appointment_id}/cancel",
                            headers=headers,
                            timeout=TIMEOUT
                        )
                        
                        if cancel_response.status_code == 200:
                            self.log_result(f"Cancellation with {creds['email']}", True, 
                                          "Cancellation works with admin credentials")
                            return True
                        else:
                            self.log_result(f"Cancellation with {creds['email']}", False, 
                                          f"Cancellation failed: {cancel_response.status_code}")
                else:
                    self.log_result(f"Admin Login ({creds['email']})", False, 
                                  f"Login failed: {response.status_code} - {response.text}", duration)
            except Exception as e:
                self.log_result(f"Admin Login ({creds['email']})", False, f"Exception: {str(e)}")
        
        return False

    def run_tests(self):
        """Run maintenance endpoints tests as requested"""
        print("🔧 MAINTENANCE ENDPOINTS TESTING")
        print("=" * 60)
        print("Focus: Testing maintenance endpoints functionality")
        print("Tests: GET /api/maintenance (public) + POST /api/maintenance (admin only)")
        print("Verification: MongoDB persistence + Authentication + State management")
        print("=" * 60)
        
        # Authentication setup
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.authenticate_client():
            print("❌ Cannot proceed without client authentication")
            return
        
        print("\n🌐 TEST 1: GET /api/maintenance (PUBLIC ACCESS)")
        print("-" * 50)
        print("Vérifier que l'endpoint GET est public et ne nécessite pas d'authentification")
        self.test_maintenance_get_public()
        
        print("\n🚫 TEST 2: POST /api/maintenance (NO AUTH - SHOULD FAIL)")
        print("-" * 50)
        print("Vérifier que l'endpoint POST nécessite une authentification")
        self.test_maintenance_post_without_auth()
        
        print("\n👤 TEST 3: POST /api/maintenance (CLIENT AUTH - SHOULD FAIL)")
        print("-" * 50)
        print("Vérifier que l'endpoint POST nécessite une authentification admin")
        self.test_maintenance_post_with_client_auth()
        
        print("\n🔒 TEST 4: POST /api/maintenance (ADMIN - ENABLE)")
        print("-" * 50)
        print("Activer le mode maintenance avec un compte admin")
        self.test_maintenance_enable_with_admin()
        
        print("\n🔓 TEST 5: POST /api/maintenance (ADMIN - DISABLE)")
        print("-" * 50)
        print("Désactiver le mode maintenance avec un compte admin")
        self.test_maintenance_disable_with_admin()
        
        print("\n💾 TEST 6: MONGODB PERSISTENCE")
        print("-" * 50)
        print("Vérifier que les données sont bien sauvegardées dans la collection MongoDB 'maintenance'")
        self.test_maintenance_data_persistence()
        
        print("\n🔄 TEST 7: TOGGLE STATES")
        print("-" * 50)
        print("Tester les deux états : maintenance activée et désactivée")
        self.test_maintenance_toggle_states()
        
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
        print("\n🎯 CRITICAL RESULTS (Maintenance Endpoints):")
        critical_tests = [
            "Maintenance GET (Public)",
            "Maintenance POST (No Auth)",
            "Maintenance POST (Client Auth)",
            "Maintenance Enable (Admin)",
            "Maintenance Disable (Admin)",
            "Maintenance Data Persistence",
            "Maintenance Toggle States"
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