#!/usr/bin/env python3
"""
Complete Flow Test - Test the exact flow from frontend perspective
This test simulates the complete user experience to identify the issue
"""

import requests
import json
from datetime import datetime
import sys

# Configuration - Use the exact same URL as frontend
BASE_URL = "https://henna-lash.onrender.com/api"
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

class CompleteFlowTester:
    def __init__(self):
        self.client_token = None
        self.results = {'passed': 0, 'failed': 0, 'critical_issues': []}

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request exactly like frontend does"""
        url = f"{BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)  # Same timeout as frontend
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed to {url}")
            return None
        except requests.exceptions.Timeout:
            print_error(f"Request timeout to {url} (30s)")
            return None
        except Exception as e:
            print_error(f"Request error: {str(e)}")
            return None

    def simulate_client_login(self):
        """Simulate client login exactly like frontend"""
        print_header("1. CLIENT LOGIN SIMULATION")
        print_info("Simulating client login flow...")
        
        login_data = {
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        }
        
        response = self.make_request("POST", "/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.client_token = data["access_token"]
                print_success("✅ Client login successful - token obtained")
                self.results['passed'] += 1
                return True
            else:
                print_error("❌ Client login - No token in response")
                self.results['failed'] += 1
                return False
        else:
            print_error(f"❌ Client login failed: {response.status_code if response else 'Connection failed'}")
            if response:
                print_error(f"Response: {response.text}")
            self.results['failed'] += 1
            return False

    def simulate_dashboard_data_fetch(self):
        """Simulate the exact getDashboardData call from frontend"""
        print_header("2. DASHBOARD DATA FETCH SIMULATION")
        print_info("Simulating apiService.getDashboardData('client') call...")
        
        if not self.client_token:
            print_error("❌ Cannot fetch dashboard data - no client token")
            self.results['failed'] += 1
            return None
        
        try:
            # Simulate the Promise.all call from apiService.getDashboardData
            print_info("Making parallel requests like frontend does:")
            print_info("1. GET /api/appointments")
            print_info("2. GET /api/slots?available_only=true")
            
            # Make appointments request
            appointments_response = self.make_request("GET", "/appointments", auth_token=self.client_token)
            if not appointments_response or appointments_response.status_code != 200:
                print_error("❌ Appointments request failed")
                self.results['failed'] += 1
                return None
            
            appointments_data = appointments_response.json()
            print_success(f"✅ Appointments fetched: {len(appointments_data)} appointments")
            
            # Make slots request
            slots_response = self.make_request("GET", "/slots?available_only=true")
            if not slots_response or slots_response.status_code != 200:
                print_error("❌ Slots request failed")
                self.results['failed'] += 1
                return None
            
            slots_data = slots_response.json()
            print_success(f"✅ Available slots fetched: {len(slots_data)} slots")
            
            # Combine data like frontend does
            dashboard_data = {
                'appointments': appointments_data,
                'slots': slots_data
            }
            
            print_success("✅ Dashboard data combined successfully")
            self.results['passed'] += 1
            return dashboard_data
            
        except Exception as e:
            print_error(f"❌ Error in dashboard data fetch: {str(e)}")
            self.results['failed'] += 1
            return None

    def analyze_slot_rendering(self, dashboard_data):
        """Analyze how slots would be rendered in the frontend"""
        print_header("3. SLOT RENDERING ANALYSIS")
        
        if not dashboard_data or 'slots' not in dashboard_data:
            print_error("❌ No slots data to analyze")
            self.results['failed'] += 1
            return
        
        slots = dashboard_data['slots']
        print_info(f"Analyzing rendering of {len(slots)} slots...")
        
        if len(slots) == 0:
            print_warning("⚠️  No available slots - this could be why user sees no data")
            return
        
        # Analyze first few slots in detail
        for i, slot in enumerate(slots[:3]):
            print_info(f"\n--- SLOT #{i+1} RENDERING SIMULATION ---")
            print_info(f"Raw slot data: {json.dumps(slot, indent=2)}")
            
            # Simulate the exact frontend rendering logic from ClientDashboard.jsx
            print_info("Simulating frontend rendering:")
            
            # Line 250: {slot.date ? formatDate(slot.date) : 'Date non spécifiée'}
            slot_date = slot.get('date')
            if slot_date:
                print_success(f"✅ Date field present: {slot_date}")
                # Simulate formatDate function
                try:
                    # JavaScript: new Date(dateString).toLocaleDateString('fr-FR', {...})
                    js_date = datetime.fromisoformat(slot_date.replace('T00:00:00', ''))
                    formatted = js_date.strftime('%A %d %B %Y')
                    print_success(f"✅ Would display: {formatted}")
                except Exception as e:
                    print_error(f"❌ formatDate would fail: {str(e)}")
                    self.results['critical_issues'].append(f"formatDate fails for: {slot_date}")
            else:
                print_error("❌ Date field missing/empty - would show 'Date non spécifiée'")
                self.results['critical_issues'].append("Date field missing in slot data")
            
            # Line 254: {slot.start_time ? formatTime(slot.start_time) : 'Heure non spécifiée'}
            slot_start_time = slot.get('start_time')
            if slot_start_time:
                print_success(f"✅ Start time field present: {slot_start_time}")
                # Simulate formatTime function
                try:
                    # JavaScript: new Date(`2000-01-01T${timeString}`).toLocaleTimeString('fr-FR', {...})
                    print_success(f"✅ Would display: {slot_start_time}")
                except Exception as e:
                    print_error(f"❌ formatTime would fail: {str(e)}")
                    self.results['critical_issues'].append(f"formatTime fails for: {slot_start_time}")
            else:
                print_error("❌ Start time field missing/empty - would show 'Heure non spécifiée'")
                self.results['critical_issues'].append("Start time field missing in slot data")

    def test_browser_compatibility(self, dashboard_data):
        """Test if the data would work in different browser scenarios"""
        print_header("4. BROWSER COMPATIBILITY TEST")
        
        if not dashboard_data or 'slots' not in dashboard_data:
            print_error("❌ No slots data for browser compatibility test")
            return
        
        slots = dashboard_data['slots']
        if len(slots) == 0:
            print_warning("⚠️  No slots for browser compatibility test")
            return
        
        first_slot = slots[0]
        print_info("Testing browser compatibility scenarios...")
        
        # Test 1: JSON parsing (already done by requests)
        print_success("✅ JSON parsing works (Python equivalent)")
        
        # Test 2: Date parsing
        slot_date = first_slot.get('date')
        if slot_date:
            try:
                # Test different date parsing scenarios
                print_info(f"Testing date parsing for: {slot_date}")
                
                # Scenario 1: Direct Date() constructor
                from datetime import datetime
                parsed_date = datetime.fromisoformat(slot_date.replace('T00:00:00', ''))
                print_success(f"✅ Date parsing works: {parsed_date}")
                
                # Scenario 2: Check for timezone issues
                if 'T' in slot_date and slot_date.endswith('T00:00:00'):
                    print_info("✅ Date is in ISO format without timezone (good)")
                else:
                    print_warning(f"⚠️  Date format might cause timezone issues: {slot_date}")
                
            except Exception as e:
                print_error(f"❌ Date parsing would fail in browser: {str(e)}")
                self.results['critical_issues'].append(f"Date parsing issue: {str(e)}")
        
        # Test 3: Time parsing
        slot_time = first_slot.get('start_time')
        if slot_time:
            try:
                print_info(f"Testing time parsing for: {slot_time}")
                # Simulate: new Date(`2000-01-01T${timeString}`)
                test_datetime_str = f"2000-01-01T{slot_time}:00"
                parsed_time = datetime.fromisoformat(test_datetime_str)
                print_success(f"✅ Time parsing works: {parsed_time.strftime('%H:%M')}")
            except Exception as e:
                print_error(f"❌ Time parsing would fail in browser: {str(e)}")
                self.results['critical_issues'].append(f"Time parsing issue: {str(e)}")

    def run_complete_flow_test(self):
        """Run the complete flow test"""
        print_header("COMPLETE FLOW TEST - CLIENT DASHBOARD SLOT ISSUE")
        print_info("Testing the complete user flow to identify slot data issues")
        print_info(f"Backend URL: {BASE_URL}")
        print_info(f"Client credentials: {CLIENT_EMAIL}")
        
        # Step 1: Login
        if not self.simulate_client_login():
            print_error("❌ Cannot proceed without client login")
            return False
        
        # Step 2: Fetch dashboard data
        dashboard_data = self.simulate_dashboard_data_fetch()
        if not dashboard_data:
            print_error("❌ Cannot proceed without dashboard data")
            return False
        
        # Step 3: Analyze slot rendering
        self.analyze_slot_rendering(dashboard_data)
        
        # Step 4: Test browser compatibility
        self.test_browser_compatibility(dashboard_data)
        
        # Print results
        print_header("COMPLETE FLOW TEST RESULTS")
        
        if self.results['critical_issues']:
            print_error("🚨 CRITICAL ISSUES FOUND:")
            for issue in self.results['critical_issues']:
                print_error(f"  • {issue}")
        
        print_info(f"Tests passed: {self.results['passed']}")
        print_info(f"Tests failed: {self.results['failed']}")
        
        if self.results['failed'] == 0 and not self.results['critical_issues']:
            print_success("🎉 NO ISSUES FOUND - Backend data is correct")
            print_info("The problem might be:")
            print_info("1. Frontend caching issues")
            print_info("2. Browser-specific JavaScript issues")
            print_info("3. Network connectivity problems")
            print_info("4. Frontend environment configuration")
            return True
        else:
            print_error("❌ ISSUES DETECTED - This explains the client dashboard problem")
            return False

if __name__ == "__main__":
    tester = CompleteFlowTester()
    success = tester.run_complete_flow_test()
    sys.exit(0 if success else 1)