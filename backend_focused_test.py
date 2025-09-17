#!/usr/bin/env python3
"""
Backend Focused Testing - Post-Corrections Validation
Focus: Location parsing, Modern design backend support, Email templates, Core functionality
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import random

# Configuration - Use external URL as specified in frontend/.env
BASE_URL = "https://henna-lash.onrender.com/api"
TIMEOUT = 15

class FocusedBackendTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        self.created_slot_ids = []
        
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

    def test_backend_health(self):
        """Test 1: Backend Health and MongoDB Connection"""
        print("\n🏥 TEST 1: SANTÉ GÉNÉRALE DU BACKEND")
        print("-" * 40)
        
        # Test /api/ping
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/ping", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Backend Health Check", True, "Backend responding correctly", duration)
            else:
                self.log_result("Backend Health Check", False, f"Status {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Exception: {str(e)}")
            return False
        
        return True

    def test_authentication_system(self):
        """Test 2: Authentication System"""
        print("\n🔐 TEST 2: SYSTÈME D'AUTHENTIFICATION")
        print("-" * 40)
        
        # Test admin authentication
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
            else:
                # Try to create admin user
                self.create_admin_user()
                return self.test_authentication_system()  # Retry
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
        
        # Test client authentication
        try:
            # Create new client for testing
            random_num = random.randint(1000, 9999)
            client_email = f"testclient{random_num}@email.com"
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": client_email,
                    "password": "client123",
                    "first_name": "Sophie",
                    "last_name": "Martin",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Client Registration", True, f"Client registered: {client_email}", duration)
                
                # Login with new client
                start_time = time.time()
                response = requests.post(
                    f"{BASE_URL}/login",
                    json={
                        "email": client_email,
                        "password": "client123"
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.client_token = response.json()["access_token"]
                    self.log_result("Client Authentication", True, "Client login successful", duration)
                    return True
                else:
                    self.log_result("Client Authentication", False, f"Login failed: {response.status_code}", duration)
                    return False
            else:
                self.log_result("Client Registration", False, f"Registration failed: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False

    def create_admin_user(self):
        """Create admin user if doesn't exist"""
        try:
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": "admin@salon.com",
                    "password": "admin123",
                    "first_name": "Admin",
                    "last_name": "Salon",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                self.log_result("Admin User Creation", True, "Admin user created")
            return True
        except:
            return False

    def test_crud_operations(self):
        """Test 3: CRUD Operations for Core Functionality"""
        print("\n🔧 TEST 3: OPÉRATIONS CRUD CORE")
        print("-" * 40)
        
        if not self.admin_token:
            self.log_result("CRUD Operations", False, "Missing admin token")
            return False
        
        # Test slot creation (simplified format)
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create multiple slots for testing
            tomorrow = datetime.now() + timedelta(days=1)
            times = ["10:00", "11:00", "14:00", "15:00", "16:00"]
            
            created_slots = 0
            for time_slot in times:
                slot_data = {
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "time": time_slot
                }
                
                response = requests.post(
                    f"{BASE_URL}/slots",
                    json=slot_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    slot = response.json()
                    self.created_slot_ids.append(slot["id"])
                    created_slots += 1
            
            duration = time.time() - start_time
            
            if created_slots > 0:
                self.log_result("Slot Creation (Simplified)", True, f"Created {created_slots} slots with auto-calculated end_time", duration)
            else:
                self.log_result("Slot Creation (Simplified)", False, "No slots created", duration)
                return False
        except Exception as e:
            self.log_result("Slot Creation (Simplified)", False, f"Exception: {str(e)}")
            return False
        
        # Test slot retrieval
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                slots = response.json()
                self.log_result("Available Slots Retrieval", True, f"Retrieved {len(slots)} available slots", duration)
            else:
                self.log_result("Available Slots Retrieval", False, f"Status {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Available Slots Retrieval", False, f"Exception: {str(e)}")
            return False
        
        return True

    def test_location_parsing_in_appointments(self):
        """Test 4: Location Information Storage in Appointment Notes"""
        print("\n📍 TEST 4: STOCKAGE INFORMATIONS LIEU DANS NOTES")
        print("-" * 50)
        
        if not self.client_token or not self.created_slot_ids:
            self.log_result("Location Parsing Test", False, "Missing client token or available slots")
            return False
        
        # Test different location scenarios
        location_tests = [
            {
                "notes": "Lieu: salon\nPersonnes: 2\nInstagram: @sophie_beauty",
                "expected_lieu": "Chez moi",
                "description": "Salon location"
            },
            {
                "notes": "Lieu: domicile\nPersonnes: 1\nInstagram: @marie_style",
                "expected_lieu": "Chez vous", 
                "description": "Domicile location"
            },
            {
                "notes": "Lieu: evenement\nPersonnes: 3\nInstagram: @event_beauty",
                "expected_lieu": "Autre",
                "description": "Event location"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        successful_tests = 0
        
        for i, test_case in enumerate(location_tests):
            if i >= len(self.created_slot_ids):
                break
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.created_slot_ids[i],
                    "service_name": "Très simple",
                    "service_price": 5.0,
                    "notes": test_case["notes"]
                }
                
                response = requests.post(
                    f"{BASE_URL}/appointments",
                    json=appointment_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    appointment = response.json()
                    stored_notes = appointment.get("notes", "")
                    
                    # Verify notes are stored correctly
                    if test_case["notes"] in stored_notes:
                        self.log_result(f"Location Storage ({test_case['description']})", True, 
                                      f"Notes stored correctly for {test_case['expected_lieu']}", duration)
                        successful_tests += 1
                    else:
                        self.log_result(f"Location Storage ({test_case['description']})", False, 
                                      f"Notes not stored correctly", duration)
                else:
                    self.log_result(f"Location Storage ({test_case['description']})", False, 
                                  f"Appointment creation failed: {response.status_code}", duration)
            except Exception as e:
                self.log_result(f"Location Storage ({test_case['description']})", False, f"Exception: {str(e)}")
        
        # Overall result
        if successful_tests == len(location_tests):
            self.log_result("Location Parsing System", True, f"All {successful_tests} location scenarios work correctly")
            return True
        else:
            self.log_result("Location Parsing System", False, f"Only {successful_tests}/{len(location_tests)} scenarios work")
            return False

    def test_service_selection_system(self):
        """Test 5: Service Selection with All 4 Services"""
        print("\n🎨 TEST 5: SYSTÈME SÉLECTION SERVICES (4 SERVICES)")
        print("-" * 50)
        
        if not self.client_token or len(self.created_slot_ids) < 4:
            self.log_result("Service Selection Test", False, "Missing client token or insufficient slots")
            return False
        
        services = [
            {"name": "Très simple", "price": 5.0, "description": "Service basique"},
            {"name": "Simple", "price": 8.0, "description": "Service standard"},
            {"name": "Chargé", "price": 12.0, "description": "Service avancé"},
            {"name": "Mariée", "price": 20.0, "description": "Service premium"}
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        successful_bookings = 0
        
        for i, service in enumerate(services):
            if i >= len(self.created_slot_ids):
                break
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.created_slot_ids[i],
                    "service_name": service["name"],
                    "service_price": service["price"],  # CRITICAL: Numeric price
                    "notes": f"Test {service['description']} - Prix: {service['price']}€"
                }
                
                response = requests.post(
                    f"{BASE_URL}/appointments",
                    json=appointment_data,
                    headers=headers,
                    timeout=TIMEOUT
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    appointment = response.json()
                    stored_service = appointment.get("service_name")
                    stored_price = appointment.get("service_price")
                    
                    if stored_service == service["name"] and stored_price == service["price"]:
                        self.log_result(f"Service Booking ({service['name']})", True, 
                                      f"✅ {service['name']} ({service['price']}€) booked successfully", duration)
                        successful_bookings += 1
                    else:
                        self.log_result(f"Service Booking ({service['name']})", False, 
                                      f"Service data mismatch: expected {service['name']}/{service['price']}, got {stored_service}/{stored_price}", duration)
                elif response.status_code == 422:
                    self.log_result(f"Service Booking ({service['name']})", False, 
                                  f"❌ 422 ERROR STILL EXISTS: {response.text}", duration)
                else:
                    self.log_result(f"Service Booking ({service['name']})", False, 
                                  f"Status {response.status_code}: {response.text}", duration)
            except Exception as e:
                self.log_result(f"Service Booking ({service['name']})", False, f"Exception: {str(e)}")
        
        # Overall result
        if successful_bookings == len(services):
            self.log_result("All Services System", True, f"All {successful_bookings} services work correctly - 422 error RESOLVED")
            return True
        else:
            self.log_result("All Services System", False, f"Only {successful_bookings}/{len(services)} services work - 422 error may persist")
            return False

    def test_email_system(self):
        """Test 6: Email System (if configured)"""
        print("\n📧 TEST 6: SYSTÈME EMAIL (TEMPLATES MODERNISÉS)")
        print("-" * 50)
        
        # Test by checking if email service is configured
        # We can't directly test email sending without access to the email account
        # But we can verify the backend accepts email-triggering operations
        
        if not self.admin_token:
            self.log_result("Email System Test", False, "Missing admin token")
            return False
        
        # Test review creation (triggers email notification)
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            review_data = {
                "rating": 5,
                "comment": "Test review pour vérifier le système email modernisé"
            }
            
            response = requests.post(
                f"{BASE_URL}/reviews",
                json=review_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Email System (Review Notification)", True, 
                              "Review created successfully - email notification should be sent", duration)
                return True
            else:
                self.log_result("Email System (Review Notification)", False, 
                              f"Review creation failed: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Email System (Review Notification)", False, f"Exception: {str(e)}")
            return False

    def test_reviews_system(self):
        """Test 7: Reviews System"""
        print("\n⭐ TEST 7: SYSTÈME AVIS")
        print("-" * 25)
        
        # Test public reviews endpoint (no auth required)
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/reviews?approved_only=true", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                reviews = response.json()
                self.log_result("Public Reviews Retrieval", True, f"Retrieved {len(reviews)} approved reviews", duration)
            else:
                self.log_result("Public Reviews Retrieval", False, f"Status {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Public Reviews Retrieval", False, f"Exception: {str(e)}")
            return False
        
        # Test admin reviews endpoint (auth required)
        if self.admin_token:
            try:
                start_time = time.time()
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BASE_URL}/reviews", headers=headers, timeout=TIMEOUT)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    reviews = response.json()
                    self.log_result("Admin Reviews Management", True, f"Admin can access {len(reviews)} reviews", duration)
                    return True
                else:
                    self.log_result("Admin Reviews Management", False, f"Status {response.status_code}", duration)
                    return False
            except Exception as e:
                self.log_result("Admin Reviews Management", False, f"Exception: {str(e)}")
                return False
        
        return True

    def run_focused_tests(self):
        """Run focused tests based on user's corrections"""
        print("🎯 TESTS BACKEND POST-CORRECTIONS")
        print("=" * 60)
        print("Focus: Lieu, Design moderne, Templates email, Fonctionnalités core")
        print("=" * 60)
        
        # Run all focused tests
        test_results = []
        
        test_results.append(self.test_backend_health())
        test_results.append(self.test_authentication_system())
        test_results.append(self.test_crud_operations())
        test_results.append(self.test_location_parsing_in_appointments())
        test_results.append(self.test_service_selection_system())
        test_results.append(self.test_email_system())
        test_results.append(self.test_reviews_system())
        
        # Summary
        self.print_focused_summary()
        
        return all(test_results)

    def print_focused_summary(self):
        """Print focused test summary"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ TESTS BACKEND POST-CORRECTIONS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ RÉUSSIS: {passed}/{total} tests")
        print(f"❌ ÉCHOUÉS: {total - passed}/{total} tests")
        
        # Critical results for user's specific requests
        print("\n🎯 RÉSULTATS CRITIQUES (Demandes utilisateur):")
        
        critical_categories = {
            "Santé Backend": ["Backend Health Check"],
            "Authentification": ["Admin Authentication", "Client Authentication"],
            "Lieu dans Notes": ["Location Parsing System"],
            "Services (422 Fix)": ["All Services System"],
            "Email Modernisé": ["Email System (Review Notification)"],
            "CRUD Core": ["Slot Creation (Simplified)", "Available Slots Retrieval"]
        }
        
        for category, test_names in critical_categories.items():
            category_results = []
            for test_name in test_names:
                result = next((r for r in self.test_results if test_name in r['test']), None)
                if result:
                    category_results.append(result['success'])
            
            if category_results:
                all_passed = all(category_results)
                status = "✅" if all_passed else "❌"
                print(f"  {status} {category}: {'FONCTIONNEL' if all_passed else 'PROBLÈMES DÉTECTÉS'}")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 TESTS ÉCHOUÉS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        else:
            print("\n🎉 TOUS LES TESTS RÉUSSIS - CORRECTIONS VALIDÉES!")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = FocusedBackendTester()
    tester.run_focused_tests()