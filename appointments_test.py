#!/usr/bin/env python3
"""
Focused test for appointments endpoint - specifically testing slot_info data structure
Based on user report: "les rendez-vous affichent 'Date/Heure non spécifiée'"
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration - Use external URL as specified in frontend/.env
BASE_URL = "https://henna-lash.onrender.com/api"
ADMIN_EMAIL = "admin@salon.com"
ADMIN_PASSWORD = "testadmin123"
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

class AppointmentsTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_slot_id = None
        self.test_appointment_id = None
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
                response = requests.get(url, headers=headers, timeout=15)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
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

    def authenticate(self):
        """Authenticate admin and client users"""
        print_header("AUTHENTICATION")
        
        # Test admin login
        admin_login = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.admin_token = data["access_token"]
                print_success("Admin authentication successful")
                self.results['passed'] += 1
            else:
                print_error("Admin login - No token in response")
                self.results['failed'] += 1
                return False
        else:
            print_error("Admin login failed")
            self.results['failed'] += 1
            return False
        
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
                print_success("Client authentication successful")
                self.results['passed'] += 1
                return True
            else:
                print_error("Client login - No token in response")
                self.results['failed'] += 1
                return False
        else:
            print_error("Client login failed")
            self.results['failed'] += 1
            return False

    def create_test_appointment(self):
        """Create a test appointment to analyze slot_info data"""
        print_header("CREATING TEST APPOINTMENT")
        
        # First create a slot
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "15:30"
        }
        
        response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            slot_data_response = response.json()
            self.test_slot_id = slot_data_response.get("id")
            print_success(f"Test slot created - ID: {self.test_slot_id}")
            print_info(f"Slot details: Date={slot_data_response.get('date')}, Start={slot_data_response.get('start_time')}, End={slot_data_response.get('end_time')}")
            self.results['passed'] += 1
        else:
            print_error(f"Failed to create test slot: {response.text if response else 'Connection failed'}")
            self.results['failed'] += 1
            return False
        
        # Create appointment with service selection
        appointment_data = {
            "slot_id": self.test_slot_id,
            "service_name": "Chargé",
            "service_price": 12.0,
            "notes": "Test appointment pour vérifier structure slot_info"
        }
        
        response = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
        if response and response.status_code == 200:
            data = response.json()
            self.test_appointment_id = data.get("id")
            print_success(f"Test appointment created - ID: {self.test_appointment_id}")
            print_info(f"Service: {data.get('service_name')} - {data.get('service_price')}€")
            self.results['passed'] += 1
            return True
        else:
            print_error(f"Failed to create test appointment: {response.text if response else 'Connection failed'}")
            self.results['failed'] += 1
            return False

    def test_appointments_endpoint_structure(self):
        """Test GET /api/appointments endpoint and analyze slot_info structure"""
        print_header("TESTING APPOINTMENTS ENDPOINT - SLOT_INFO STRUCTURE")
        
        # Test admin view of appointments
        response = self.make_request("GET", "/appointments", auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error("Failed to get appointments from admin view")
            self.results['failed'] += 1
            return
        
        appointments = response.json()
        print_success(f"Retrieved {len(appointments)} appointments from admin view")
        
        if not appointments:
            print_warning("No appointments found - cannot test slot_info structure")
            self.results['warnings'] += 1
            return
        
        # Analyze each appointment's structure
        for i, appointment in enumerate(appointments):
            print_info(f"\n--- APPOINTMENT {i+1} ANALYSIS ---")
            print_info(f"Appointment ID: {appointment.get('id', 'MISSING')}")
            print_info(f"User Name: {appointment.get('user_name', 'MISSING')}")
            print_info(f"User Email: {appointment.get('user_email', 'MISSING')}")
            print_info(f"Service Name: {appointment.get('service_name', 'MISSING')}")
            print_info(f"Service Price: {appointment.get('service_price', 'MISSING')}")
            print_info(f"Status: {appointment.get('status', 'MISSING')}")
            
            # CRITICAL: Check slot_info structure
            slot_info = appointment.get('slot_info')
            if slot_info is None:
                print_error("❌ CRITICAL: slot_info is NULL/missing")
                self.results['failed'] += 1
                continue
            elif not slot_info:
                print_error("❌ CRITICAL: slot_info is empty")
                self.results['failed'] += 1
                continue
            
            print_success("✅ slot_info exists and is not empty")
            
            # Check required fields in slot_info
            required_fields = ['date', 'start_time', 'end_time']
            all_fields_present = True
            
            for field in required_fields:
                value = slot_info.get(field)
                if value is None:
                    print_error(f"❌ CRITICAL: slot_info.{field} is NULL")
                    all_fields_present = False
                    self.results['failed'] += 1
                elif value == "":
                    print_error(f"❌ CRITICAL: slot_info.{field} is empty string")
                    all_fields_present = False
                    self.results['failed'] += 1
                else:
                    print_success(f"✅ slot_info.{field} = '{value}'")
                    
                    # Validate format
                    if field == 'date':
                        try:
                            # Try to parse the date
                            if 'T' in str(value):
                                datetime.fromisoformat(str(value).replace('Z', '+00:00'))
                                print_success(f"✅ slot_info.date format is valid ISO datetime")
                            else:
                                datetime.strptime(str(value), "%Y-%m-%d")
                                print_success(f"✅ slot_info.date format is valid YYYY-MM-DD")
                        except ValueError:
                            print_error(f"❌ slot_info.date format is invalid: {value}")
                            self.results['failed'] += 1
                    
                    elif field in ['start_time', 'end_time']:
                        try:
                            # Try to parse the time
                            datetime.strptime(str(value), "%H:%M")
                            print_success(f"✅ slot_info.{field} format is valid HH:MM")
                        except ValueError:
                            print_error(f"❌ slot_info.{field} format is invalid: {value}")
                            self.results['failed'] += 1
            
            if all_fields_present:
                print_success("✅ ALL REQUIRED SLOT_INFO FIELDS PRESENT AND VALID")
                self.results['passed'] += 1
            else:
                print_error("❌ SOME SLOT_INFO FIELDS ARE MISSING OR INVALID")
        
        # Test client view of appointments
        print_info("\n--- TESTING CLIENT VIEW ---")
        response = self.make_request("GET", "/appointments", auth_token=self.client_token)
        if response and response.status_code == 200:
            client_appointments = response.json()
            print_success(f"Client can retrieve {len(client_appointments)} appointments")
            
            # Check if client appointments also have slot_info
            for appointment in client_appointments:
                slot_info = appointment.get('slot_info')
                if slot_info and slot_info.get('date') and slot_info.get('start_time') and slot_info.get('end_time'):
                    print_success("✅ Client appointments also have complete slot_info")
                    self.results['passed'] += 1
                    break
            else:
                print_warning("⚠️ Client appointments may not have complete slot_info")
                self.results['warnings'] += 1
        else:
            print_error("Failed to get appointments from client view")
            self.results['failed'] += 1

    def test_frontend_compatibility(self):
        """Test if the data structure is compatible with frontend expectations"""
        print_header("TESTING FRONTEND COMPATIBILITY")
        
        response = self.make_request("GET", "/appointments", auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error("Cannot test frontend compatibility - no appointments data")
            self.results['failed'] += 1
            return
        
        appointments = response.json()
        if not appointments:
            print_warning("No appointments to test frontend compatibility")
            self.results['warnings'] += 1
            return
        
        appointment = appointments[0]  # Test first appointment
        slot_info = appointment.get('slot_info')
        
        if not slot_info:
            print_error("❌ Cannot test frontend compatibility - no slot_info")
            self.results['failed'] += 1
            return
        
        # Simulate frontend checks that would cause "Date/Heure non spécifiée"
        print_info("Simulating frontend checks...")
        
        # Check 1: Truthiness test (JavaScript-style)
        date_value = slot_info.get('date')
        start_time_value = slot_info.get('start_time')
        end_time_value = slot_info.get('end_time')
        
        if date_value and str(date_value).strip():
            print_success("✅ slot_info.date passes JavaScript truthiness test")
        else:
            print_error("❌ slot_info.date would fail JavaScript truthiness test")
            self.results['failed'] += 1
        
        if start_time_value and str(start_time_value).strip():
            print_success("✅ slot_info.start_time passes JavaScript truthiness test")
        else:
            print_error("❌ slot_info.start_time would fail JavaScript truthiness test")
            self.results['failed'] += 1
        
        if end_time_value and str(end_time_value).strip():
            print_success("✅ slot_info.end_time passes JavaScript truthiness test")
        else:
            print_error("❌ slot_info.end_time would fail JavaScript truthiness test")
            self.results['failed'] += 1
        
        # Check 2: JSON serialization test
        try:
            json_str = json.dumps(appointment)
            parsed_back = json.loads(json_str)
            parsed_slot_info = parsed_back.get('slot_info', {})
            
            if (parsed_slot_info.get('date') and 
                parsed_slot_info.get('start_time') and 
                parsed_slot_info.get('end_time')):
                print_success("✅ Appointment data survives JSON serialization/deserialization")
                self.results['passed'] += 1
            else:
                print_error("❌ Appointment data corrupted during JSON serialization")
                self.results['failed'] += 1
        except Exception as e:
            print_error(f"❌ JSON serialization failed: {str(e)}")
            self.results['failed'] += 1

    def cleanup(self):
        """Clean up test data"""
        print_header("CLEANUP")
        
        if self.test_appointment_id and self.admin_token:
            response = self.make_request("DELETE", f"/appointments/{self.test_appointment_id}", auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Test appointment deleted")
            else:
                print_warning("Could not delete test appointment")
        
        if self.test_slot_id and self.admin_token:
            response = self.make_request("DELETE", f"/slots/{self.test_slot_id}", auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("Test slot deleted")
            else:
                print_warning("Could not delete test slot")

    def run_focused_test(self):
        """Run focused test on appointments endpoint"""
        print_header("FOCUSED APPOINTMENTS ENDPOINT TEST")
        print_info(f"Testing against: {BASE_URL}")
        print_info("Focus: slot_info data structure in appointments")
        print_info("User issue: 'Date/Heure non spécifiée' in appointments display")
        
        start_time = time.time()
        
        # Run tests
        if not self.authenticate():
            print_error("Authentication failed - cannot continue")
            return False
        
        if not self.create_test_appointment():
            print_error("Could not create test appointment - testing existing data only")
        
        self.test_appointments_endpoint_structure()
        self.test_frontend_compatibility()
        self.cleanup()
        
        # Print results
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("TEST RESULTS")
        print_success(f"Passed: {self.results['passed']}")
        if self.results['warnings'] > 0:
            print_warning(f"Warnings: {self.results['warnings']}")
        if self.results['failed'] > 0:
            print_error(f"Failed: {self.results['failed']}")
        
        total_tests = self.results['passed'] + self.results['failed'] + self.results['warnings']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print_info(f"Success rate: {success_rate:.1f}%")
        print_info(f"Test duration: {duration:.2f} seconds")
        
        if self.results['failed'] == 0:
            print_success("🎉 APPOINTMENTS ENDPOINT SLOT_INFO STRUCTURE IS CORRECT!")
            return True
        else:
            print_error("❌ APPOINTMENTS ENDPOINT HAS SLOT_INFO ISSUES")
            return False

if __name__ == "__main__":
    tester = AppointmentsTester()
    success = tester.run_focused_test()
    exit(0 if success else 1)