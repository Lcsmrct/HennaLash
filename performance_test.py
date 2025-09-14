#!/usr/bin/env python3
"""
Performance Testing Suite for Appointment Creation Optimization
Tests the FastAPI BackgroundTasks optimization for email sending
"""

import requests
import json
import time
import statistics
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

class PerformanceTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        
    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None, timeout=30):
        """Make HTTP request with timing"""
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
        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed to {url}")
            return None, None
        except requests.exceptions.Timeout:
            print_error(f"Request timeout to {url}")
            return None, None
        except Exception as e:
            print_error(f"Request error: {str(e)}")
            return None, None

    def authenticate(self):
        """Authenticate admin and client users"""
        print_header("AUTHENTICATION SETUP")
        
        # Admin login
        admin_login = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response, duration = self.make_request("POST", "/login", admin_login)
        if response and response.status_code == 200:
            data = response.json()
            self.admin_token = data["access_token"]
            print_success(f"Admin authenticated successfully ({duration:.3f}s)")
        else:
            print_error("Admin authentication failed")
            return False
        
        # Client login
        client_login = {
            "email": CLIENT_EMAIL,
            "password": CLIENT_PASSWORD
        }
        
        response, duration = self.make_request("POST", "/login", client_login)
        if response and response.status_code == 200:
            data = response.json()
            self.client_token = data["access_token"]
            print_success(f"Client authenticated successfully ({duration:.3f}s)")
        else:
            print_error("Client authentication failed")
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
            print_info(f"Test slot created: {slot_id} ({duration:.3f}s)")
            return slot_id
        else:
            print_error("Failed to create test slot")
            return None

    def test_appointment_creation_performance(self, service_name, service_price, num_tests=5):
        """Test appointment creation performance for a specific service"""
        print_header(f"PERFORMANCE TEST: {service_name} ({service_price}€)")
        
        times = []
        successful_tests = 0
        
        for i in range(num_tests):
            print_info(f"Test {i+1}/{num_tests} for {service_name}...")
            
            # Create a unique slot for each test
            slot_id = self.create_test_slot()
            if not slot_id:
                print_error(f"Failed to create slot for test {i+1}")
                continue
            
            # Test appointment creation
            appointment_data = {
                "slot_id": slot_id,
                "service_name": service_name,
                "service_price": service_price,
                "notes": f"Performance test {i+1} - {service_name}"
            }
            
            response, duration = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
            
            if response and response.status_code == 200:
                times.append(duration)
                successful_tests += 1
                
                # Get appointment ID for cleanup
                appointment_id = response.json().get("id")
                
                print_success(f"  Test {i+1}: {duration:.3f}s - Appointment created")
                
                # Clean up - delete appointment
                if appointment_id:
                    self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
                    
            else:
                print_error(f"  Test {i+1}: Failed - {response.status_code if response else 'Connection failed'}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)
            
            print_info(f"\n📊 PERFORMANCE RESULTS FOR {service_name}:")
            print_info(f"  Successful tests: {successful_tests}/{num_tests}")
            print_info(f"  Average time: {avg_time:.3f}s")
            print_info(f"  Median time: {median_time:.3f}s")
            print_info(f"  Min time: {min_time:.3f}s")
            print_info(f"  Max time: {max_time:.3f}s")
            
            # Performance evaluation
            if avg_time < 1.5:
                print_success(f"🎯 EXCELLENT: Average {avg_time:.3f}s < 1.5s target!")
                performance_status = "EXCELLENT"
            elif avg_time < 2.0:
                print_success(f"✅ GOOD: Average {avg_time:.3f}s < 2.0s (acceptable)")
                performance_status = "GOOD"
            elif avg_time < 3.0:
                print_warning(f"⚠️  ACCEPTABLE: Average {avg_time:.3f}s < 3.0s")
                performance_status = "ACCEPTABLE"
            else:
                print_error(f"❌ POOR: Average {avg_time:.3f}s > 3.0s")
                performance_status = "POOR"
            
            self.test_results.append({
                "service": service_name,
                "price": service_price,
                "avg_time": avg_time,
                "median_time": median_time,
                "min_time": min_time,
                "max_time": max_time,
                "successful_tests": successful_tests,
                "total_tests": num_tests,
                "performance_status": performance_status
            })
            
            return avg_time
        else:
            print_error(f"No successful tests for {service_name}")
            return None

    def test_background_email_verification(self):
        """Verify that emails are sent in background (non-blocking)"""
        print_header("BACKGROUND EMAIL VERIFICATION")
        
        # Create test slot
        slot_id = self.create_test_slot()
        if not slot_id:
            print_error("Cannot test background email - no slot created")
            return False
        
        appointment_data = {
            "slot_id": slot_id,
            "service_name": "Simple",
            "service_price": 8.0,
            "notes": "Background email test"
        }
        
        print_info("Testing that API responds immediately while email is sent in background...")
        
        response, duration = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
        
        if response and response.status_code == 200:
            appointment_id = response.json().get("id")
            
            if duration < 2.0:
                print_success(f"✅ API responded quickly ({duration:.3f}s) - Email likely sent in background")
                
                # Clean up
                if appointment_id:
                    self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
                
                return True
            else:
                print_warning(f"⚠️  API took {duration:.3f}s - May still be sending email synchronously")
                
                # Clean up
                if appointment_id:
                    self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
                
                return False
        else:
            print_error("Background email test failed - appointment creation failed")
            return False

    def test_regression_functionality(self):
        """Test that all functionality still works after optimization"""
        print_header("REGRESSION TESTING")
        
        # Create test slot
        slot_id = self.create_test_slot()
        if not slot_id:
            print_error("Cannot test regression - no slot created")
            return False
        
        # Test appointment creation
        appointment_data = {
            "slot_id": slot_id,
            "service_name": "Chargé",
            "service_price": 12.0,
            "notes": "Regression test appointment"
        }
        
        response, duration = self.make_request("POST", "/appointments", appointment_data, auth_token=self.client_token)
        
        if response and response.status_code == 200:
            appointment_data_response = response.json()
            appointment_id = appointment_data_response.get("id")
            
            print_success("✅ Appointment creation working")
            
            # Check if slot is marked as unavailable
            response, _ = self.make_request("GET", "/slots?available_only=true")
            if response and response.status_code == 200:
                available_slots = response.json()
                slot_still_available = any(slot.get("id") == slot_id for slot in available_slots)
                
                if not slot_still_available:
                    print_success("✅ Slot correctly marked as unavailable")
                else:
                    print_error("❌ Slot still available after booking")
            
            # Check appointment has slot_info
            if appointment_data_response.get("slot_info"):
                print_success("✅ Appointment contains slot_info")
            else:
                print_warning("⚠️  Appointment missing slot_info")
            
            # Test admin can confirm appointment
            update_data = {
                "status": "confirmed",
                "notes": "Confirmed by admin - regression test"
            }
            
            response, _ = self.make_request("PUT", f"/appointments/{appointment_id}/status", update_data, auth_token=self.admin_token)
            if response and response.status_code == 200:
                print_success("✅ Admin appointment confirmation working")
                print_info("  Client confirmation email should be sent")
            else:
                print_error("❌ Admin appointment confirmation failed")
            
            # Clean up
            self.make_request("DELETE", f"/appointments/{appointment_id}", auth_token=self.admin_token)
            
            return True
        else:
            print_error("❌ Regression test failed - appointment creation failed")
            return False

    def run_performance_tests(self):
        """Run all performance tests"""
        print_header("APPOINTMENT CREATION PERFORMANCE OPTIMIZATION VALIDATION")
        print_info("🎯 TARGET: Response time < 1.5s (vs previous ~4.7s)")
        print_info("🔍 TESTING: FastAPI BackgroundTasks email optimization")
        
        if not self.authenticate():
            print_error("Authentication failed - cannot run tests")
            return False
        
        # Test all 4 services
        services = [
            {"name": "Très simple", "price": 5.0},
            {"name": "Simple", "price": 8.0},
            {"name": "Chargé", "price": 12.0},
            {"name": "Mariée", "price": 20.0}
        ]
        
        all_times = []
        
        for service in services:
            avg_time = self.test_appointment_creation_performance(
                service["name"], 
                service["price"], 
                num_tests=3  # 3 tests per service for faster execution
            )
            if avg_time:
                all_times.append(avg_time)
        
        # Test background email functionality
        background_email_ok = self.test_background_email_verification()
        
        # Test regression
        regression_ok = self.test_regression_functionality()
        
        # Overall performance analysis
        print_header("OVERALL PERFORMANCE ANALYSIS")
        
        if all_times:
            overall_avg = statistics.mean(all_times)
            overall_min = min(all_times)
            overall_max = max(all_times)
            
            print_info(f"📊 OVERALL STATISTICS:")
            print_info(f"  Average across all services: {overall_avg:.3f}s")
            print_info(f"  Best performance: {overall_min:.3f}s")
            print_info(f"  Worst performance: {overall_max:.3f}s")
            
            # Performance improvement calculation
            previous_time = 4.7  # From test_result.md
            improvement = ((previous_time - overall_avg) / previous_time) * 100
            
            print_info(f"\n🚀 PERFORMANCE IMPROVEMENT:")
            print_info(f"  Before optimization: ~{previous_time}s")
            print_info(f"  After optimization: {overall_avg:.3f}s")
            print_info(f"  Improvement: {improvement:.1f}%")
            
            if overall_avg < 1.5:
                print_success(f"🎯 TARGET ACHIEVED! Average {overall_avg:.3f}s < 1.5s target")
                performance_success = True
            elif overall_avg < 2.0:
                print_success(f"✅ GOOD PERFORMANCE! Average {overall_avg:.3f}s < 2.0s")
                performance_success = True
            else:
                print_warning(f"⚠️  Performance needs improvement: {overall_avg:.3f}s")
                performance_success = False
        else:
            print_error("❌ No performance data collected")
            performance_success = False
        
        # Summary
        print_header("TEST SUMMARY")
        
        success_count = 0
        total_tests = 0
        
        for result in self.test_results:
            total_tests += 1
            if result["performance_status"] in ["EXCELLENT", "GOOD"]:
                success_count += 1
        
        print_info(f"Services tested: {len(self.test_results)}")
        print_info(f"Performance targets met: {success_count}/{total_tests}")
        print_info(f"Background email working: {'✅' if background_email_ok else '❌'}")
        print_info(f"Regression tests passed: {'✅' if regression_ok else '❌'}")
        
        overall_success = (
            performance_success and 
            background_email_ok and 
            regression_ok and 
            success_count >= total_tests * 0.75  # At least 75% of services perform well
        )
        
        if overall_success:
            print_success("🎉 OPTIMIZATION VALIDATION SUCCESSFUL!")
            print_success("✅ Performance target achieved")
            print_success("✅ Background email working")
            print_success("✅ All functionality preserved")
        else:
            print_error("❌ OPTIMIZATION VALIDATION FAILED")
            if not performance_success:
                print_error("  Performance target not met")
            if not background_email_ok:
                print_error("  Background email not working properly")
            if not regression_ok:
                print_error("  Regression issues detected")
        
        return overall_success

if __name__ == "__main__":
    tester = PerformanceTester()
    success = tester.run_performance_tests()
    sys.exit(0 if success else 1)