#!/usr/bin/env python3
"""
Frontend Simulation Test - Simulate exactly how frontend processes slot data
This test simulates the JavaScript processing to identify the exact issue
"""

import requests
import json
from datetime import datetime
import sys

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")

def simulate_frontend_processing():
    """Simulate exactly how the frontend processes slot data"""
    print_header("FRONTEND SIMULATION TEST")
    print_info("Simulating ClientDashboard.jsx slot processing...")
    
    # Get slots data exactly like frontend does
    try:
        response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=15)
        if response.status_code != 200:
            print_error(f"Failed to get slots: {response.status_code}")
            return False
        
        slots_data = response.json()
        print_success(f"Retrieved {len(slots_data)} available slots")
        
        if len(slots_data) == 0:
            print_warning("No slots available for testing")
            return True
        
        # Test first few slots
        for i, slot in enumerate(slots_data[:3]):
            print_header(f"TESTING SLOT #{i+1}")
            print_info(f"Raw slot data: {json.dumps(slot, indent=2)}")
            
            # Simulate frontend checks
            print_info("Simulating frontend conditional checks:")
            
            # Check slot.date (line 250 in ClientDashboard.jsx)
            slot_date = slot.get('date')
            print_info(f"slot.date = {repr(slot_date)}")
            print_info(f"slot.date type = {type(slot_date)}")
            print_info(f"bool(slot.date) = {bool(slot_date)}")
            
            if slot_date:
                print_success("✅ slot.date is truthy - formatDate() will be called")
                # Simulate formatDate function
                try:
                    # This simulates: new Date(dateString).toLocaleDateString('fr-FR', {...})
                    parsed_date = datetime.fromisoformat(slot_date.replace('T00:00:00', ''))
                    formatted_date = parsed_date.strftime('%A %d %B %Y')  # Approximate French format
                    print_success(f"✅ formatDate() would return: {formatted_date}")
                except Exception as e:
                    print_error(f"❌ formatDate() would fail: {str(e)}")
            else:
                print_error("❌ slot.date is falsy - 'Date non spécifiée' will be shown")
            
            # Check slot.start_time (line 254 in ClientDashboard.jsx)
            slot_start_time = slot.get('start_time')
            print_info(f"slot.start_time = {repr(slot_start_time)}")
            print_info(f"slot.start_time type = {type(slot_start_time)}")
            print_info(f"bool(slot.start_time) = {bool(slot_start_time)}")
            
            if slot_start_time:
                print_success("✅ slot.start_time is truthy - formatTime() will be called")
                # Simulate formatTime function
                try:
                    # This simulates: new Date(`2000-01-01T${timeString}`).toLocaleTimeString('fr-FR', {...})
                    time_parts = slot_start_time.split(':')
                    formatted_time = f"{time_parts[0]}:{time_parts[1]}"
                    print_success(f"✅ formatTime() would return: {formatted_time}")
                except Exception as e:
                    print_error(f"❌ formatTime() would fail: {str(e)}")
            else:
                print_error("❌ slot.start_time is falsy - 'Heure non spécifiée' will be shown")
            
            print_info("-" * 60)
        
        return True
        
    except Exception as e:
        print_error(f"Error in frontend simulation: {str(e)}")
        return False

def test_javascript_truthiness():
    """Test JavaScript-like truthiness for common values"""
    print_header("JAVASCRIPT TRUTHINESS TEST")
    print_info("Testing how different values would be evaluated in JavaScript conditionals...")
    
    test_values = [
        None,
        "",
        "0",
        0,
        "2025-09-08T00:00:00",
        "20:57",
        False,
        True,
        [],
        {},
        "null",
        "undefined"
    ]
    
    for value in test_values:
        js_truthy = bool(value) and value != "" and value != 0 and value != "0"
        print_info(f"{repr(value)} -> JavaScript truthy: {js_truthy}")

def analyze_api_response_structure():
    """Analyze the exact structure of API response"""
    print_header("API RESPONSE STRUCTURE ANALYSIS")
    
    try:
        response = requests.get(f"{BASE_URL}/slots?available_only=true", timeout=15)
        if response.status_code != 200:
            print_error(f"Failed to get slots: {response.status_code}")
            return False
        
        # Check raw response
        print_info("Raw response headers:")
        for key, value in response.headers.items():
            print_info(f"  {key}: {value}")
        
        print_info(f"Response status: {response.status_code}")
        print_info(f"Response content type: {response.headers.get('content-type')}")
        
        # Parse JSON
        slots_data = response.json()
        print_info(f"Parsed JSON type: {type(slots_data)}")
        print_info(f"Number of slots: {len(slots_data)}")
        
        if len(slots_data) > 0:
            first_slot = slots_data[0]
            print_info("First slot keys and types:")
            for key, value in first_slot.items():
                print_info(f"  {key}: {type(value).__name__} = {repr(value)}")
        
        return True
        
    except Exception as e:
        print_error(f"Error analyzing API response: {str(e)}")
        return False

def main():
    """Run all frontend simulation tests"""
    print_header("FRONTEND SLOT DATA ISSUE DIAGNOSIS")
    print_info("Simulating exact frontend behavior to identify the root cause")
    print_info("of 'Date non spécifiée' and 'Heure non spécifiée' messages")
    
    success = True
    
    # Test 1: Analyze API response structure
    if not analyze_api_response_structure():
        success = False
    
    # Test 2: Test JavaScript truthiness
    test_javascript_truthiness()
    
    # Test 3: Simulate frontend processing
    if not simulate_frontend_processing():
        success = False
    
    print_header("DIAGNOSIS RESULTS")
    if success:
        print_success("🎯 Frontend simulation completed successfully")
        print_info("Check the output above to identify why dates/times show as 'non spécifiée'")
    else:
        print_error("❌ Frontend simulation encountered errors")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)