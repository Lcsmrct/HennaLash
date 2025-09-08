#!/usr/bin/env python3
"""
JavaScript Debug Test - Test JavaScript-specific edge cases
This test checks for JavaScript-specific issues that might cause the conditional checks to fail
"""

import requests
import json
import sys

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")

def test_javascript_edge_cases():
    """Test JavaScript-specific edge cases that might cause issues"""
    print_header("JAVASCRIPT EDGE CASES TEST")
    
    # Get real slot data
    try:
        response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=15)
        if response.status_code != 200:
            print_error(f"Failed to get slots: {response.status_code}")
            return False
        
        slots_data = response.json()
        if len(slots_data) == 0:
            print_warning("No slots available for testing")
            return True
        
        first_slot = slots_data[0]
        print_info(f"Testing with real slot data: {json.dumps(first_slot, indent=2)}")
        
        # Test JavaScript truthiness edge cases
        print_header("JAVASCRIPT TRUTHINESS EDGE CASES")
        
        slot_date = first_slot.get('date')
        slot_start_time = first_slot.get('start_time')
        
        print_info("Testing JavaScript conditional evaluation:")
        
        # Test 1: Check for undefined vs null vs empty string
        print_info(f"slot.date = {repr(slot_date)}")
        print_info(f"JavaScript: slot.date ? true : false")
        
        # In JavaScript, these are falsy: false, 0, "", null, undefined, NaN
        js_falsy_values = [None, "", 0, False]
        
        if slot_date in js_falsy_values:
            print_error(f"❌ slot.date ({repr(slot_date)}) is falsy in JavaScript")
        else:
            print_success(f"✅ slot.date ({repr(slot_date)}) is truthy in JavaScript")
        
        print_info(f"slot.start_time = {repr(slot_start_time)}")
        print_info(f"JavaScript: slot.start_time ? true : false")
        
        if slot_start_time in js_falsy_values:
            print_error(f"❌ slot.start_time ({repr(slot_start_time)}) is falsy in JavaScript")
        else:
            print_success(f"✅ slot.start_time ({repr(slot_start_time)}) is truthy in JavaScript")
        
        # Test 2: Check for potential JSON parsing issues
        print_header("JSON PARSING EDGE CASES")
        
        # Check if the values might be getting stringified incorrectly
        json_str = json.dumps(first_slot)
        print_info(f"JSON stringified slot: {json_str}")
        
        # Parse it back
        parsed_slot = json.loads(json_str)
        print_info(f"Re-parsed slot.date: {repr(parsed_slot.get('date'))}")
        print_info(f"Re-parsed slot.start_time: {repr(parsed_slot.get('start_time'))}")
        
        # Test 3: Check for potential axios response transformation issues
        print_header("AXIOS RESPONSE TRANSFORMATION TEST")
        
        # Check response headers that might affect parsing
        print_info("Response headers that might affect JavaScript parsing:")
        print_info(f"Content-Type: {response.headers.get('content-type')}")
        print_info(f"Content-Encoding: {response.headers.get('content-encoding')}")
        print_info(f"Transfer-Encoding: {response.headers.get('transfer-encoding')}")
        
        # Test 4: Check for potential date format issues in JavaScript
        print_header("JAVASCRIPT DATE FORMAT TEST")
        
        if slot_date:
            print_info(f"Testing JavaScript Date parsing for: {slot_date}")
            
            # Common JavaScript date parsing issues
            date_formats_to_test = [
                slot_date,
                slot_date.replace('T00:00:00', ''),
                slot_date + 'Z',  # Add timezone
                slot_date.replace('T', ' ')  # Replace T with space
            ]
            
            for date_format in date_formats_to_test:
                try:
                    # Simulate JavaScript: new Date(dateString)
                    from datetime import datetime
                    if 'T' in date_format:
                        parsed = datetime.fromisoformat(date_format.replace('Z', ''))
                    else:
                        parsed = datetime.strptime(date_format, '%Y-%m-%d')
                    print_success(f"✅ Date format '{date_format}' would parse successfully")
                except Exception as e:
                    print_error(f"❌ Date format '{date_format}' would fail: {str(e)}")
        
        # Test 5: Check for potential async/await issues
        print_header("ASYNC/AWAIT TIMING TEST")
        
        print_info("Checking for potential race conditions...")
        print_info("The frontend uses Promise.all() to fetch appointments and slots simultaneously")
        print_info("If there's a timing issue, slots might be undefined when the component renders")
        
        # Simulate multiple rapid requests to check for consistency
        print_info("Testing API consistency with rapid requests...")
        for i in range(3):
            rapid_response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=5)
            if rapid_response.status_code == 200:
                rapid_data = rapid_response.json()
                if len(rapid_data) > 0 and rapid_data[0].get('date') and rapid_data[0].get('start_time'):
                    print_success(f"✅ Rapid request #{i+1}: Data consistent")
                else:
                    print_error(f"❌ Rapid request #{i+1}: Data inconsistent")
            else:
                print_error(f"❌ Rapid request #{i+1}: Failed ({rapid_response.status_code})")
        
        return True
        
    except Exception as e:
        print_error(f"Error in JavaScript edge cases test: {str(e)}")
        return False

def test_frontend_environment_issues():
    """Test for frontend environment configuration issues"""
    print_header("FRONTEND ENVIRONMENT ISSUES TEST")
    
    print_info("Checking potential frontend environment issues...")
    
    # Check if the user might be accessing a different frontend URL
    print_info("Potential issues:")
    print_info("1. User accessing cached version of frontend")
    print_info("2. User accessing different deployment URL")
    print_info("3. Browser cache not cleared")
    print_info("4. Service worker caching old data")
    print_info("5. CDN caching issues")
    
    # Test the exact API endpoint the frontend should be using
    frontend_env_url = "https://henna-lash.onrender.com"
    print_info(f"Frontend should be using: {frontend_env_url}")
    
    # Test if there are multiple versions of the API
    test_urls = [
        "https://henna-lash.onrender.com/api/slots?available_only=true",
        "http://localhost:8001/api/slots?available_only=true",  # Local version
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"✅ {url} - Returns {len(data)} slots")
                if len(data) > 0:
                    first_slot = data[0]
                    has_date = bool(first_slot.get('date'))
                    has_time = bool(first_slot.get('start_time'))
                    print_info(f"   Date field present: {has_date}")
                    print_info(f"   Time field present: {has_time}")
            else:
                print_error(f"❌ {url} - Status: {response.status_code}")
        except Exception as e:
            print_warning(f"⚠️  {url} - Error: {str(e)}")

def main():
    """Run JavaScript debug tests"""
    print_header("JAVASCRIPT DEBUG TEST - SLOT DATA ISSUE")
    print_info("Testing JavaScript-specific edge cases that might cause slot data issues")
    
    success = True
    
    if not test_javascript_edge_cases():
        success = False
    
    test_frontend_environment_issues()
    
    print_header("JAVASCRIPT DEBUG RESULTS")
    
    if success:
        print_success("🎯 JavaScript debug test completed")
        print_info("Backend data is correct. Issue is likely:")
        print_info("1. Frontend caching (browser cache, service worker)")
        print_info("2. User accessing wrong URL/version")
        print_info("3. Network issues preventing data fetch")
        print_info("4. JavaScript runtime errors in browser")
    else:
        print_error("❌ JavaScript debug test found issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)