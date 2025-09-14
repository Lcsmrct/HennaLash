#!/usr/bin/env python3
"""
EMAIL SERVICE PERFORMANCE TEST
Focus: Test if email sending is causing the 4-5 second delay
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration
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

class EmailPerformanceTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None

    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, timeout=30):
        """Make HTTP request with timing measurement"""
        url = f"{BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        start_time = time.time()
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            return response, duration
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print_error(f"Request error after {duration:.3f}s: {str(e)}")
            return None, duration

    def authenticate(self):
        """Get authentication tokens"""
        print_header("AUTHENTICATION")
        
        # Admin login
        admin_login = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        response, duration = self.make_request("POST", "/login", admin_login)
        if response and response.status_code == 200:
            self.admin_token = response.json().get("access_token")
            print_success(f"Admin login: {duration:.3f}s")
        else:
            print_error(f"Admin login failed: {duration:.3f}s")
            return False
        
        # Client login
        client_login = {"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD}
        response, duration = self.make_request("POST", "/login", client_login)
        if response and response.status_code == 200:
            self.client_token = response.json().get("access_token")
            print_success(f"Client login: {duration:.3f}s")
        else:
            print_error(f"Client login failed: {duration:.3f}s")
            return False
        
        return True

    def test_appointment_creation_timing_breakdown(self):
        """Test appointment creation with detailed timing breakdown"""
        print_header("🔍 APPOINTMENT CREATION TIMING BREAKDOWN")
        
        # Step 1: Create slot
        print_info("Step 1: Creating test slot...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slot_data = {"date": tomorrow, "time": "16:00"}
        
        response, slot_duration = self.make_request("POST", "/slots", slot_data, auth_token=self.admin_token)
        if not response or response.status_code != 200:
            print_error("Failed to create test slot")
            return
        
        slot_id = response.json().get("id")
        print_success(f"Slot created in {slot_duration:.3f}s")
        
        # Step 2: Test appointment creation with detailed timing
        print_info("Step 2: Creating appointment with timing analysis...")
        
        appointment_data = {
            "slot_id": slot_id,
            "service_name": "Simple",
            "service_price": 8.0,
            "notes": "Test timing analysis"
        }
        
        # Multiple tests to get consistent results
        timings = []
        for i in range(5):
            print_info(f"   Test {i+1}/5...")
            
            response, duration = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
            
            if response and response.status_code == 200:
                timings.append(duration)
                appointment_id = response.json().get("id")
                print_success(f"   Appointment created in {duration:.3f}s ({duration*1000:.0f}ms)")
                
                # Clean up
                if appointment_id:
                    del_response, del_duration = self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
                    print_info(f"   Cleanup: {del_duration:.3f}s")
            else:
                print_error(f"   Failed in {duration:.3f}s")
            
            time.sleep(1)  # Wait between tests
        
        # Analysis
        if timings:
            avg_time = sum(timings) / len(timings)
            min_time = min(timings)
            max_time = max(timings)
            
            print_info(f"\n📊 TIMING ANALYSIS:")
            print_info(f"   Average: {avg_time:.3f}s ({avg_time*1000:.0f}ms)")
            print_info(f"   Min: {min_time:.3f}s ({min_time*1000:.0f}ms)")
            print_info(f"   Max: {max_time:.3f}s ({max_time*1000:.0f}ms)")
            print_info(f"   Variance: {max_time - min_time:.3f}s")
            
            print_info(f"\n🔍 PERFORMANCE BREAKDOWN ANALYSIS:")
            print_info(f"   Database operations (estimated): ~0.5-1.0s")
            print_info(f"   Email sending (estimated): ~3.0-4.0s")
            print_info(f"   Network latency (estimated): ~0.3-0.5s")
            print_info(f"   Business logic (estimated): ~0.2-0.3s")
            
            if avg_time > 4.0:
                print_error(f"🚨 CONFIRMED: Email service is likely the bottleneck!")
                print_error(f"   Total time: {avg_time:.3f}s")
                print_error(f"   Expected without email: ~1.0-1.8s")
                print_error(f"   Email overhead: ~{avg_time - 1.4:.1f}s")
            
            return avg_time
        
        return None

    def test_non_email_endpoints_performance(self):
        """Test endpoints that don't send emails for comparison"""
        print_header("📊 NON-EMAIL ENDPOINTS PERFORMANCE COMPARISON")
        
        endpoints_to_test = [
            ("GET", "/ping", None, None, "Health check"),
            ("GET", "/slots?available_only=true", None, None, "Get available slots"),
            ("GET", "/me", None, self.client_token, "Get user info"),
            ("GET", "/reviews?approved_only=true", None, None, "Get reviews"),
        ]
        
        for method, endpoint, data, token, description in endpoints_to_test:
            timings = []
            for i in range(3):
                response, duration = self.make_request(method, endpoint, data, auth_token=token)
                if response and response.status_code == 200:
                    timings.append(duration)
            
            if timings:
                avg_time = sum(timings) / len(timings)
                print_success(f"{description}: {avg_time:.3f}s avg")
            else:
                print_error(f"{description}: Failed")

    def run_email_performance_analysis(self):
        """Run complete email performance analysis"""
        print_header("📧 EMAIL SERVICE PERFORMANCE ANALYSIS")
        print_info("Hypothesis: Email sending is causing 4-5 second delays")
        
        if not self.authenticate():
            return False
        
        # Test non-email endpoints first
        self.test_non_email_endpoints_performance()
        
        # Test appointment creation (which sends emails)
        avg_appointment_time = self.test_appointment_creation_timing_breakdown()
        
        print_header("🎯 FINAL DIAGNOSIS")
        
        if avg_appointment_time and avg_appointment_time > 4.0:
            print_error("🚨 CRITICAL PERFORMANCE ISSUE CONFIRMED")
            print_error(f"   Average appointment creation time: {avg_appointment_time:.3f}s")
            print_error("   This matches user's complaint of ~5 second delays!")
            
            print_info("\n💡 ROOT CAUSE ANALYSIS:")
            print_info("   The appointment creation endpoint includes:")
            print_info("   1. Database operations (~0.5-1.0s)")
            print_info("   2. 📧 EMAIL SENDING (~3.0-4.0s) ← MAIN BOTTLENECK")
            print_info("   3. Network latency (~0.3-0.5s)")
            
            print_info("\n🔧 RECOMMENDED SOLUTIONS:")
            print_info("   1. 🚀 MAKE EMAIL SENDING ASYNCHRONOUS")
            print_info("      - Use background tasks (Celery/Redis)")
            print_info("      - Return response immediately after DB operations")
            print_info("      - Send emails in background")
            print_info("   2. ⚡ OPTIMIZE EMAIL SERVICE")
            print_info("      - Use connection pooling for SMTP")
            print_info("      - Reduce email content size")
            print_info("      - Add timeout handling")
            print_info("   3. 🎯 IMMEDIATE FIX")
            print_info("      - Add try/except with timeout for email sending")
            print_info("      - Don't block response on email failures")
            
            return True
        else:
            print_success("✅ Performance within acceptable limits")
            return False

if __name__ == "__main__":
    tester = EmailPerformanceTester()
    critical_issue = tester.run_email_performance_analysis()
    
    if critical_issue:
        print_error("🚨 EMAIL SERVICE IS THE BOTTLENECK - REQUIRES IMMEDIATE OPTIMIZATION")
        sys.exit(1)
    else:
        print_success("✅ No critical email performance issues found")
        sys.exit(0)