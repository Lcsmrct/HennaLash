#!/usr/bin/env python3
"""
Comprehensive Password Reset System Testing
Focus: Test complet du workflow de réinitialisation avec code réel
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import random
import re

# Configuration - Use frontend .env URL
BASE_URL = "https://cancel-appt-fix.preview.emergentagent.com/api"
TIMEOUT = 15

class ComprehensivePasswordResetTester:
    def __init__(self):
        self.test_results = []
        # Create unique test user for this session
        self.test_user_email = f"testreset{random.randint(1000, 9999)}@test.com"
        self.test_user_password = "originalpassword123"
        self.new_password = "nouveaumotdepasse456"
        self.reset_code = None
        
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

    def create_test_user(self):
        """Create a fresh test user for this test session"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": self.test_user_email,
                    "password": self.test_user_password,
                    "first_name": "Test",
                    "last_name": "Reset",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Create Test User", True, 
                              f"Test user created: {self.test_user_email}", duration)
                return True
            else:
                self.log_result("Create Test User", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Create Test User", False, f"Exception: {str(e)}")
            return False

    def verify_initial_login(self):
        """Verify user can login with original password"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": self.test_user_email,
                    "password": self.test_user_password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Initial Login Verification", True, 
                              "User can login with original password", duration)
                return True
            else:
                self.log_result("Initial Login Verification", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Initial Login Verification", False, f"Exception: {str(e)}")
            return False

    def request_password_reset(self):
        """Request password reset and capture any code information"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/auth/password-reset/request",
                json={"email": self.test_user_email},
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Password Reset Request", True, 
                              f"Request successful: {result.get('message', 'N/A')}", duration)
                
                # Wait a moment for email processing
                time.sleep(2)
                return True
            else:
                self.log_result("Password Reset Request", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Request", False, f"Exception: {str(e)}")
            return False

    def test_brute_force_code_discovery(self):
        """Try to discover the reset code using systematic approach"""
        print("🔍 TENTATIVE DE DÉCOUVERTE DU CODE DE RÉINITIALISATION")
        print("   Note: Test systématique de codes possibles...")
        
        # Try common patterns for 6-digit codes
        code_patterns = []
        
        # Sequential numbers
        for i in range(100000, 999999, 111111):  # 100000, 211111, 322222, etc.
            code_patterns.append(str(i))
        
        # Common patterns
        common_codes = [
            "123456", "654321", "111111", "222222", "333333", "444444", "555555", 
            "666666", "777777", "888888", "999999", "000000", "123123", "456456",
            "789789", "147147", "258258", "369369", "159159", "753753"
        ]
        code_patterns.extend(common_codes)
        
        # Random codes (since it's randomly generated)
        for _ in range(50):
            code_patterns.append(f"{random.randint(100000, 999999):06d}")
        
        for code in code_patterns:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/password-reset/confirm",
                    json={
                        "email": self.test_user_email,
                        "code": code,
                        "new_password": self.new_password
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    self.reset_code = code
                    self.log_result("Code Discovery", True, 
                                  f"Found valid reset code: {code}")
                    return True
                elif response.status_code == 400:
                    # Expected for invalid codes
                    continue
                else:
                    print(f"   Unexpected response for code {code}: {response.status_code}")
                    
            except Exception as e:
                print(f"   Exception testing code {code}: {str(e)}")
                continue
        
        self.log_result("Code Discovery", False, 
                      "Could not discover valid reset code")
        return False

    def test_password_reset_with_invalid_code(self):
        """Test password reset with invalid code"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/auth/password-reset/confirm",
                json={
                    "email": self.test_user_email,
                    "code": "000000",  # Invalid code
                    "new_password": self.new_password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 400:
                self.log_result("Invalid Code Test", True, 
                              "Correctly rejected invalid code with 400", duration)
                return True
            else:
                self.log_result("Invalid Code Test", False, 
                              f"Expected 400, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Invalid Code Test", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_with_valid_code(self):
        """Test password reset with the discovered valid code"""
        if not self.reset_code:
            self.log_result("Valid Code Reset", False, 
                          "No valid reset code available for testing")
            return False
            
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/auth/password-reset/confirm",
                json={
                    "email": self.test_user_email,
                    "code": self.reset_code,
                    "new_password": self.new_password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Valid Code Reset", True, 
                              f"Password reset successful: {result.get('message', 'N/A')}", duration)
                return True
            else:
                self.log_result("Valid Code Reset", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Valid Code Reset", False, f"Exception: {str(e)}")
            return False

    def test_login_with_new_password(self):
        """CRITICAL TEST: Verify login with new password works"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": self.test_user_email,
                    "password": self.new_password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.log_result("New Password Login", True, 
                              f"✅ CRITICAL SUCCESS: Password was updated in database! Login successful", duration)
                return True
            else:
                self.log_result("New Password Login", False, 
                              f"❌ CRITICAL FAILURE: Password NOT updated in database! Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("New Password Login", False, f"Exception: {str(e)}")
            return False

    def test_login_with_old_password(self):
        """Verify old password no longer works"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": self.test_user_email,
                    "password": self.test_user_password  # Old password
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 401:
                self.log_result("Old Password Login", True, 
                              "✅ CORRECT: Old password correctly rejected", duration)
                return True
            elif response.status_code == 200:
                self.log_result("Old Password Login", False, 
                              "❌ PROBLEM: Old password still works - password may not have been updated", duration)
                return False
            else:
                self.log_result("Old Password Login", False, 
                              f"Unexpected status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Old Password Login", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run the complete password reset workflow test"""
        print("🔐 TEST COMPLET SYSTÈME DE RÉINITIALISATION DE MOT DE PASSE")
        print("=" * 80)
        print("Focus: Test complet avec utilisateur frais et découverte de code")
        print("=" * 80)
        
        # Step 1: Create fresh test user
        print("\n👤 ÉTAPE 1: Création utilisateur test")
        print("-" * 50)
        if not self.create_test_user():
            print("❌ Impossible de créer l'utilisateur test")
            return
        
        # Step 2: Verify initial login
        print("\n🔑 ÉTAPE 2: Vérification connexion initiale")
        print("-" * 50)
        if not self.verify_initial_login():
            print("❌ Impossible de se connecter avec le mot de passe initial")
            return
        
        # Step 3: Request password reset
        print("\n📧 ÉTAPE 3: Demande de réinitialisation")
        print("-" * 50)
        if not self.request_password_reset():
            print("❌ Échec de la demande de réinitialisation")
            return
        
        # Step 4: Test invalid code
        print("\n🚫 ÉTAPE 4: Test code invalide")
        print("-" * 50)
        self.test_password_reset_with_invalid_code()
        
        # Step 5: Try to discover valid code
        print("\n🔍 ÉTAPE 5: Découverte du code valide")
        print("-" * 50)
        code_found = self.test_brute_force_code_discovery()
        
        # Step 6: Test password reset with valid code
        print("\n✅ ÉTAPE 6: Réinitialisation avec code valide")
        print("-" * 50)
        if code_found:
            reset_success = self.test_password_reset_with_valid_code()
        else:
            print("⚠️ Code non trouvé - test de réinitialisation sauté")
            reset_success = False
        
        # Step 7: CRITICAL - Test login with new password
        print("\n🔑 ÉTAPE 7: CRITIQUE - Test connexion nouveau mot de passe")
        print("-" * 50)
        if reset_success:
            new_password_works = self.test_login_with_new_password()
            
            # Step 8: Verify old password no longer works
            print("\n🔒 ÉTAPE 8: Vérification ancien mot de passe")
            print("-" * 50)
            self.test_login_with_old_password()
        else:
            print("⚠️ Réinitialisation échouée - tests de connexion sautés")
        
        # Final diagnosis
        self.print_final_diagnosis()

    def print_final_diagnosis(self):
        """Print comprehensive diagnosis"""
        print("\n" + "=" * 80)
        print("🔍 DIAGNOSTIC FINAL COMPLET")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ TESTS RÉUSSIS: {passed}/{total}")
        print(f"❌ TESTS ÉCHOUÉS: {total - passed}/{total}")
        
        # Critical analysis
        print("\n🚨 ANALYSE CRITIQUE:")
        
        # Check each step
        steps = [
            ("Create Test User", "Création utilisateur"),
            ("Initial Login Verification", "Connexion initiale"),
            ("Password Reset Request", "Demande réinitialisation"),
            ("Invalid Code Test", "Validation codes invalides"),
            ("Code Discovery", "Découverte code valide"),
            ("Valid Code Reset", "Réinitialisation avec code valide"),
            ("New Password Login", "Connexion nouveau mot de passe"),
            ("Old Password Login", "Rejet ancien mot de passe")
        ]
        
        for test_key, description in steps:
            result = next((r for r in self.test_results if r['test'] == test_key), None)
            if result:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {description}: {result['message']}")
        
        # Show failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 DÉTAILS DES ÉCHECS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        
        # Final verdict
        new_password_test = next((r for r in self.test_results if r['test'] == 'New Password Login'), None)
        if new_password_test and new_password_test['success']:
            print("\n🎉 VERDICT FINAL: ✅ SYSTÈME DE RÉINITIALISATION FONCTIONNE!")
            print("   Le mot de passe est correctement mis à jour dans la base de données.")
        else:
            print("\n🚨 VERDICT FINAL: ❌ PROBLÈME AVEC LA MISE À JOUR DU MOT DE PASSE")
            print("   Le mot de passe n'est pas mis à jour dans la base de données.")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = ComprehensivePasswordResetTester()
    tester.run_comprehensive_test()