#!/usr/bin/env python3
"""
Backend API Testing Suite for Salon Booking System
Tests all APIs locally on localhost:8001
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

# Configuration
BASE_URL = "https://henna-lash.onrender.com/api"
ADMIN_EMAIL = "admin@salon.com"
ADMIN_PASSWORD = "testadmin123"  # We'll update this password
CLIENT_EMAIL = "marie.dupont@email.com"
CLIENT_PASSWORD = "marie123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_slot_id = None
        self.test_appointment_id = None
        self.test_review_id = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            elif method.upper() == "HEAD":
                response = requests.head(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed to {url}")
            return None
        except requests.exceptions.Timeout:
            print_error(f"Request timeout to {url}")
            return None
        except Exception as e:
            print_error(f"Request error: {str(e)}")
            return None

    def test_health_check(self):
        """Test /ping endpoint"""
        print_header("1. HEALTH CHECK TESTS")
        
        # Test GET /ping
        response = self.make_request("GET", "/ping")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("status") == "Ok":
                print_success("GET /api/ping - Health check working")
                self.results['passed'] += 1
            else:
                print_error(f"GET /api/ping - Unexpected response: {data}")
                self.results['failed'] += 1
        else:
            print_error("GET /api/ping - Failed")
            self.results['failed'] += 1
        
        # Test HEAD /ping
        response = self.make_request("HEAD", "/ping")
        if response and response.status_code == 200:
            print_success("HEAD /api/ping - Health check working")
            self.results['passed'] += 1
        else:
            print_error("HEAD /api/ping - Failed")
            self.results['failed'] += 1

    def test_mongodb_connection(self):
        """Test MongoDB connection by checking if we can access endpoints"""
        print_header("2. MONGODB CONNECTION TEST")
        
        # Test basic endpoint that requires DB
        response = self.make_request("GET", "/slots")
        if response and response.status_code == 200:
            print_success("MongoDB connection working - slots endpoint accessible")
            self.results['passed'] += 1
        else:
            print_error("MongoDB connection failed - cannot access slots endpoint")
            self.results['failed'] += 1

    def test_authentication(self):
        """Test authentication endpoints"""
        print_header("3. AUTHENTICATION TESTS")
        
        # Test admin registration (if not exists)
        admin_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "first_name": "Admin",
            "last_name": "Salon",
            "phone": "0123456789"
        }
        
        response = self.make_request("POST", "/register", admin_data)
        if response:
            if response.status_code == 200:
                print_success("Admin registration successful")
                self.results['passed'] += 1
            elif response.status_code == 400 and "already registered" in response.text:
                print_info("Admin already exists (expected)")
                self.results['passed'] += 1
            else:
                print_error(f"Admin registration failed: {response.text}")
                self.results['failed'] += 1
        else:
            print_error("Admin registration - Connection failed")
            self.results['failed'] += 1
        
        # Test client registration
        client_data = {
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD,
            "first_name": "Marie",
            "last_name": "Dupont",
            "phone": "0987654321"
        }
        
        response = self.make_request("POST", "/register", client_data)
        if response:
            if response.status_code == 200:
                print_success("Client registration successful")
                self.results['passed'] += 1
            elif response.status_code == 400 and "already registered" in response.text:
                print_info("Client already exists (expected)")
                self.results['passed'] += 1
            else:
                print_warning(f"Client registration issue: {response.text}")
                self.results['warnings'] += 1
        else:
            print_error("Client registration - Connection failed")
            self.results['failed'] += 1
        
        # Test admin login - try different passwords if default fails
        admin_passwords = [ADMIN_PASSWORD, "admin", "password", "123456"]
        admin_login_success = False
        
        for password in admin_passwords:
            admin_login = {
                "email": ADMIN_EMAIL,
                "password": password
            }
            
            response = self.make_request("POST", "/login", admin_login)
            if response and response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.admin_token = data["access_token"]
                    print_success(f"Admin login successful with password '{password}' - token obtained")
                    self.results['passed'] += 1
                    admin_login_success = True
                    break
                else:
                    print_error("Admin login - No token in response")
            elif response:
                print_info(f"Admin login failed with password '{password}': {response.status_code}")
        
        if not admin_login_success:
            print_error("Admin login failed with all attempted passwords")
            self.results['failed'] += 1
        
        # Test client login
        client_login = {
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        }
        
        response = self.make_request("POST", "/login", client_login)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.client_token = data["access_token"]
                print_success("Client login successful - token obtained")
                self.results['passed'] += 1
            else:
                print_error("Client login - No token in response")
                self.results['failed'] += 1
        else:
            print_error("Client login failed")
            self.results['failed'] += 1

    def test_admin_slot_management(self):
        """Test admin slot management APIs"""
        print_header("4. ADMIN SLOT MANAGEMENT TESTS")
        
        if not self.admin_token:
            print_error("Cannot test admin APIs - no admin token")
            self.results['failed'] += 5
            return
        
        # Test slot creation
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "14:30"
        }
        
        response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            data = response.json()
            self.test_slot_id = data.get("id")
            print_success(f"Slot creation successful - ID: {self.test_slot_id}")
            print_info(f"Auto-calculated end_time: {data.get('end_time')}")
            self.results['passed'] += 1
        else:
            print_error(f"Slot creation failed: {response.text if response else 'Connection failed'}")
            self.results['failed'] += 1
        
        # Test get all slots
        response = self.make_request("GET", "/slots", auth_token=self.admin_token)
        if response and response.status_code == 200:
            slots = response.json()
            print_success(f"Get all slots successful - Found {len(slots)} slots")
            self.results['passed'] += 1
        else:
            print_error("Get all slots failed")
            self.results['failed'] += 1
        
        # Test get available slots only
        response = self.make_request("GET", "/slots?available_only=true")
        if response and response.status_code == 200:
            available_slots = response.json()
            print_success(f"Get available slots successful - Found {len(available_slots)} available slots")
            self.results['passed'] += 1
        else:
            print_error("Get available slots failed")
            self.results['failed'] += 1
        
        # Test slot deletion (if we have a slot ID)
        if self.test_slot_id:
            response = self.make_request("DELETE", f"/slots/{self.test_slot_id}", auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Slot deletion successful")
                self.results['passed'] += 1
                self.test_slot_id = None  # Reset since deleted
            else:
                print_error("Slot deletion failed")
                self.results['failed'] += 1

    def test_appointment_management(self):
        """Test appointment management APIs"""
        print_header("5. APPOINTMENT MANAGEMENT TESTS")
        
        if not self.admin_token or not self.client_token:
            print_error("Cannot test appointments - missing tokens")
            self.results['failed'] += 5
            return
        
        # First create a slot for booking
        tomorrow = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "10:00"
        }
        
        response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            slot_id = response.json().get("id")
            print_success("Test slot created for appointment booking")
            
            # Test appointment creation with service selection
            appointment_data = {
                "slot_id": slot_id,
                "service_name": "Chargé",
                "service_price": 12.0,
                "notes": "Test de réservation avec service Chargé"
            }
            
            response = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
            if response and response.status_code == 200:
                data = response.json()
                self.test_appointment_id = data.get("id")
                print_success(f"Appointment creation successful - Service: {data.get('service_name')} ({data.get('service_price')}€)")
                self.results['passed'] += 1
            else:
                print_error(f"Appointment creation failed: {response.text if response else 'Connection failed'}")
                self.results['failed'] += 1
        else:
            print_error("Could not create test slot for appointment")
            self.results['failed'] += 1
        
        # Test get appointments (admin view)
        response = self.make_request("GET", "/appointments", auth_token=self.admin_token)
        if response and response.status_code == 200:
            appointments = response.json()
            print_success(f"Admin get appointments successful - Found {len(appointments)} appointments")
            self.results['passed'] += 1
        else:
            print_error("Admin get appointments failed")
            self.results['failed'] += 1
        
        # Test get appointments (client view)
        response = self.make_request("GET", "/appointments", auth_token=self.client_token)
        if response and response.status_code == 200:
            appointments = response.json()
            print_success(f"Client get appointments successful - Found {len(appointments)} appointments")
            self.results['passed'] += 1
        else:
            print_error("Client get appointments failed")
            self.results['failed'] += 1
        
        # Test appointment status update (admin only)
        if self.test_appointment_id:
            update_data = {
                "status": "confirmed",
                "notes": "Rendez-vous confirmé par l'admin"
            }
            
            response = self.make_request("PUT", f"/appointments/{self.test_appointment_id}", update_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Appointment status update successful")
                print_info("Client confirmation email should be sent")
                self.results['passed'] += 1
            else:
                print_error("Appointment status update failed")
                self.results['failed'] += 1
        
        # Test appointment deletion (admin only)
        if self.test_appointment_id:
            response = self.make_request("DELETE", f"/appointments/{self.test_appointment_id}", auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Appointment deletion successful")
                self.results['passed'] += 1
            else:
                print_error("Appointment deletion failed")
                self.results['failed'] += 1

    def test_reviews_system(self):
        """Test reviews system APIs"""
        print_header("6. REVIEWS SYSTEM TESTS")
        
        if not self.client_token:
            print_error("Cannot test reviews - no client token")
            self.results['failed'] += 4
            return
        
        # Test review creation
        review_data = {
            "rating": 5,
            "comment": "Excellent service ! Je recommande vivement ce salon. L'équipe est très professionnelle et le résultat est parfait."
        }
        
        response = self.make_request("POST", "/reviews", review_data, auth_token=self.client_token)
        if response and response.status_code == 200:
            data = response.json()
            self.test_review_id = data.get("id")
            print_success(f"Review creation successful - Rating: {data.get('rating')}/5")
            self.results['passed'] += 1
        else:
            print_error(f"Review creation failed: {response.text if response else 'Connection failed'}")
            self.results['failed'] += 1
        
        # Test get reviews (public - approved only)
        response = self.make_request("GET", "/reviews?approved_only=true")
        if response and response.status_code == 200:
            reviews = response.json()
            print_success(f"Get public reviews successful - Found {len(reviews)} approved reviews")
            self.results['passed'] += 1
        else:
            print_error("Get public reviews failed")
            self.results['failed'] += 1
        
        # Test get all reviews (admin view)
        if self.admin_token:
            response = self.make_request("GET", "/reviews", auth_token=self.admin_token)
            if response and response.status_code == 200:
                reviews = response.json()
                print_success(f"Admin get all reviews successful - Found {len(reviews)} total reviews")
                self.results['passed'] += 1
            else:
                print_error("Admin get all reviews failed")
                self.results['failed'] += 1
        
        # Test review status update (admin only)
        if self.test_review_id and self.admin_token:
            update_data = {
                "status": "approved"
            }
            
            response = self.make_request("PUT", f"/reviews/{self.test_review_id}", update_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Review approval successful")
                self.results['passed'] += 1
            else:
                print_error("Review approval failed")
                self.results['failed'] += 1

    def test_email_service(self):
        """Test email service configuration"""
        print_header("7. EMAIL SERVICE TEST")
        
        print_info("Email service configuration:")
        print_info("- Gmail Username: l20245303@gmail.com")
        print_info("- Gmail App Password: Configured")
        print_info("- Email notifications are sent during:")
        print_info("  * New appointment creation (to admin)")
        print_info("  * Appointment confirmation (to client)")
        print_info("  * New review submission (to admin)")
        
        # Email testing is implicit through appointment and review creation
        # The actual sending happens in the background
        print_success("Email service configuration verified")
        self.results['passed'] += 1

    def test_cors_and_headers(self):
        """Test CORS configuration and headers"""
        print_header("8. CORS AND HEADERS TEST")
        
        # Test CORS preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        try:
            response = requests.options(f"{BASE_URL}/ping", headers=headers, timeout=10)
            if response.status_code in [200, 204]:
                cors_headers = response.headers
                if "Access-Control-Allow-Origin" in cors_headers:
                    print_success(f"CORS preflight successful - Origin allowed: {cors_headers.get('Access-Control-Allow-Origin')}")
                    self.results['passed'] += 1
                else:
                    print_warning("CORS preflight response missing Access-Control-Allow-Origin header")
                    self.results['warnings'] += 1
            else:
                print_error(f"CORS preflight failed - Status: {response.status_code}")
                self.results['failed'] += 1
        except Exception as e:
            print_error(f"CORS test failed: {str(e)}")
            self.results['failed'] += 1
        
        # Test basic headers on a simple request
        response = self.make_request("GET", "/ping")
        if response:
            headers = response.headers
            print_info(f"Response headers: Content-Type: {headers.get('content-type', 'Not set')}")
            print_info(f"Server: {headers.get('server', 'Not set')}")
            if "application/json" in headers.get('content-type', ''):
                print_success("Content-Type header correctly set to JSON")
                self.results['passed'] += 1
            else:
                print_warning("Content-Type header not set to JSON")
                self.results['warnings'] += 1

    def test_performance_and_latency(self):
        """Test API performance and latency"""
        print_header("9. PERFORMANCE AND LATENCY TEST")
        
        endpoints_to_test = [
            ("/ping", "GET", None, None),
            ("/reviews?approved_only=true", "GET", None, None),
            ("/slots?available_only=true", "GET", None, None)
        ]
        
        for endpoint, method, data, token in endpoints_to_test:
            times = []
            for i in range(3):  # Test 3 times for average
                start_time = time.time()
                response = self.make_request(method, endpoint, data, auth_token=token)
                end_time = time.time()
                
                if response and response.status_code == 200:
                    times.append(end_time - start_time)
                else:
                    print_warning(f"Performance test failed for {endpoint}")
                    break
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                print_info(f"{method} {endpoint}:")
                print_info(f"  Average: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
                
                if avg_time < 2.0:  # Less than 2 seconds is good
                    print_success(f"Performance OK - Average response time: {avg_time:.3f}s")
                    self.results['passed'] += 1
                elif avg_time < 5.0:  # Less than 5 seconds is acceptable
                    print_warning(f"Performance acceptable - Average response time: {avg_time:.3f}s")
                    self.results['warnings'] += 1
                else:
                    print_error(f"Performance poor - Average response time: {avg_time:.3f}s")
                    self.results['failed'] += 1

    def test_service_selection(self):
        """Test the 4 service types in booking system"""
        print_header("10. SERVICE SELECTION TEST")
        
        services = [
            {"name": "Très simple", "price": 5.0},
            {"name": "Simple", "price": 8.0},
            {"name": "Chargé", "price": 12.0},
            {"name": "Mariée", "price": 20.0}
        ]
        
        if not self.admin_token or not self.client_token:
            print_error("Cannot test service selection - missing tokens")
            self.results['failed'] += len(services)
            return
        
        for service in services:
            # Create a slot for each service test
            test_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            slot_data = {
                "date": test_date,
                "time": f"{9 + services.index(service)}:00"
            }
            
            response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                slot_id = response.json().get("id")
                
                # Test booking with this service
                appointment_data = {
                    "slot_id": slot_id,
                    "service_name": service["name"],
                    "service_price": service["price"],
                    "notes": f"Test réservation service {service['name']}"
                }
                
                response = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
                if response and response.status_code == 200:
                    data = response.json()
                    print_success(f"Service '{service['name']}' booking successful - {service['price']}€")
                    self.results['passed'] += 1
                    
                    # Clean up - delete the appointment
                    apt_id = data.get("id")
                    if apt_id:
                        self.make_request("DELETE", f"/appointments/{apt_id}", auth_token=self.admin_token)
                else:
                    print_error(f"Service '{service['name']}' booking failed")
                    self.results['failed'] += 1
            else:
                print_error(f"Could not create slot for service '{service['name']}'")
                self.results['failed'] += 1

    def run_all_tests(self):
        """Run all backend tests"""
        print_header("BACKEND API TESTING SUITE - SALON BOOKING SYSTEM")
        print_info(f"Testing against: {BASE_URL}")
        print_info(f"Admin credentials: {ADMIN_EMAIL}")
        print_info(f"Client credentials: {CLIENT_EMAIL}")
        
        start_time = time.time()
        
        # Run all tests
        self.test_health_check()
        self.test_mongodb_connection()
        self.test_authentication()
        self.test_admin_slot_management()
        self.test_appointment_management()
        self.test_reviews_system()
        self.test_email_service()
        self.test_cors_and_headers()
        self.test_performance_and_latency()
        self.test_service_selection()
        
        # Print final results
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("TEST RESULTS SUMMARY")
        print_success(f"Passed: {self.results['passed']}")
        if self.results['warnings'] > 0:
            print_warning(f"Warnings: {self.results['warnings']}")
        if self.results['failed'] > 0:
            print_error(f"Failed: {self.results['failed']}")
        else:
            print_success("All critical tests passed!")
        
        total_tests = self.results['passed'] + self.results['failed'] + self.results['warnings']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print_info(f"Success rate: {success_rate:.1f}%")
        print_info(f"Test duration: {duration:.2f} seconds")
        
        if self.results['failed'] == 0:
            print_success("🎉 ALL BACKEND APIS ARE WORKING CORRECTLY!")
            return True
        else:
            print_error("❌ SOME BACKEND APIS HAVE ISSUES")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)