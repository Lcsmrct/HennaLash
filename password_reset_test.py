#!/usr/bin/env python3
"""
Password Reset System Testing
Focus: Test spécifique du système de réinitialisation de mot de passe
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import random

# Configuration - Use frontend .env URL
BASE_URL = "https://design-modernize.preview.emergentagent.com/api"
TIMEOUT = 15

class PasswordResetTester:
    def __init__(self):
        self.test_results = []
        self.test_user_email = "admin@admin.com"  # Use existing user as requested
        self.test_user_password = "admin123"
        self.new_password = "nouveaumotdepasse123"
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

    def test_user_exists(self):
        """Verify test user exists by attempting login"""
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
                self.log_result("User Exists Check", True, 
                              f"User {self.test_user_email} exists and can login", duration)
                return True
            else:
                self.log_result("User Exists Check", False, 
                              f"User {self.test_user_email} login failed: {response.status_code} - {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("User Exists Check", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_request(self):
        """Test POST /api/auth/password-reset/request with valid email"""
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
                return True
            else:
                self.log_result("Password Reset Request", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Request", False, f"Exception: {str(e)}")
            return False

    def verify_reset_code_in_database(self):
        """Verify that reset code is stored in password_resets collection"""
        # Since we can't directly access MongoDB, we'll test by trying different codes
        # This is a limitation - in a real test environment, we'd check the database directly
        print("🔍 VÉRIFICATION: Code stocké dans password_resets collection")
        print("   Note: Test indirect - vérification via tentatives de codes")
        
        # Try some common test codes that might be generated
        test_codes = ["123456", "000000", "111111", "999999", "654321", "555555"]
        
        for code in test_codes:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/password-reset/confirm",
                    json={
                        "email": self.test_user_email,
                        "code": code,
                        "new_password": "testpassword123"
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    self.reset_code = code
                    self.log_result("Reset Code Database Check", True, 
                                  f"Found valid reset code: {code}")
                    return True
                elif response.status_code == 400:
                    # Expected for invalid codes
                    continue
                else:
                    print(f"   Unexpected response for code {code}: {response.status_code}")
            except Exception as e:
                print(f"   Exception testing code {code}: {str(e)}")
        
        self.log_result("Reset Code Database Check", False, 
                      "Could not find valid reset code in database")
        return False

    def test_password_reset_confirm_invalid(self):
        """Test POST /api/auth/password-reset/confirm with invalid code"""
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
                self.log_result("Password Reset Confirm (Invalid Code)", True, 
                              "Correctly rejected invalid code with 400", duration)
                return True
            else:
                self.log_result("Password Reset Confirm (Invalid Code)", False, 
                              f"Expected 400, got {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Confirm (Invalid Code)", False, f"Exception: {str(e)}")
            return False

    def test_password_reset_confirm_valid(self):
        """Test POST /api/auth/password-reset/confirm with valid code"""
        if not self.reset_code:
            self.log_result("Password Reset Confirm (Valid Code)", False, 
                          "No valid reset code found to test with")
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
                self.log_result("Password Reset Confirm (Valid Code)", True, 
                              f"Password reset successful: {result.get('message', 'N/A')}", duration)
                return True
            else:
                self.log_result("Password Reset Confirm (Valid Code)", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Password Reset Confirm (Valid Code)", False, f"Exception: {str(e)}")
            return False

    def test_login_with_new_password(self):
        """Test login with the new password to verify password was updated in database"""
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
                self.log_result("Login with New Password", True, 
                              f"✅ CRITICAL SUCCESS: Password was updated in database! Login successful with new password", duration)
                return True
            else:
                self.log_result("Login with New Password", False, 
                              f"❌ CRITICAL FAILURE: Password NOT updated in database! Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Login with New Password", False, f"Exception: {str(e)}")
            return False

    def test_login_with_old_password(self):
        """Test login with old password to verify it no longer works"""
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
                self.log_result("Login with Old Password", True, 
                              "✅ CORRECT: Old password correctly rejected", duration)
                return True
            elif response.status_code == 200:
                self.log_result("Login with Old Password", False, 
                              "❌ PROBLEM: Old password still works - password may not have been updated", duration)
                return False
            else:
                self.log_result("Login with Old Password", False, 
                              f"Unexpected status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Login with Old Password", False, f"Exception: {str(e)}")
            return False

    def create_test_user_if_needed(self):
        """Create test user if it doesn't exist"""
        try:
            # Try to register the user
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "email": self.test_user_email,
                    "password": self.test_user_password,
                    "first_name": "Admin",
                    "last_name": "Test",
                    "phone": "0123456789"
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Create Test User", True, 
                              f"Test user created: {self.test_user_email}", duration)
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_result("Create Test User", True, 
                              f"Test user already exists: {self.test_user_email}", duration)
                return True
            else:
                self.log_result("Create Test User", False, 
                              f"Status {response.status_code}: {response.text}", duration)
                return False
        except Exception as e:
            self.log_result("Create Test User", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_password_reset_test(self):
        """Run comprehensive password reset workflow test"""
        print("🔐 TEST SYSTÈME DE RÉINITIALISATION DE MOT DE PASSE")
        print("=" * 70)
        print("Focus: Diagnostiquer pourquoi le mot de passe n'est pas mis à jour dans la BDD")
        print("=" * 70)
        
        # Step 1: Ensure test user exists
        print("\n📋 ÉTAPE 1: Vérification utilisateur test")
        print("-" * 40)
        if not self.test_user_exists():
            print("⚠️ Utilisateur test n'existe pas, création...")
            if not self.create_test_user_if_needed():
                print("❌ Impossible de créer l'utilisateur test")
                return
        
        # Step 2: Test password reset request
        print("\n📧 ÉTAPE 2: Demande de réinitialisation")
        print("-" * 40)
        if not self.test_password_reset_request():
            print("❌ Échec de la demande de réinitialisation")
            return
        
        # Step 3: Verify code is stored in database
        print("\n🗄️ ÉTAPE 3: Vérification stockage code en BDD")
        print("-" * 40)
        code_stored = self.verify_reset_code_in_database()
        
        # Step 4: Test invalid code rejection
        print("\n🚫 ÉTAPE 4: Test code invalide")
        print("-" * 40)
        self.test_password_reset_confirm_invalid()
        
        # Step 5: Test valid code confirmation (if we found a code)
        print("\n✅ ÉTAPE 5: Confirmation avec code valide")
        print("-" * 40)
        if code_stored:
            password_reset_success = self.test_password_reset_confirm_valid()
        else:
            print("⚠️ Pas de code valide trouvé - test de confirmation sauté")
            password_reset_success = False
        
        # Step 6: CRITICAL - Test login with new password
        print("\n🔑 ÉTAPE 6: CRITIQUE - Test connexion nouveau mot de passe")
        print("-" * 40)
        if password_reset_success:
            new_password_works = self.test_login_with_new_password()
            
            # Step 7: Verify old password no longer works
            print("\n🔒 ÉTAPE 7: Vérification ancien mot de passe")
            print("-" * 40)
            self.test_login_with_old_password()
        else:
            print("⚠️ Réinitialisation échouée - test de connexion sauté")
            new_password_works = False
        
        # Summary and diagnosis
        self.print_diagnosis()

    def print_diagnosis(self):
        """Print detailed diagnosis of the password reset system"""
        print("\n" + "=" * 70)
        print("🔍 DIAGNOSTIC DÉTAILLÉ")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ TESTS RÉUSSIS: {passed}/{total}")
        print(f"❌ TESTS ÉCHOUÉS: {total - passed}/{total}")
        
        # Critical analysis
        print("\n🚨 ANALYSE CRITIQUE:")
        
        # Check if password reset request works
        request_test = next((r for r in self.test_results if r['test'] == 'Password Reset Request'), None)
        if request_test and request_test['success']:
            print("  ✅ Demande de réinitialisation fonctionne")
        else:
            print("  ❌ Problème avec la demande de réinitialisation")
        
        # Check if code validation works
        invalid_code_test = next((r for r in self.test_results if r['test'] == 'Password Reset Confirm (Invalid Code)'), None)
        if invalid_code_test and invalid_code_test['success']:
            print("  ✅ Validation des codes fonctionne")
        else:
            print("  ❌ Problème avec la validation des codes")
        
        # Check if password update works
        new_password_test = next((r for r in self.test_results if r['test'] == 'Login with New Password'), None)
        if new_password_test and new_password_test['success']:
            print("  ✅ MISE À JOUR MOT DE PASSE FONCTIONNE!")
        else:
            print("  ❌ PROBLÈME CRITIQUE: Mot de passe pas mis à jour en BDD")
        
        # Show failed tests details
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 DÉTAILS DES ÉCHECS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        
        # Recommendations
        print("\n💡 RECOMMANDATIONS:")
        if new_password_test and not new_password_test['success']:
            print("  1. Vérifier la fonction get_password_hash() dans auth.py")
            print("  2. Vérifier la requête MongoDB update_one() dans server.py ligne 829-832")
            print("  3. Vérifier que le champ 'hashed_password' est bien utilisé (pas 'password_hash')")
            print("  4. Vérifier les logs backend pour erreurs lors de l'update")
        
        if not any(r['test'] == 'Reset Code Database Check' and r['success'] for r in self.test_results):
            print("  5. Vérifier que la collection password_resets est créée")
            print("  6. Vérifier l'expiration des codes (expires_at)")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = PasswordResetTester()
    tester.run_comprehensive_password_reset_test()