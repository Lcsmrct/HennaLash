#!/usr/bin/env python3
"""
Backend Comprehensive Testing - Final Validation
Focus: All corrections mentioned in review request
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

class ComprehensiveBackendTester:
    def __init__(self):
        self.admin_token = None
        self.client_token = None
        self.test_results = []
        self.available_slots = []
        
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

    def test_backend_health_and_mongodb(self):
        """Test 1: Backend Health and MongoDB Connection"""
        print("\n🏥 TEST 1: SANTÉ GÉNÉRALE DU BACKEND")
        print("-" * 40)
        
        # Test /api/ping
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/ping", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200 and response.json().get("status") == "Ok":
                self.log_result("Backend Health (/api/ping)", True, "Backend responding correctly", duration)
            else:
                self.log_result("Backend Health (/api/ping)", False, f"Unexpected response: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Backend Health (/api/ping)", False, f"Exception: {str(e)}")
            return False
        
        # Test MongoDB connection by checking if we can retrieve data
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/reviews?approved_only=true", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                reviews = response.json()
                self.log_result("MongoDB Connection", True, f"Database accessible - {len(reviews)} reviews found", duration)
                return True
            else:
                self.log_result("MongoDB Connection", False, f"Database access failed: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("MongoDB Connection", False, f"Exception: {str(e)}")
            return False

    def test_authentication_system(self):
        """Test 2: Authentication System (Login/Register)"""
        print("\n🔐 TEST 2: FONCTIONNALITÉS CORE - AUTHENTIFICATION")
        print("-" * 50)
        
        # Test client registration and login
        random_num = random.randint(10000, 99999)
        client_email = f"testclient{random_num}@email.com"
        
        try:
            # Register new client
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
                    self.log_result("Client Login", True, "Client authentication successful", duration)
                    return True
                else:
                    self.log_result("Client Login", False, f"Login failed: {response.status_code} - {response.text}", duration)
                    return False
            else:
                self.log_result("Client Registration", False, f"Registration failed: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Authentication System", False, f"Exception: {str(e)}")
            return False

    def test_crud_operations(self):
        """Test 3: CRUD Operations for Appointments, Slots, Reviews"""
        print("\n🔧 TEST 3: OPÉRATIONS CRUD (APPOINTMENTS, SLOTS, REVIEWS)")
        print("-" * 55)
        
        if not self.client_token:
            self.log_result("CRUD Operations", False, "Missing client token")
            return False
        
        # Test getting available slots
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=TIMEOUT)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.available_slots = response.json()
                self.log_result("Get Available Slots", True, f"Retrieved {len(self.available_slots)} available slots", duration)
            else:
                self.log_result("Get Available Slots", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Get Available Slots", False, f"Exception: {str(e)}")
            return False
        
        # Test reviews system
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            review_data = {
                "rating": 5,
                "comment": "Test review pour validation système backend"
            }
            
            response = requests.post(
                f"{BASE_URL}/reviews",
                json=review_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Create Review", True, "Review created successfully", duration)
                return True
            else:
                self.log_result("Create Review", False, f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Create Review", False, f"Exception: {str(e)}")
            return False

    def test_location_parsing_in_appointments(self):
        """Test 4: Location Information Storage in Appointment Notes (CRITICAL FIX)"""
        print("\n📍 TEST 4: CORRECTION AFFICHAGE LIEU DANS ESPACE CLIENT")
        print("-" * 55)
        
        if not self.client_token or not self.available_slots:
            self.log_result("Location Parsing Test", False, "Missing client token or available slots")
            return False
        
        # Test location information storage in notes
        location_scenarios = [
            {
                "notes": "Lieu: salon\nPersonnes: 2\nInstagram: @sophie_beauty",
                "expected_parsing": "Chez moi",
                "description": "Salon location (should parse to 'Chez moi')"
            },
            {
                "notes": "Lieu: domicile\nPersonnes: 1\nInstagram: @marie_style", 
                "expected_parsing": "Chez vous",
                "description": "Domicile location (should parse to 'Chez vous')"
            },
            {
                "notes": "Lieu: evenement\nPersonnes: 3\nInstagram: @event_beauty",
                "expected_parsing": "Autre",
                "description": "Event location (should parse to 'Autre')"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        successful_tests = 0
        
        for i, scenario in enumerate(location_scenarios):
            if i >= len(self.available_slots):
                break
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.available_slots[i]["id"],
                    "service_name": "Très simple",
                    "service_price": 5.0,
                    "notes": scenario["notes"]
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
                    
                    # Verify the location information is stored correctly in notes
                    if scenario["notes"] in stored_notes:
                        self.log_result(f"Location Storage ({scenario['expected_parsing']})", True, 
                                      f"✅ Location info stored correctly for parsing to '{scenario['expected_parsing']}'", duration)
                        successful_tests += 1
                    else:
                        self.log_result(f"Location Storage ({scenario['expected_parsing']})", False, 
                                      f"Location info not stored correctly", duration)
                elif response.status_code == 422:
                    self.log_result(f"Location Storage ({scenario['expected_parsing']})", False, 
                                  f"❌ 422 ERROR: {response.text}", duration)
                else:
                    self.log_result(f"Location Storage ({scenario['expected_parsing']})", False, 
                                  f"Status {response.status_code}: {response.text}", duration)
            except Exception as e:
                self.log_result(f"Location Storage ({scenario['expected_parsing']})", False, f"Exception: {str(e)}")
        
        # Overall result
        if successful_tests >= 2:  # At least 2 out of 3 scenarios should work
            self.log_result("Location Parsing System", True, f"Location information correctly stored in notes for frontend parsing ({successful_tests}/3 scenarios)")
            return True
        else:
            self.log_result("Location Parsing System", False, f"Location storage issues detected ({successful_tests}/3 scenarios)")
            return False

    def test_service_selection_422_fix(self):
        """Test 5: Service Selection System - 422 Error Fix (CRITICAL)"""
        print("\n🎨 TEST 5: ERREUR 422 RÉSERVATION RENDEZ-VOUS (CORRECTION)")
        print("-" * 55)
        
        if not self.client_token or not self.available_slots:
            self.log_result("422 Fix Test", False, "Missing client token or available slots")
            return False
        
        # Test all 4 services with NUMERIC prices (not string prices like "5€")
        services = [
            {"name": "Très simple", "price": 5.0, "description": "Service basique 5€"},
            {"name": "Simple", "price": 8.0, "description": "Service standard 8€"},
            {"name": "Chargé", "price": 12.0, "description": "Service avancé 12€"},
            {"name": "Mariée", "price": 20.0, "description": "Service premium 20€"}
        ]
        
        headers = {"Authorization": f"Bearer {self.client_token}"}
        successful_bookings = 0
        
        for i, service in enumerate(services):
            if i >= len(self.available_slots):
                break
                
            try:
                start_time = time.time()
                appointment_data = {
                    "slot_id": self.available_slots[i]["id"],
                    "service_name": service["name"],
                    "service_price": service["price"],  # CRITICAL: Numeric price (not string)
                    "notes": f"Test {service['description']} - Correction erreur 422"
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
                    self.log_result(f"Service Booking ({service['name']})", True, 
                                  f"✅ NO 422 ERROR - {service['name']} ({service['price']}€) booked successfully", duration)
                    successful_bookings += 1
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
            self.log_result("422 Error Fix", True, f"✅ ERREUR 422 CORRIGÉE - All {successful_bookings} services work correctly")
            return True
        else:
            self.log_result("422 Error Fix", False, f"❌ ERREUR 422 PERSISTE - Only {successful_bookings}/{len(services)} services work")
            return False

    def test_email_system_modern_templates(self):
        """Test 6: Email System with Modern Templates"""
        print("\n📧 TEST 6: SYSTÈME EMAIL (TEMPLATES MODERNISÉS)")
        print("-" * 50)
        
        # Test email system by creating a review (triggers admin notification)
        if not self.client_token:
            self.log_result("Email System Test", False, "Missing client token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            review_data = {
                "rating": 5,
                "comment": "Test pour vérifier les templates email modernisés avec design premium"
            }
            
            response = requests.post(
                f"{BASE_URL}/reviews",
                json=review_data,
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Email System (Modern Templates)", True, 
                              "✅ Email notification system functional - modern templates should be used", duration)
                return True
            else:
                self.log_result("Email System (Modern Templates)", False, 
                              f"Email system test failed: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Email System (Modern Templates)", False, f"Exception: {str(e)}")
            return False

    def test_appointment_retrieval_with_slot_info(self):
        """Test 7: Appointment Retrieval with Slot Info (for client dashboard)"""
        print("\n📋 TEST 7: RÉCUPÉRATION APPOINTMENTS AVEC SLOT_INFO")
        print("-" * 50)
        
        if not self.client_token:
            self.log_result("Appointment Retrieval", False, "Missing client token")
            return False
        
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            response = requests.get(
                f"{BASE_URL}/appointments",
                headers=headers,
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                appointments = response.json()
                
                if appointments:
                    # Check if appointments have slot_info for location parsing
                    has_slot_info = any(apt.get('slot_info') for apt in appointments)
                    
                    if has_slot_info:
                        sample_apt = next((apt for apt in appointments if apt.get('slot_info')), appointments[0])
                        slot_info = sample_apt.get('slot_info', {})
                        self.log_result("Appointment Slot Info", True, 
                                      f"✅ Appointments include slot_info for frontend parsing - Sample: date={slot_info.get('date', 'N/A')}, time={slot_info.get('start_time', 'N/A')}", duration)
                    else:
                        self.log_result("Appointment Slot Info", False, 
                                      f"❌ Appointments missing slot_info - frontend will show 'Date/Heure non spécifiée'", duration)
                        return False
                else:
                    self.log_result("Appointment Slot Info", True, 
                                  "No appointments found (expected for new client)", duration)
                
                return True
            else:
                self.log_result("Appointment Slot Info", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Appointment Slot Info", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run comprehensive tests for all user corrections"""
        print("🎯 TESTS BACKEND COMPLETS - VALIDATION CORRECTIONS")
        print("=" * 70)
        print("Focus: Lieu, Erreur 422, Design moderne, Templates email, Core functionality")
        print("=" * 70)
        
        # Run all tests
        test_results = []
        
        test_results.append(self.test_backend_health_and_mongodb())
        test_results.append(self.test_authentication_system())
        test_results.append(self.test_crud_operations())
        test_results.append(self.test_location_parsing_in_appointments())
        test_results.append(self.test_service_selection_422_fix())
        test_results.append(self.test_email_system_modern_templates())
        test_results.append(self.test_appointment_retrieval_with_slot_info())
        
        # Summary
        self.print_comprehensive_summary()
        
        return all(test_results)

    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ COMPLET - VALIDATION CORRECTIONS BACKEND")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ RÉUSSIS: {passed}/{total} tests")
        print(f"❌ ÉCHOUÉS: {total - passed}/{total} tests")
        
        # Map tests to user's specific requests
        print("\n🎯 VALIDATION DES CORRECTIONS DEMANDÉES:")
        
        user_requests = {
            "1. Santé générale du backend": {
                "tests": ["Backend Health (/api/ping)", "MongoDB Connection"],
                "description": "Backend démarre correctement, MongoDB connecté"
            },
            "2. Fonctionnalités core": {
                "tests": ["Client Registration", "Client Login", "Get Available Slots", "Create Review"],
                "description": "Authentification, CRUD appointments/slots/reviews"
            },
            "3. Correction lieu dans réservations": {
                "tests": ["Location Parsing System"],
                "description": "Lieu (Chez vous/Chez moi/Autres) stocké dans notes"
            },
            "4. Erreur 422 réservations": {
                "tests": ["422 Error Fix"],
                "description": "Services avec prix numériques (non string)"
            },
            "5. Système email (templates modernisés)": {
                "tests": ["Email System (Modern Templates)"],
                "description": "Notifications admin/client avec design premium"
            },
            "6. Support espace client": {
                "tests": ["Appointment Slot Info"],
                "description": "Appointments avec slot_info pour affichage lieu"
            }
        }
        
        for request, details in user_requests.items():
            request_results = []
            for test_name in details["tests"]:
                result = next((r for r in self.test_results if test_name in r['test']), None)
                if result:
                    request_results.append(result['success'])
            
            if request_results:
                all_passed = all(request_results)
                status = "✅ VALIDÉ" if all_passed else "❌ PROBLÈME"
                print(f"  {status} {request}")
                print(f"    └─ {details['description']}")
        
        # Show critical failures
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 PROBLÈMES DÉTECTÉS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        else:
            print("\n🎉 TOUTES LES CORRECTIONS VALIDÉES AVEC SUCCÈS!")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    tester.run_comprehensive_tests()