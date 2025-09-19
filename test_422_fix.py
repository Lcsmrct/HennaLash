#!/usr/bin/env python3
"""
Focused Test for 422 Error Fix - Service Price Validation
Testing the specific fix for appointment creation with numeric prices
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "https://hennalash.onrender.com/api"
TIMEOUT = 10

class Service422Tester:
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
    
    def setup_authentication(self):
        """Setup admin and client authentication"""
        # Admin login
        try:
            response = requests.post(f"{BASE_URL}/login", json={
                "email": "admin@salon.com", "password": "admin123"
            }, timeout=TIMEOUT)
            if response.status_code == 200:
                self.admin_token = response.json()["access_token"]
                print("✅ Admin authenticated")
            else:
                print("❌ Admin authentication failed")
                return False
        except Exception as e:
            print(f"❌ Admin auth error: {e}")
            return False
        
        # Client login (create new one)
        try:
            import random
            email = f"test422_{random.randint(1000, 9999)}@email.com"
            
            # Register
            response = requests.post(f"{BASE_URL}/register", json={
                "email": email, "password": "test123",
                "first_name": "Test", "last_name": "User", "phone": "0123456789"
            }, timeout=TIMEOUT)
            
            if response.status_code == 200:
                # Login
                response = requests.post(f"{BASE_URL}/login", json={
                    "email": email, "password": "test123"
                }, timeout=TIMEOUT)
                if response.status_code == 200:
                    self.client_token = response.json()["access_token"]
                    print(f"✅ Client authenticated: {email}")
                    return True
            
            print("❌ Client authentication failed")
            return False
        except Exception as e:
            print(f"❌ Client auth error: {e}")
            return False
    
    def create_test_slots(self):
        """Create multiple test slots"""
        if not self.admin_token:
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        tomorrow = datetime.now() + timedelta(days=1)
        times = ["09:00", "10:00", "11:00", "14:00", "15:00"]
        
        for time_slot in times:
            try:
                response = requests.post(f"{BASE_URL}/slots", json={
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "time": time_slot
                }, headers=headers, timeout=TIMEOUT)
                # Don't worry about duplicates
            except:
                pass
        
        # Get available slots
        try:
            response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=TIMEOUT)
            if response.status_code == 200:
                self.available_slots = response.json()
                print(f"✅ Available slots: {len(self.available_slots)}")
                return len(self.available_slots) > 0
        except:
            pass
        
        return False
    
    def test_service_booking(self, service_name, service_price, expected_success=True):
        """Test booking with specific service and price"""
        if not self.client_token or not self.available_slots:
            return False
        
        # Get fresh slot
        try:
            response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=TIMEOUT)
            if response.status_code == 200:
                slots = response.json()
                if not slots:
                    self.log_result(f"Service {service_name}", False, "No available slots")
                    return False
                slot_id = slots[0]["id"]
            else:
                self.log_result(f"Service {service_name}", False, "Cannot get slots")
                return False
        except Exception as e:
            self.log_result(f"Service {service_name}", False, f"Slot fetch error: {e}")
            return False
        
        # Test appointment creation
        try:
            start_time = time.time()
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            appointment_data = {
                "slot_id": slot_id,
                "service_name": service_name,
                "service_price": service_price,
                "notes": f"Test booking for {service_name} - Price: {service_price}"
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
                self.log_result(
                    f"Service {service_name} ({service_price}€)", 
                    True, 
                    f"✅ SUCCESS - No 422 error! ID: {appointment.get('id', 'N/A')[:8]}...", 
                    duration
                )
                return True
            elif response.status_code == 422:
                error_detail = response.json().get('detail', 'Unknown error')
                self.log_result(
                    f"Service {service_name} ({service_price}€)", 
                    False, 
                    f"🚨 422 ERROR STILL EXISTS: {error_detail}", 
                    duration
                )
                return False
            else:
                self.log_result(
                    f"Service {service_name} ({service_price}€)", 
                    False, 
                    f"Unexpected status {response.status_code}: {response.text[:100]}", 
                    duration
                )
                return False
                
        except Exception as e:
            self.log_result(f"Service {service_name} ({service_price}€)", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_price_formats(self):
        """Test that invalid price formats are properly rejected"""
        if not self.client_token or not self.available_slots:
            return False
        
        # Test with string price (should fail with 422)
        try:
            response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=TIMEOUT)
            if response.status_code == 200:
                slots = response.json()
                if slots:
                    slot_id = slots[0]["id"]
                    
                    headers = {"Authorization": f"Bearer {self.client_token}"}
                    
                    # Test with string price
                    appointment_data = {
                        "slot_id": slot_id,
                        "service_name": "Test Service",
                        "service_price": "5€ par main",  # String instead of number
                        "notes": "Test with string price"
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/appointments",
                        json=appointment_data,
                        headers=headers,
                        timeout=TIMEOUT
                    )
                    
                    if response.status_code == 422:
                        self.log_result("Invalid Price Format", True, "✅ Correctly rejected string price with 422")
                        return True
                    else:
                        self.log_result("Invalid Price Format", False, f"Expected 422, got {response.status_code}")
                        return False
        except Exception as e:
            self.log_result("Invalid Price Format", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_test(self):
        """Run focused test on 422 error fix"""
        print("🎯 FOCUSED TEST: 422 ERROR FIX - SERVICE PRICE VALIDATION")
        print("=" * 70)
        print("Testing the fix: Services now send numeric prices instead of strings")
        print()
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed")
            return
        
        if not self.create_test_slots():
            print("❌ Slot creation failed")
            return
        
        print("\n🔥 TESTING ALL 4 SERVICES WITH NUMERIC PRICES:")
        print("-" * 50)
        
        # Test all 4 services with corrected numeric prices
        services = [
            ("Très simple", 5.0),
            ("Simple", 8.0),
            ("Chargé", 12.0),
            ("Mariée", 20.0)
        ]
        
        success_count = 0
        for service_name, price in services:
            if self.test_service_booking(service_name, price):
                success_count += 1
        
        print(f"\n📊 SERVICE BOOKING RESULTS: {success_count}/{len(services)} services working")
        
        print("\n🧪 TESTING INVALID PRICE FORMAT (Should be rejected):")
        print("-" * 50)
        self.test_invalid_price_formats()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 SUMMARY - 422 ERROR FIX VALIDATION")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ PASSED: {passed}/{total} tests")
        print(f"❌ FAILED: {total - passed}/{total} tests")
        
        if success_count == len(services):
            print("\n🎉 SUCCESS: All 4 services work with numeric prices!")
            print("✅ 422 error fix is WORKING correctly")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: {success_count}/{len(services)} services working")
            print("❌ Some services still have issues")
        
        # Show any failures
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("\n🚨 FAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['message']}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = Service422Tester()
    tester.run_focused_test()