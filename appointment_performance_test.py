#!/usr/bin/env python3
"""
URGENT PERFORMANCE DIAGNOSTIC - Appointment Creation Timing Test
Focus: Measure precise timing of POST /api/appointments endpoint
Problem: User reports 5-second delay for appointment confirmation
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration - Use external URL as per frontend .env
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

class AppointmentPerformanceTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, timeout=30):
        """Make HTTP request with timing measurement"""
        url = f"{BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            return response, duration
        except requests.exceptions.ConnectionError as e:
            end_time = time.time()
            duration = end_time - start_time
            print_error(f"Connection failed to {url} after {duration:.3f}s: {str(e)}")
            return None, duration
        except requests.exceptions.Timeout as e:
            end_time = time.time()
            duration = end_time - start_time
            print_error(f"Request timeout to {url} after {duration:.3f}s")
            return None, duration
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print_error(f"Request error after {duration:.3f}s: {str(e)}")
            return None, duration

    def authenticate(self):
        """Get authentication tokens"""
        print_header("AUTHENTICATION SETUP")
        
        # Test admin login
        admin_login = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response, duration = self.make_request("POST", "/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("access_token")
            print_success(f"Admin login successful in {duration:.3f}s")
        else:
            print_error(f"Admin login failed in {duration:.3f}s")
            return False
        
        # Test client login
        client_login = {
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        }
        
        response, duration = self.make_request("POST", "/login", client_login)
        if response and response.status_code == 200:
            data = response.json()
            self.client_token = data.get("access_token")
            print_success(f"Client login successful in {duration:.3f}s")
        else:
            print_error(f"Client login failed in {duration:.3f}s")
            return False
        
        return True

    def create_test_slot(self):
        """Create a test slot for appointment booking"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {
            "date": tomorrow,
            "time": "15:30"
        }
        
        response, duration = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if response and response.status_code == 200:
            slot_id = response.json().get("id")
            print_success(f"Test slot created in {duration:.3f}s - ID: {slot_id}")
            return slot_id
        else:
            print_error(f"Failed to create test slot in {duration:.3f}s")
            return None

    def test_appointment_creation_performance(self):
        """Test appointment creation with precise timing for different services"""
        print_header("🎯 APPOINTMENT CREATION PERFORMANCE TEST")
        
        services = [
            {"name": "Simple", "price": 8.0},
            {"name": "Chargé", "price": 12.0},
            {"name": "Très simple", "price": 5.0},
            {"name": "Mariée", "price": 20.0}
        ]
        
        for service in services:
            print(f"\n🔍 Testing service: {service['name']} ({service['price']}€)")
            
            # Create slot for this test
            slot_id = self.create_test_slot()
            if not slot_id:
                continue
            
            # Prepare appointment data
            appointment_data = {
                "slot_id": slot_id,
                "service_name": service["name"],
                "service_price": service["price"],
                "notes": f"Test performance pour service {service['name']}"
            }
            
            # Measure appointment creation timing
            print_info("⏱️  Starting appointment creation timing...")
            
            # Multiple measurements for accuracy
            timings = []
            for i in range(3):
                print_info(f"   Attempt {i+1}/3...")
                
                response, duration = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
                
                if response and response.status_code == 200:
                    timings.append(duration)
                    data = response.json()
                    appointment_id = data.get("id")
                    
                    print_success(f"   ✅ Appointment created in {duration:.3f}s ({duration*1000:.0f}ms)")
                    
                    # Clean up - delete appointment
                    if appointment_id:
                        del_response, del_duration = self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
                        print_info(f"   🗑️  Cleanup completed in {del_duration:.3f}s")
                else:
                    print_error(f"   ❌ Appointment creation failed in {duration:.3f}s")
                    if response:
                        print_error(f"      Status: {response.status_code}, Response: {response.text}")
                
                # Small delay between attempts
                time.sleep(0.5)
            
            # Calculate statistics
            if timings:
                avg_time = sum(timings) / len(timings)
                min_time = min(timings)
                max_time = max(timings)
                
                result = {
                    "service": service["name"],
                    "price": service["price"],
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "attempts": len(timings)
                }
                self.test_results.append(result)
                
                print_info(f"📊 Statistics for {service['name']}:")
                print_info(f"   Average: {avg_time:.3f}s ({avg_time*1000:.0f}ms)")
                print_info(f"   Min: {min_time:.3f}s ({min_time*1000:.0f}ms)")
                print_info(f"   Max: {max_time:.3f}s ({max_time*1000:.0f}ms)")
                
                # Performance analysis
                if avg_time > 5.0:
                    print_error(f"🚨 CRITICAL: Average time {avg_time:.3f}s > 5s - MATCHES USER COMPLAINT!")
                elif avg_time > 2.0:
                    print_warning(f"⚠️  SLOW: Average time {avg_time:.3f}s > 2s - Needs optimization")
                else:
                    print_success(f"✅ GOOD: Average time {avg_time:.3f}s < 2s")

    def test_individual_components(self):
        """Test individual components to identify bottlenecks"""
        print_header("🔍 COMPONENT-LEVEL PERFORMANCE ANALYSIS")
        
        # Test 1: Database query performance (get available slots)
        print_info("1. Testing database query performance...")
        response, duration = self.make_request("GET", "/slots?available_only=true")
        if response and response.status_code == 200:
            slots = response.json()
            print_success(f"   Database query: {duration:.3f}s ({len(slots)} slots)")
        else:
            print_error(f"   Database query failed: {duration:.3f}s")
        
        # Test 2: Authentication overhead
        print_info("2. Testing authentication overhead...")
        response, duration = self.make_request("GET", "/me", auth_token=self.client_token)
        if response and response.status_code == 200:
            print_success(f"   Authentication check: {duration:.3f}s")
        else:
            print_error(f"   Authentication check failed: {duration:.3f}s")
        
        # Test 3: Simple endpoint without business logic
        print_info("3. Testing simple endpoint (ping)...")
        response, duration = self.make_request("GET", "/ping")
        if response and response.status_code == 200:
            print_success(f"   Simple endpoint: {duration:.3f}s")
        else:
            print_error(f"   Simple endpoint failed: {duration:.3f}s")

    def analyze_potential_causes(self):
        """Analyze potential causes of slowness"""
        print_header("🔬 POTENTIAL SLOWNESS CAUSES ANALYSIS")
        
        print_info("Analyzing potential causes of 5-second delay:")
        print_info("1. 📧 EMAIL SERVICE: Appointment creation sends admin notification email")
        print_info("   - Gmail SMTP connection and sending could add 2-4 seconds")
        print_info("   - Email service runs synchronously in appointment creation")
        
        print_info("2. 🗄️  DATABASE OPERATIONS:")
        print_info("   - MongoDB aggregation pipeline for appointment response")
        print_info("   - Multiple database lookups (users, time_slots)")
        print_info("   - Slot availability update")
        
        print_info("3. 🌐 NETWORK LATENCY:")
        print_info("   - External URL: https://henna-lash.onrender.com")
        print_info("   - Cloud hosting latency")
        print_info("   - CORS preflight requests")
        
        print_info("4. 🔄 BUSINESS LOGIC:")
        print_info("   - Slot availability verification")
        print_info("   - User authentication and authorization")
        print_info("   - Appointment data aggregation with user/slot info")

    def generate_performance_report(self):
        """Generate detailed performance report"""
        print_header("📋 PERFORMANCE DIAGNOSTIC REPORT")
        
        if not self.test_results:
            print_error("No test results available")
            return
        
        print_info("🎯 APPOINTMENT CREATION PERFORMANCE SUMMARY:")
        print_info("-" * 60)
        
        total_avg = 0
        critical_services = []
        slow_services = []
        good_services = []
        
        for result in self.test_results:
            service = result["service"]
            avg_time = result["avg_time"]
            min_time = result["min_time"]
            max_time = result["max_time"]
            
            print_info(f"Service: {service} ({result['price']}€)")
            print_info(f"  Average: {avg_time:.3f}s ({avg_time*1000:.0f}ms)")
            print_info(f"  Range: {min_time:.3f}s - {max_time:.3f}s")
            
            total_avg += avg_time
            
            if avg_time > 5.0:
                critical_services.append(service)
                print_error(f"  🚨 CRITICAL: > 5s")
            elif avg_time > 2.0:
                slow_services.append(service)
                print_warning(f"  ⚠️  SLOW: > 2s")
            else:
                good_services.append(service)
                print_success(f"  ✅ GOOD: < 2s")
            
            print_info("")
        
        overall_avg = total_avg / len(self.test_results)
        print_info(f"📊 OVERALL AVERAGE: {overall_avg:.3f}s ({overall_avg*1000:.0f}ms)")
        
        print_info("\n🎯 DIAGNOSIS:")
        if critical_services:
            print_error(f"🚨 CRITICAL ISSUE CONFIRMED: {len(critical_services)} services > 5s")
            print_error(f"   Services affected: {', '.join(critical_services)}")
            print_error("   This matches the user's complaint of 5-second delays!")
        elif slow_services:
            print_warning(f"⚠️  PERFORMANCE ISSUE: {len(slow_services)} services > 2s")
            print_warning(f"   Services affected: {', '.join(slow_services)}")
        else:
            print_success("✅ All services performing well (< 2s)")
        
        print_info("\n💡 RECOMMENDED OPTIMIZATIONS:")
        if overall_avg > 2.0:
            print_info("1. 📧 Make email sending ASYNCHRONOUS (background task)")
            print_info("2. 🗄️  Optimize MongoDB aggregation pipeline")
            print_info("3. 🔄 Add response caching for user/slot lookups")
            print_info("4. ⚡ Consider database connection pooling")
            print_info("5. 🌐 Investigate hosting performance (Render.com)")

    def run_performance_diagnostic(self):
        """Run complete performance diagnostic"""
        print_header("🚨 URGENT APPOINTMENT CREATION PERFORMANCE DIAGNOSTIC")
        print_info("Problem: User reports 5-second delay for appointment confirmation")
        print_info(f"Testing against: {BASE_URL}")
        
        start_time = time.time()
        
        # Step 1: Authentication
        if not self.authenticate():
            print_error("Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Component-level testing
        self.test_individual_components()
        
        # Step 3: Appointment creation performance testing
        self.test_appointment_creation_performance()
        
        # Step 4: Analysis
        self.analyze_potential_causes()
        
        # Step 5: Generate report
        self.generate_performance_report()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        print_header("🏁 DIAGNOSTIC COMPLETE")
        print_info(f"Total diagnostic time: {total_duration:.2f} seconds")
        
        # Return True if critical performance issues found
        if self.test_results:
            overall_avg = sum(r["avg_time"] for r in self.test_results) / len(self.test_results)
            return overall_avg > 5.0  # True if critical issue confirmed
        
        return False

if __name__ == "__main__":
    tester = AppointmentPerformanceTester()
    critical_issue_found = tester.run_performance_diagnostic()
    
    if critical_issue_found:
        print_error("🚨 CRITICAL PERFORMANCE ISSUE CONFIRMED - REQUIRES IMMEDIATE OPTIMIZATION")
        sys.exit(1)
    else:
        print_success("✅ Performance within acceptable limits")
        sys.exit(0)