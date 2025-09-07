#!/usr/bin/env python3
"""
CORS Testing Suite - Focused on OPTIONS preflight requests
Tests the specific CORS issue reported: "OPTIONS /api/login HTTP/1.1" 400 Bad Request
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://henna-lash.onrender.com/api"

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

class CORSTester:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }

    def test_options_preflight(self, endpoint, origin, methods=None, headers=None):
        """Test OPTIONS preflight request for specific endpoint"""
        url = f"{BASE_URL}{endpoint}"
        
        # Default headers for preflight
        preflight_headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        if methods:
            preflight_headers["Access-Control-Request-Method"] = methods
        if headers:
            preflight_headers["Access-Control-Request-Headers"] = headers
        
        try:
            print_info(f"Testing OPTIONS {endpoint} from origin: {origin}")
            start_time = time.time()
            response = requests.options(url, headers=preflight_headers, timeout=10)
            end_time = time.time()
            
            print_info(f"Response time: {(end_time - start_time):.3f}s")
            print_info(f"Status code: {response.status_code}")
            
            # Check status code
            if response.status_code == 400:
                print_error(f"❌ CRITICAL: OPTIONS {endpoint} returned 400 Bad Request")
                print_error("This is the exact error reported by the user!")
                self.results['failed'] += 1
                return False
            elif response.status_code in [200, 204]:
                print_success(f"✅ OPTIONS {endpoint} successful - Status: {response.status_code}")
            else:
                print_warning(f"⚠️  OPTIONS {endpoint} unexpected status: {response.status_code}")
                self.results['warnings'] += 1
            
            # Check CORS headers
            cors_headers = response.headers
            print_info("CORS Response Headers:")
            
            required_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods", 
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Credentials"
            ]
            
            all_headers_present = True
            for header in required_headers:
                value = cors_headers.get(header, "NOT SET")
                print_info(f"  {header}: {value}")
                if value == "NOT SET":
                    all_headers_present = False
            
            # Specific checks
            allow_origin = cors_headers.get("Access-Control-Allow-Origin")
            allow_credentials = cors_headers.get("Access-Control-Allow-Credentials")
            allow_methods = cors_headers.get("Access-Control-Allow-Methods", "")
            
            if allow_origin and (allow_origin == origin or allow_origin == "*"):
                print_success(f"✅ Origin {origin} is allowed")
            else:
                print_error(f"❌ Origin {origin} not properly allowed. Got: {allow_origin}")
                self.results['failed'] += 1
                return False
            
            if allow_credentials and allow_credentials.lower() == "true":
                print_success("✅ Credentials allowed")
            else:
                print_warning(f"⚠️  Credentials not allowed: {allow_credentials}")
            
            if "POST" in allow_methods.upper():
                print_success("✅ POST method allowed")
            else:
                print_error(f"❌ POST method not allowed. Methods: {allow_methods}")
                self.results['failed'] += 1
                return False
            
            if all_headers_present:
                print_success("✅ All required CORS headers present")
                self.results['passed'] += 1
                return True
            else:
                print_error("❌ Missing required CORS headers")
                self.results['failed'] += 1
                return False
                
        except requests.exceptions.ConnectionError:
            print_error(f"❌ Connection failed to {url}")
            self.results['failed'] += 1
            return False
        except requests.exceptions.Timeout:
            print_error(f"❌ Request timeout to {url}")
            self.results['failed'] += 1
            return False
        except Exception as e:
            print_error(f"❌ Request error: {str(e)}")
            self.results['failed'] += 1
            return False

    def test_actual_login_after_preflight(self, origin):
        """Test actual login request after successful preflight"""
        print_header("TESTING ACTUAL LOGIN AFTER PREFLIGHT")
        
        # First do preflight
        preflight_success = self.test_options_preflight("/login", origin)
        
        if not preflight_success:
            print_error("❌ Skipping actual login test - preflight failed")
            return False
        
        # Now test actual login
        url = f"{BASE_URL}/login"
        headers = {
            "Content-Type": "application/json",
            "Origin": origin
        }
        
        login_data = {
            "email": "admin@salon.com",
            "password": "testadmin123"
        }
        
        try:
            print_info(f"Testing POST /login from origin: {origin}")
            start_time = time.time()
            response = requests.post(url, json=login_data, headers=headers, timeout=10)
            end_time = time.time()
            
            print_info(f"Response time: {(end_time - start_time):.3f}s")
            print_info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print_success("✅ Login successful after preflight - token received")
                    self.results['passed'] += 1
                    return True
                else:
                    print_error("❌ Login response missing token")
                    self.results['failed'] += 1
                    return False
            elif response.status_code == 401:
                print_info("ℹ️  Login failed with 401 (expected if credentials wrong)")
                print_success("✅ But CORS is working - no 400 Bad Request on OPTIONS")
                self.results['passed'] += 1
                return True
            else:
                print_error(f"❌ Login failed with status: {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results['failed'] += 1
                return False
                
        except Exception as e:
            print_error(f"❌ Login request error: {str(e)}")
            self.results['failed'] += 1
            return False

    def run_comprehensive_cors_tests(self):
        """Run comprehensive CORS tests"""
        print_header("COMPREHENSIVE CORS TESTING SUITE")
        print_info(f"Testing against: {BASE_URL}")
        print_info("Focus: OPTIONS preflight requests that were causing 400 Bad Request")
        
        start_time = time.time()
        
        # Test different origins
        origins_to_test = [
            "https://henna-lash.onrender.com",
            "https://henna-lash-frontend.onrender.com", 
            "http://localhost:3000",
            "https://example.com"  # Should be rejected
        ]
        
        # Test critical endpoints that need CORS
        endpoints_to_test = [
            "/login",
            "/register", 
            "/appointments",
            "/reviews",
            "/slots",
            "/ping"
        ]
        
        print_header("1. TESTING OPTIONS PREFLIGHT FOR CRITICAL ENDPOINTS")
        
        for endpoint in endpoints_to_test:
            print_header(f"Testing {endpoint}")
            
            for origin in origins_to_test:
                if origin == "https://example.com":
                    print_info(f"Testing unauthorized origin: {origin}")
                
                success = self.test_options_preflight(endpoint, origin)
                
                if endpoint == "/login" and origin in ["https://henna-lash.onrender.com", "https://henna-lash-frontend.onrender.com"]:
                    # For login endpoint with authorized origins, also test actual request
                    if success:
                        self.test_actual_login_after_preflight(origin)
                
                print()  # Add spacing
        
        # Test specific CORS scenarios
        print_header("2. TESTING SPECIFIC CORS SCENARIOS")
        
        # Test with different request methods
        print_info("Testing different HTTP methods in preflight...")
        for method in ["GET", "POST", "PUT", "DELETE"]:
            url = f"{BASE_URL}/ping"
            headers = {
                "Origin": "https://henna-lash.onrender.com",
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            try:
                response = requests.options(url, headers=headers, timeout=10)
                if response.status_code in [200, 204]:
                    print_success(f"✅ {method} method allowed in preflight")
                    self.results['passed'] += 1
                else:
                    print_error(f"❌ {method} method rejected: {response.status_code}")
                    self.results['failed'] += 1
            except Exception as e:
                print_error(f"❌ {method} preflight failed: {str(e)}")
                self.results['failed'] += 1
        
        # Test with different headers
        print_info("Testing different headers in preflight...")
        headers_to_test = [
            "Content-Type",
            "Authorization", 
            "Content-Type,Authorization",
            "X-Custom-Header"
        ]
        
        for header_list in headers_to_test:
            url = f"{BASE_URL}/ping"
            headers = {
                "Origin": "https://henna-lash.onrender.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": header_list
            }
            
            try:
                response = requests.options(url, headers=headers, timeout=10)
                if response.status_code in [200, 204]:
                    print_success(f"✅ Headers '{header_list}' allowed")
                    self.results['passed'] += 1
                else:
                    print_warning(f"⚠️  Headers '{header_list}' rejected: {response.status_code}")
                    self.results['warnings'] += 1
            except Exception as e:
                print_error(f"❌ Headers '{header_list}' test failed: {str(e)}")
                self.results['failed'] += 1
        
        # Print final results
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("CORS TEST RESULTS SUMMARY")
        print_success(f"Passed: {self.results['passed']}")
        if self.results['warnings'] > 0:
            print_warning(f"Warnings: {self.results['warnings']}")
        if self.results['failed'] > 0:
            print_error(f"Failed: {self.results['failed']}")
        else:
            print_success("All CORS tests passed!")
        
        total_tests = self.results['passed'] + self.results['failed'] + self.results['warnings']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print_info(f"Success rate: {success_rate:.1f}%")
        print_info(f"Test duration: {duration:.2f} seconds")
        
        # Specific diagnosis for the user's issue
        print_header("DIAGNOSIS FOR USER'S ISSUE")
        
        if self.results['failed'] == 0:
            print_success("🎉 CORS IS WORKING CORRECTLY!")
            print_success("✅ No 400 Bad Request errors on OPTIONS preflight")
            print_success("✅ All required CORS headers present")
            print_success("✅ Frontend should be able to make API calls")
            print_info("If user still sees 'Network Error', the issue is likely:")
            print_info("  1. Browser cache - try hard refresh (Ctrl+F5)")
            print_info("  2. Frontend configuration issue")
            print_info("  3. Client-side network/firewall issue")
        else:
            print_error("❌ CORS ISSUES DETECTED!")
            print_error("The user's 'Network Error' is likely caused by these CORS problems")
            print_info("Recommended fixes:")
            print_info("  1. Check server.py CORS configuration")
            print_info("  2. Verify allow_origins list includes user's domain")
            print_info("  3. Ensure allow_credentials=True is compatible with origins")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = CORSTester()
    success = tester.run_comprehensive_cors_tests()
    exit(0 if success else 1)