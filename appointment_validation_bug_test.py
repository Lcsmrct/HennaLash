#!/usr/bin/env python3
"""
Focused Test for Appointment Validation Bug
Tests specifically the bug where client notes disappear after appointment validation
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")

class AppointmentValidationTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_slot_id = None
        self.test_appointment_id = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'critical_issues': []
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
        print_header("AUTHENTICATION SETUP")
        
        # Test admin login with multiple password attempts
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
                    print_success(f"Admin login successful with password '{password}'")
                    admin_login_success = True
                    break
        
        if not admin_login_success:
            print_error("Admin login failed with all attempted passwords")
            self.results['critical_issues'].append("Cannot authenticate admin user")
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
                print_success("Client login successful")
            else:
                print_error("Client login - No token in response")
                self.results['critical_issues'].append("Cannot get client token")
                return False
        else:
            print_error("Client login failed")
            self.results['critical_issues'].append("Cannot authenticate client user")
            return False
        
        return True

    def create_test_appointment_with_detailed_notes(self):
        """Create an appointment with detailed client notes (Instagram, location, etc.)"""
        print_header("STEP 1: CREATE APPOINTMENT WITH DETAILED CLIENT NOTES")
        
        # First create a slot for booking
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "15:30"
        }
        
        response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error("Failed to create test slot")
            self.results['critical_issues'].append("Cannot create test slot")
            return False
        
        slot_data_response = response.json()
        self.test_slot_id = slot_data_response.get("id")
        print_success(f"Test slot created - ID: {self.test_slot_id}")
        print_info(f"Slot details: {tomorrow} {slot_data_response.get('start_time')}-{slot_data_response.get('end_time')}")
        
        # Create appointment with detailed client notes
        detailed_notes = """Instagram: @marie_beauty_lover
Lieu préféré: Salon principal (pas l'annexe)
Allergies: Aucune allergie connue
Préférences: Henné naturel, couleur marron foncé
Remarques spéciales: Premier rendez-vous, un peu stressée
Contact d'urgence: 06.12.34.56.78
Parking: Préfère se garer devant le salon"""
        
        appointment_data = {
            "slot_id": self.test_slot_id,
            "service_name": "Chargé",
            "service_price": 12.0,
            "notes": detailed_notes
        }
        
        response = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
        if not response or response.status_code != 200:
            print_error("Failed to create appointment with detailed notes")
            self.results['critical_issues'].append("Cannot create appointment")
            return False
        
        appointment_response = response.json()
        self.test_appointment_id = appointment_response.get("id")
        print_success(f"Appointment created with detailed notes - ID: {self.test_appointment_id}")
        print_info(f"Service: {appointment_response.get('service_name')} ({appointment_response.get('service_price')}€)")
        print_info(f"Notes length: {len(appointment_response.get('notes', ''))} characters")
        
        return True

    def verify_appointment_before_validation(self):
        """Verify appointment contains all info before validation"""
        print_header("STEP 2: VERIFY APPOINTMENT DATA BEFORE VALIDATION")
        
        # Get appointment from admin view (should have aggregated data)
        response = self.make_request("GET", "/appointments", auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error("Failed to get appointments from admin view")
            self.results['critical_issues'].append("Cannot retrieve appointments")
            return False
        
        appointments = response.json()
        test_appointment = None
        
        for apt in appointments:
            if apt.get("id") == self.test_appointment_id:
                test_appointment = apt
                break
        
        if not test_appointment:
            print_error("Test appointment not found in admin view")
            self.results['critical_issues'].append("Test appointment not found")
            return False
        
        print_success("Test appointment found in admin view")
        
        # Verify all required fields are present
        required_fields = {
            'notes': 'Client notes with Instagram/location info',
            'service_name': 'Service name',
            'service_price': 'Service price',
            'user_name': 'User name (aggregated)',
            'user_email': 'User email (aggregated)',
            'slot_info': 'Slot information (aggregated)'
        }
        
        missing_fields = []
        for field, description in required_fields.items():
            if field not in test_appointment or not test_appointment[field]:
                missing_fields.append(f"{field} ({description})")
            else:
                print_success(f"✓ {description}: Present")
        
        if missing_fields:
            print_error(f"Missing fields before validation: {', '.join(missing_fields)}")
            self.results['critical_issues'].append(f"Missing fields: {missing_fields}")
            return False
        
        # Verify client notes contain expected information
        notes = test_appointment.get('notes', '')
        expected_keywords = ['Instagram', 'Lieu', 'Allergies', 'Préférences', 'Contact']
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword not in notes:
                missing_keywords.append(keyword)
            else:
                print_success(f"✓ Notes contain '{keyword}' information")
        
        if missing_keywords:
            print_warning(f"Notes missing some keywords: {missing_keywords}")
        
        # Verify slot_info contains date and time
        slot_info = test_appointment.get('slot_info', {})
        if isinstance(slot_info, dict):
            if 'date' in slot_info and 'start_time' in slot_info:
                print_success(f"✓ Slot info complete: {slot_info.get('date')} {slot_info.get('start_time')}")
            else:
                print_error("Slot info missing date or start_time")
                self.results['critical_issues'].append("Incomplete slot_info before validation")
                return False
        else:
            print_error("Slot info is not a dictionary")
            self.results['critical_issues'].append("Invalid slot_info format")
            return False
        
        print_success("All appointment data verified before validation")
        self.results['passed'] += 1
        return True

    def validate_appointment_and_check_data_preservation(self):
        """Validate appointment and verify data preservation"""
        print_header("STEP 3: VALIDATE APPOINTMENT AND CHECK DATA PRESERVATION")
        
        # Update appointment status to confirmed with admin notes
        admin_notes = "Rendez-vous confirmé. Client contacté par téléphone."
        update_data = {
            "status": "confirmed",
            "notes": admin_notes
        }
        
        print_info(f"Validating appointment {self.test_appointment_id} with admin notes...")
        
        response = self.make_request("PUT", f"/appointments/{self.test_appointment_id}/status", update_data, auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error(f"Failed to validate appointment: {response.status_code if response else 'Connection failed'}")
            if response:
                print_error(f"Response: {response.text}")
            self.results['critical_issues'].append("Cannot validate appointment")
            return False
        
        validated_appointment = response.json()
        print_success("Appointment validation successful")
        
        # Verify the response contains all required data
        print_info("Checking data preservation after validation...")
        
        # Check 1: Original client notes should be preserved
        notes = validated_appointment.get('notes', '')
        if 'Instagram' in notes and 'Lieu' in notes:
            print_success("✓ Original client notes preserved (Instagram, Lieu info present)")
            self.results['passed'] += 1
        else:
            print_error("❌ CRITICAL BUG: Original client notes lost after validation")
            self.results['critical_issues'].append("Client notes lost during validation")
            self.results['failed'] += 1
        
        # Check if admin notes were appended correctly
        if admin_notes in notes:
            print_success("✓ Admin notes correctly appended")
            self.results['passed'] += 1
        else:
            print_warning("Admin notes not found in response")
        
        # Check 2: Slot info should be complete
        slot_info = validated_appointment.get('slot_info', {})
        if isinstance(slot_info, dict) and 'date' in slot_info and 'start_time' in slot_info:
            print_success(f"✓ Slot info preserved: {slot_info.get('date')} {slot_info.get('start_time')}")
            self.results['passed'] += 1
        else:
            print_error("❌ CRITICAL BUG: Slot info missing or incomplete after validation")
            self.results['critical_issues'].append("Slot info lost during validation")
            self.results['failed'] += 1
        
        # Check 3: User information should be present
        user_name = validated_appointment.get('user_name')
        user_email = validated_appointment.get('user_email')
        if user_name and user_email:
            print_success(f"✓ User info preserved: {user_name} ({user_email})")
            self.results['passed'] += 1
        else:
            print_error("❌ CRITICAL BUG: User info missing after validation")
            self.results['critical_issues'].append("User info lost during validation")
            self.results['failed'] += 1
        
        # Check 4: Status should be updated
        status = validated_appointment.get('status')
        if status == 'confirmed':
            print_success("✓ Status correctly updated to 'confirmed'")
            self.results['passed'] += 1
        else:
            print_error(f"❌ Status not updated correctly: {status}")
            self.results['failed'] += 1
        
        # Check 5: Service information should be preserved
        service_name = validated_appointment.get('service_name')
        service_price = validated_appointment.get('service_price')
        if service_name and service_price:
            print_success(f"✓ Service info preserved: {service_name} ({service_price}€)")
            self.results['passed'] += 1
        else:
            print_error("❌ Service info missing after validation")
            self.results['failed'] += 1
        
        return True

    def test_client_side_appointment_retrieval(self):
        """Test client side - get appointment list and verify info is complete"""
        print_header("STEP 4: TEST CLIENT SIDE APPOINTMENT RETRIEVAL")
        
        # Get appointments from client view
        response = self.make_request("GET", "/appointments", auth_token=self.client_token)
        if not response or response.status_code != 200:
            print_error("Failed to get appointments from client view")
            self.results['critical_issues'].append("Cannot retrieve client appointments")
            return False
        
        client_appointments = response.json()
        test_appointment = None
        
        for apt in client_appointments:
            if apt.get("id") == self.test_appointment_id:
                test_appointment = apt
                break
        
        if not test_appointment:
            print_error("Test appointment not found in client view")
            self.results['critical_issues'].append("Appointment not visible to client")
            return False
        
        print_success("Test appointment found in client view")
        
        # Verify client can see their appointment details
        notes = test_appointment.get('notes', '')
        if 'Instagram' in notes:
            print_success("✓ Client can see their original notes")
            self.results['passed'] += 1
        else:
            print_error("❌ Client cannot see their original notes")
            self.results['failed'] += 1
        
        # Check if client can see appointment status
        status = test_appointment.get('status')
        if status == 'confirmed':
            print_success("✓ Client can see confirmed status")
            self.results['passed'] += 1
        else:
            print_error(f"❌ Client status incorrect: {status}")
            self.results['failed'] += 1
        
        # Check service information visibility
        service_name = test_appointment.get('service_name')
        if service_name:
            print_success(f"✓ Client can see service: {service_name}")
            self.results['passed'] += 1
        else:
            print_error("❌ Client cannot see service information")
            self.results['failed'] += 1
        
        return True

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

    def run_bug_test(self):
        """Run the complete bug test"""
        print_header("APPOINTMENT VALIDATION BUG TEST")
        print_info("Testing the specific bug where client notes disappear after appointment validation")
        print_info(f"Testing against: {BASE_URL}")
        
        start_time = time.time()
        
        # Step 1: Authentication
        if not self.authenticate():
            return False
        
        # Step 2: Create appointment with detailed notes
        if not self.create_test_appointment_with_detailed_notes():
            return False
        
        # Step 3: Verify data before validation
        if not self.verify_appointment_before_validation():
            return False
        
        # Step 4: Validate appointment and check data preservation
        if not self.validate_appointment_and_check_data_preservation():
            return False
        
        # Step 5: Test client side retrieval
        if not self.test_client_side_appointment_retrieval():
            return False
        
        # Cleanup
        self.cleanup()
        
        # Print results
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("BUG TEST RESULTS")
        print_success(f"Passed checks: {self.results['passed']}")
        if self.results['failed'] > 0:
            print_error(f"Failed checks: {self.results['failed']}")
        
        if self.results['critical_issues']:
            print_error("CRITICAL ISSUES FOUND:")
            for issue in self.results['critical_issues']:
                print_error(f"  • {issue}")
        
        print_info(f"Test duration: {duration:.2f} seconds")
        
        if self.results['failed'] == 0 and not self.results['critical_issues']:
            print_success("🎉 BUG TEST PASSED - No data loss during appointment validation!")
            return True
        else:
            print_error("❌ BUG TEST FAILED - Data loss detected during appointment validation")
            return False

if __name__ == "__main__":
    tester = AppointmentValidationTester()
    success = tester.run_bug_test()
    sys.exit(0 if success else 1)