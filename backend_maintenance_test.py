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

class MaintenanceTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        
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
        """Authenticate as admin user"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "admin@salon.com",
                    "password": "admin123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                self.log_result("Admin Authentication", True, "Admin login successful", duration)
                return True
            else:
                self.log_result("Admin Authentication", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_client(self):
        """Authenticate as client user"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "marie.dupont@email.com",
                    "password": "motdepasse123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.client_token = response.json()["access_token"]
                self.log_result("Client Authentication", True, "Client login successful", duration)
                return True
            else:
                self.log_result("Client Authentication", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False

    def test_maintenance_status_get(self):
        """MAINTENANCE TEST: GET /api/maintenance - check maintenance status (public endpoint)"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{BASE_URL}/maintenance",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                maintenance_data = response.json()
                is_maintenance = maintenance_data.get('is_maintenance', False)
                message = maintenance_data.get('message', 'N/A')
                
                self.log_result("Maintenance Status GET", True, 
                              f"✅ Maintenance status retrieved: is_maintenance={is_maintenance}, message='{message}'", duration)
                return True
            else:
                self.log_result("Maintenance Status GET", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Status GET", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_toggle_admin_only(self):
        """MAINTENANCE TEST: POST /api/maintenance - toggle maintenance (admin only)"""
        if not self.admin_token:
            self.log_result("Maintenance Toggle Admin", False, "Missing admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test enabling maintenance
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "Site en maintenance pour tests automatisés"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                maintenance_data = response.json()
                is_maintenance = maintenance_data.get('is_maintenance', False)
                
                if is_maintenance:
                    self.log_result("Maintenance Toggle Admin", True, 
                                  f"✅ Maintenance enabled successfully by admin", duration)
                    
                    # Test disabling maintenance
                    start_time = time.time()
                    response = requests.post(
                        f"{BASE_URL}/maintenance",
                        json={
                            "is_maintenance": False,
                            "message": "Site opérationnel"
                        },
                        headers=headers,
                        timeout=TIMEOUT
                    )
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        maintenance_data = response.json()
                        is_maintenance = maintenance_data.get('is_maintenance', False)
                        
                        if not is_maintenance:
                            self.log_result("Maintenance Disable Admin", True, 
                                          f"✅ Maintenance disabled successfully by admin", duration)
                            return True
                        else:
                            self.log_result("Maintenance Disable Admin", False, 
                                          f"Maintenance still enabled after disable request", duration)
                            return False
                    else:
                        self.log_result("Maintenance Disable Admin", False, 
                                      f"Status {response.status_code}: {response.text}", duration)
                        return False
                else:
                    self.log_result("Maintenance Toggle Admin", False, 
                                  f"Maintenance not enabled after enable request", duration)
                    return False
            else:
                self.log_result("Maintenance Toggle Admin", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Toggle Admin", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_toggle_client_forbidden(self):
        """MAINTENANCE TEST: POST /api/maintenance - verify clients cannot toggle maintenance"""
        if not self.client_token:
            self.log_result("Maintenance Toggle Client Forbidden", False, "Missing client token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "Tentative client non autorisée"
                },
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 403:
                self.log_result("Maintenance Toggle Client Forbidden", True, 
                              f"✅ Client correctly forbidden from toggling maintenance (403)", duration)
                return True
            elif response.status_code == 401:
                self.log_result("Maintenance Toggle Client Forbidden", True, 
                              f"✅ Client correctly unauthorized for maintenance toggle (401)", duration)
                return True
            else:
                self.log_result("Maintenance Toggle Client Forbidden", False, 
                              f"Expected 403/401, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Toggle Client Forbidden", False, f"Exception: {str(e)}")
            return False
    
    def test_maintenance_toggle_no_auth(self):
        """MAINTENANCE TEST: POST /api/maintenance - verify no auth cannot toggle maintenance"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance",
                json={
                    "is_maintenance": True,
                    "message": "Tentative sans authentification"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Maintenance Toggle No Auth", True, 
                              f"✅ Unauthenticated request correctly rejected (401)", duration)
                return True
            elif response.status_code == 403:
                self.log_result("Maintenance Toggle No Auth", True, 
                              f"✅ Unauthenticated request correctly forbidden (403)", duration)
                return True
            else:
                self.log_result("Maintenance Toggle No Auth", False, 
                              f"Expected 401/403, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Maintenance Toggle No Auth", False, f"Exception: {str(e)}")
            return False
    
    def test_emergency_disable_maintenance(self):
        """MAINTENANCE TEST: POST /api/maintenance/emergency-disable - emergency disable endpoint"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/maintenance/emergency-disable",
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Emergency Disable Maintenance", True, 
                              f"✅ Emergency disable works: {result.get('message', 'N/A')}", duration)
                return True
            else:
                self.log_result("Emergency Disable Maintenance", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Emergency Disable Maintenance", False, f"Exception: {str(e)}")
            return False

    def test_admin_authentication_regression(self):
        """REGRESSION TEST: Verify admin authentication still works correctly"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "admin@salon.com",
                    "password": "admin123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.log_result("Admin Authentication Regression", True, 
                                  f"✅ Admin authentication works correctly", duration)
                    return True
                else:
                    self.log_result("Admin Authentication Regression", False, 
                                  f"No access token in response", duration)
                    return False
            else:
                self.log_result("Admin Authentication Regression", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Authentication Regression", False, f"Exception: {str(e)}")
            return False

    def test_client_authentication_regression(self):
        """REGRESSION TEST: Verify client authentication still works correctly"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": "marie.dupont@email.com",
                    "password": "motdepasse123"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.log_result("Client Authentication Regression", True, 
                                  f"✅ Client authentication works correctly", duration)
                    return True
                else:
                    self.log_result("Client Authentication Regression", False, 
                                  f"No access token in response", duration)
                    return False
            else:
                self.log_result("Client Authentication Regression", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Client Authentication Regression", False, f"Exception: {str(e)}")
            return False

    def test_health_check_regression(self):
        """REGRESSION TEST: Verify health check endpoints still work"""
        try:
            # Test GET /api/ping
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/ping", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "Ok":
                    self.log_result("Health Check GET Regression", True, 
                                  f"✅ GET /api/ping works correctly", duration)
                    
                    # Test HEAD /api/ping
                    start_time = time.time()
                    response = requests.head(f"{BASE_URL}/ping", timeout=TIMEOUT)
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        self.log_result("Health Check HEAD Regression", True, 
                                      f"✅ HEAD /api/ping works correctly", duration)
                        return True
                    else:
                        self.log_result("Health Check HEAD Regression", False, 
                                      f"HEAD Status {response.status_code}", duration)
                        return False
                else:
                    self.log_result("Health Check GET Regression", False, 
                                  f"Wrong status in response: {data}", duration)
                    return False
            else:
                self.log_result("Health Check GET Regression", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Health Check Regression", False, f"Exception: {str(e)}")
            return False

    def test_admin_slots_endpoint(self):
        """REGRESSION TEST: Verify admin can still create slots"""
        if not self.admin_token:
            self.log_result("Admin Slots Endpoint", False, "Missing admin token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create slot for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            slot_data = {
                "date": tomorrow.strftime("%Y-%m-%d"),
                "time": "15:30"  # 3:30 PM
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/slots",
                json=slot_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slot = response.json()
                self.log_result("Admin Slots Endpoint", True, 
                              f"✅ Admin can create slots: {slot.get('id', 'N/A')}", duration)
                return True
            else:
                self.log_result("Admin Slots Endpoint", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Slots Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_admin_appointments_endpoint(self):
        """REGRESSION TEST: Verify admin can still view appointments"""
        if not self.admin_token:
            self.log_result("Admin Appointments Endpoint", False, "Missing admin token")
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
                self.log_result("Admin Appointments Endpoint", True, 
                              f"✅ Admin can view appointments: {len(appointments)} found", duration)
                return True
            else:
                self.log_result("Admin Appointments Endpoint", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Admin Appointments Endpoint", False, f"Exception: {str(e)}")
            return False

    def run_tests(self):
        """Run maintenance tests and regression tests"""
        print("🔧 BACKEND API TESTING - MAINTENANCE FEATURES & REGRESSION TESTS")
        print("=" * 70)
        print("Focus: Tester les nouvelles fonctionnalités de maintenance et vérifier les régressions")
        print("1. Endpoints de maintenance (critique) - GET/POST /api/maintenance")
        print("2. Interface admin améliorée - vérifier authentification admin")
        print("3. Tests de régression - s'assurer que les fonctionnalités existantes marchent toujours")
        print("=" * 70)
        
        # Authentication setup
        print("\n🔐 AUTHENTICATION SETUP")
        print("-" * 30)
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.authenticate_client():
            print("❌ Cannot proceed without client authentication")
            return
        
        # PRIORITY 1: MAINTENANCE ENDPOINTS TESTING
        print("\n🚨 PRIORITY 1: MAINTENANCE ENDPOINTS TESTING")
        print("-" * 50)
        print("Testing GET /api/maintenance - vérifier le statut de maintenance")
        self.test_maintenance_status_get()
        
        print("\nTesting POST /api/maintenance - activer/désactiver la maintenance (admin uniquement)")
        self.test_maintenance_toggle_admin_only()
        
        print("\nTesting POST /api/maintenance - vérifier que seuls les admins peuvent modifier le statut")
        self.test_maintenance_toggle_client_forbidden()
        self.test_maintenance_toggle_no_auth()
        
        print("\nTesting POST /api/maintenance/emergency-disable - route d'urgence")
        self.test_emergency_disable_maintenance()
        
        # PRIORITY 2: ADMIN INTERFACE REGRESSION TESTS
        print("\n🔧 PRIORITY 2: INTERFACE ADMIN AMÉLIORÉE")
        print("-" * 50)
        print("Testing admin authentication regression")
        self.test_admin_authentication_regression()
        
        print("\nTesting admin slot creation endpoint")
        self.test_admin_slots_endpoint()
        
        print("\nTesting admin appointments endpoint")
        self.test_admin_appointments_endpoint()
        
        # PRIORITY 3: REGRESSION TESTS
        print("\n🔄 PRIORITY 3: TESTS DE RÉGRESSION")
        print("-" * 50)
        print("Testing client authentication regression")
        self.test_client_authentication_regression()
        
        print("\nTesting health check endpoints regression")
        self.test_health_check_regression()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 MAINTENANCE & REGRESSION TEST SUMMARY")
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
        
        # Show maintenance results
        print("\n🔧 MAINTENANCE ENDPOINTS RESULTS:")
        maintenance_tests = [
            "Maintenance Status GET",
            "Maintenance Toggle Admin", 
            "Maintenance Disable Admin",
            "Maintenance Toggle Client Forbidden",
            "Maintenance Toggle No Auth",
            "Emergency Disable Maintenance"
        ]
        
        for test_name in maintenance_tests:
            result = next((r for r in self.test_results if r['test'] == test_name), None)
            if result:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {test_name}: {result['message']}")
        
        # Show regression results
        print("\n🔄 REGRESSION TEST RESULTS:")
        regression_tests = [
            "Admin Authentication Regression",
            "Client Authentication Regression",
            "Health Check GET Regression",
            "Health Check HEAD Regression",
            "Admin Slots Endpoint",
            "Admin Appointments Endpoint"
        ]
        
        for test_name in regression_tests:
            result = next((r for r in self.test_results if r['test'] == test_name), None)
            if result:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {test_name}: {result['message']}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = MaintenanceTester()
    tester.run_tests()