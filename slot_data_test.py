#!/usr/bin/env python3
"""
Slot Data Structure Testing - Urgent Test for Client Dashboard Issue
Tests specifically for the slot data structure issue where client dashboard shows:
"Date non spécifiée" and "Heure non spécifiée"

PROBLEM: Client dashboard shows undefined date and time for slots
TESTS: 
1. GET /api/slots?available_only=true (used by client dashboard)
2. Verify data structure (date, start_time, end_time fields)
3. Check if slots have valid JSON data
4. Verify admin-created slots have proper date/start_time/end_time
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration - Use external URL as per frontend .env
BASE_URL = "https://henna-lash.onrender.com/api"
ADMIN_EMAIL = "admin@salon.com"
ADMIN_PASSWORD = "testadmin123"

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

class SlotDataTester:
    def __init__(self):
        self.admin_token = None
        self.results = {'passed': 0, 'failed': 0, 'critical_issues': []}

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

    def authenticate_admin(self):
        """Authenticate as admin to create test slots"""
        print_header("ADMIN AUTHENTICATION")
        
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
                return True
            else:
                print_error("Admin login - No token in response")
                return False
        else:
            print_error(f"Admin login failed: {response.status_code if response else 'Connection failed'}")
            return False

    def test_client_dashboard_slots_endpoint(self):
        """Test the exact endpoint used by client dashboard"""
        print_header("1. CLIENT DASHBOARD SLOTS ENDPOINT TEST")
        print_info("Testing GET /api/slots?available_only=true (endpoint used by client dashboard)")
        
        response = self.make_request("GET", "/slots?available_only=true")
        if not response:
            self.results['failed'] += 1
            self.results['critical_issues'].append("Cannot connect to slots endpoint")
            return None
        
        if response.status_code != 200:
            print_error(f"Slots endpoint failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            self.results['failed'] += 1
            self.results['critical_issues'].append(f"Slots endpoint returns {response.status_code}")
            return None
        
        try:
            slots_data = response.json()
            print_success(f"Slots endpoint accessible - Found {len(slots_data)} available slots")
            self.results['passed'] += 1
            return slots_data
        except json.JSONDecodeError:
            print_error("Invalid JSON response from slots endpoint")
            self.results['failed'] += 1
            self.results['critical_issues'].append("Invalid JSON from slots endpoint")
            return None

    def analyze_slot_data_structure(self, slots_data):
        """Analyze the structure of slot data returned by API"""
        print_header("2. SLOT DATA STRUCTURE ANALYSIS")
        
        if not slots_data:
            print_error("No slots data to analyze")
            self.results['failed'] += 1
            return
        
        if len(slots_data) == 0:
            print_warning("No available slots found - creating test slot for analysis")
            test_slot = self.create_test_slot()
            if test_slot:
                slots_data = [test_slot]
            else:
                print_error("Cannot create test slot for analysis")
                self.results['failed'] += 1
                return
        
        print_info(f"Analyzing {len(slots_data)} slots...")
        
        # Analyze first slot in detail
        first_slot = slots_data[0]
        print_info("First slot data structure:")
        print(json.dumps(first_slot, indent=2, default=str))
        
        # Check required fields
        required_fields = ['id', 'date', 'start_time', 'end_time', 'is_available']
        missing_fields = []
        
        for field in required_fields:
            if field not in first_slot:
                missing_fields.append(field)
            else:
                field_value = first_slot[field]
                print_info(f"✓ {field}: {field_value} (type: {type(field_value).__name__})")
        
        if missing_fields:
            print_error(f"Missing required fields: {missing_fields}")
            self.results['failed'] += 1
            self.results['critical_issues'].append(f"Missing fields in slot data: {missing_fields}")
        else:
            print_success("All required fields present in slot data")
            self.results['passed'] += 1
        
        # Check data types and values
        self.validate_slot_field_values(first_slot)
        
        # Check all slots for consistency
        self.check_all_slots_consistency(slots_data)

    def validate_slot_field_values(self, slot):
        """Validate individual slot field values"""
        print_header("3. SLOT FIELD VALUES VALIDATION")
        
        # Check date field
        date_value = slot.get('date')
        if date_value is None:
            print_error("❌ CRITICAL: date field is None/null")
            self.results['critical_issues'].append("Slot date field is None")
            self.results['failed'] += 1
        elif date_value == "":
            print_error("❌ CRITICAL: date field is empty string")
            self.results['critical_issues'].append("Slot date field is empty")
            self.results['failed'] += 1
        else:
            try:
                # Try to parse date
                if isinstance(date_value, str):
                    datetime.strptime(date_value, "%Y-%m-%d")
                    print_success(f"✅ date field valid: {date_value}")
                    self.results['passed'] += 1
                else:
                    print_info(f"Date field type: {type(date_value)} - Value: {date_value}")
                    self.results['passed'] += 1
            except ValueError:
                print_error(f"❌ CRITICAL: Invalid date format: {date_value}")
                self.results['critical_issues'].append(f"Invalid date format: {date_value}")
                self.results['failed'] += 1
        
        # Check start_time field
        start_time_value = slot.get('start_time')
        if start_time_value is None:
            print_error("❌ CRITICAL: start_time field is None/null")
            self.results['critical_issues'].append("Slot start_time field is None")
            self.results['failed'] += 1
        elif start_time_value == "":
            print_error("❌ CRITICAL: start_time field is empty string")
            self.results['critical_issues'].append("Slot start_time field is empty")
            self.results['failed'] += 1
        else:
            try:
                # Try to parse time
                if isinstance(start_time_value, str):
                    datetime.strptime(start_time_value, "%H:%M")
                    print_success(f"✅ start_time field valid: {start_time_value}")
                    self.results['passed'] += 1
                else:
                    print_info(f"Start_time field type: {type(start_time_value)} - Value: {start_time_value}")
                    self.results['passed'] += 1
            except ValueError:
                print_error(f"❌ CRITICAL: Invalid start_time format: {start_time_value}")
                self.results['critical_issues'].append(f"Invalid start_time format: {start_time_value}")
                self.results['failed'] += 1
        
        # Check end_time field
        end_time_value = slot.get('end_time')
        if end_time_value is None:
            print_error("❌ CRITICAL: end_time field is None/null")
            self.results['critical_issues'].append("Slot end_time field is None")
            self.results['failed'] += 1
        elif end_time_value == "":
            print_error("❌ CRITICAL: end_time field is empty string")
            self.results['critical_issues'].append("Slot end_time field is empty")
            self.results['failed'] += 1
        else:
            try:
                # Try to parse time
                if isinstance(end_time_value, str):
                    datetime.strptime(end_time_value, "%H:%M")
                    print_success(f"✅ end_time field valid: {end_time_value}")
                    self.results['passed'] += 1
                else:
                    print_info(f"End_time field type: {type(end_time_value)} - Value: {end_time_value}")
                    self.results['passed'] += 1
            except ValueError:
                print_error(f"❌ CRITICAL: Invalid end_time format: {end_time_value}")
                self.results['critical_issues'].append(f"Invalid end_time format: {end_time_value}")
                self.results['failed'] += 1

    def check_all_slots_consistency(self, slots_data):
        """Check all slots for data consistency"""
        print_header("4. ALL SLOTS CONSISTENCY CHECK")
        
        print_info(f"Checking consistency across {len(slots_data)} slots...")
        
        issues_found = 0
        for i, slot in enumerate(slots_data):
            slot_issues = []
            
            # Check for None/empty values
            if slot.get('date') in [None, ""]:
                slot_issues.append("date is None/empty")
            if slot.get('start_time') in [None, ""]:
                slot_issues.append("start_time is None/empty")
            if slot.get('end_time') in [None, ""]:
                slot_issues.append("end_time is None/empty")
            
            if slot_issues:
                print_error(f"❌ Slot #{i+1} (ID: {slot.get('id', 'unknown')}) has issues: {', '.join(slot_issues)}")
                issues_found += 1
            else:
                print_success(f"✅ Slot #{i+1} data is valid")
        
        if issues_found == 0:
            print_success(f"All {len(slots_data)} slots have valid data structure")
            self.results['passed'] += 1
        else:
            print_error(f"❌ CRITICAL: {issues_found} slots have data issues")
            self.results['critical_issues'].append(f"{issues_found} slots have invalid data")
            self.results['failed'] += 1

    def create_test_slot(self):
        """Create a test slot to verify admin slot creation works properly"""
        print_header("5. ADMIN SLOT CREATION TEST")
        
        if not self.admin_token:
            print_error("Cannot create test slot - no admin token")
            return None
        
        # Create slot for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "15:30"
        }
        
        print_info(f"Creating test slot: {slot_data}")
        
        response = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            created_slot = response.json()
            print_success("Test slot created successfully")
            print_info("Created slot data:")
            print(json.dumps(created_slot, indent=2, default=str))
            
            # Validate the created slot immediately
            print_info("Validating newly created slot...")
            self.validate_slot_field_values(created_slot)
            
            return created_slot
        else:
            print_error(f"Failed to create test slot: {response.status_code if response else 'Connection failed'}")
            if response:
                print_error(f"Response: {response.text}")
            return None

    def test_frontend_compatibility(self, slots_data):
        """Test if slot data is compatible with frontend expectations"""
        print_header("6. FRONTEND COMPATIBILITY TEST")
        
        if not slots_data:
            print_error("No slots data for frontend compatibility test")
            self.results['failed'] += 1
            return
        
        print_info("Testing frontend compatibility for slot data...")
        
        # Simulate frontend processing
        for i, slot in enumerate(slots_data[:3]):  # Test first 3 slots
            print_info(f"\nTesting slot #{i+1} frontend processing:")
            
            # Simulate how frontend might access the data
            try:
                slot_date = slot.get('date')
                slot_start_time = slot.get('start_time')
                slot_end_time = slot.get('end_time')
                
                # Check if these would show as "Date non spécifiée"
                if slot_date and slot_date != "":
                    print_success(f"  Date would display: {slot_date}")
                else:
                    print_error(f"  ❌ Date would show 'Date non spécifiée' - value: {slot_date}")
                    self.results['critical_issues'].append("Frontend would show 'Date non spécifiée'")
                
                if slot_start_time and slot_start_time != "":
                    print_success(f"  Start time would display: {slot_start_time}")
                else:
                    print_error(f"  ❌ Start time would show 'Heure non spécifiée' - value: {slot_start_time}")
                    self.results['critical_issues'].append("Frontend would show 'Heure non spécifiée'")
                
                if slot_end_time and slot_end_time != "":
                    print_success(f"  End time would display: {slot_end_time}")
                else:
                    print_error(f"  ❌ End time would show 'Heure non spécifiée' - value: {slot_end_time}")
                    self.results['critical_issues'].append("Frontend would show 'Heure non spécifiée' for end_time")
                
            except Exception as e:
                print_error(f"  ❌ Error processing slot data: {str(e)}")
                self.results['failed'] += 1

    def run_slot_data_tests(self):
        """Run all slot data tests"""
        print_header("URGENT SLOT DATA TESTING - CLIENT DASHBOARD ISSUE")
        print_info("Problem: Client dashboard shows 'Date non spécifiée' and 'Heure non spécifiée'")
        print_info("Testing slot data structure from GET /api/slots?available_only=true")
        print_info(f"API Base URL: {BASE_URL}")
        
        # Authenticate admin first
        if not self.authenticate_admin():
            print_error("Cannot proceed without admin authentication")
            return False
        
        # Test the client dashboard endpoint
        slots_data = self.test_client_dashboard_slots_endpoint()
        
        if slots_data is not None:
            # Analyze slot data structure
            self.analyze_slot_data_structure(slots_data)
            
            # Test frontend compatibility
            self.test_frontend_compatibility(slots_data)
        
        # Print final results
        print_header("SLOT DATA TEST RESULTS")
        
        if self.results['critical_issues']:
            print_error("🚨 CRITICAL ISSUES FOUND:")
            for issue in self.results['critical_issues']:
                print_error(f"  • {issue}")
        
        print_info(f"Tests passed: {self.results['passed']}")
        print_info(f"Tests failed: {self.results['failed']}")
        
        if self.results['failed'] == 0 and not self.results['critical_issues']:
            print_success("🎉 NO SLOT DATA ISSUES FOUND - Problem may be in frontend processing")
            return True
        else:
            print_error("❌ SLOT DATA ISSUES DETECTED - This explains the client dashboard problem")
            return False

if __name__ == "__main__":
    tester = SlotDataTester()
    success = tester.run_slot_data_tests()
    sys.exit(0 if success else 1)