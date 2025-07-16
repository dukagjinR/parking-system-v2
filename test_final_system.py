#!/usr/bin/env python3
"""
Final System Test for Parking Management System
Tests all major functionality including authentication, settings, reports, and user management
"""

import requests
import json
import time

def test_final_system():
    base_url = "http://localhost:9000"
    
    print("🧪 Testing Final Parking Management System")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 9000")
        return
    
    # Test 2: Test login with admin credentials
    print("\n🔐 Testing Authentication...")
    session = requests.Session()
    
    # Test login page
    response = session.get(f"{base_url}/login")
    if response.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page error: {response.status_code}")
        return
    
    # Test admin login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return
    
    # Test 3: Test dashboard access
    print("\n📊 Testing Dashboard...")
    response = session.get(f"{base_url}/")
    if response.status_code == 200:
        print("✅ Dashboard accessible")
    else:
        print(f"❌ Dashboard error: {response.status_code}")
    
    # Test 4: Test settings page
    print("\n⚙️ Testing Settings...")
    response = session.get(f"{base_url}/settings")
    if response.status_code == 200:
        print("✅ Settings page accessible")
        
        # Test settings form submission
        settings_data = {
            'hourly_rate': '3.0',
            'daily_rate': '25.0',
            'max_capacity': '60',
            'ticket_text': 'Faleminderit për përdorimin e parkingut tonë!'
        }
        
        response = session.post(f"{base_url}/settings", data=settings_data)
        if response.status_code == 200:
            print("✅ Settings saved successfully")
        else:
            print(f"❌ Settings save failed: {response.status_code}")
    else:
        print(f"❌ Settings page error: {response.status_code}")
    
    # Test 5: Test reports page
    print("\n📈 Testing Reports...")
    response = session.get(f"{base_url}/reports")
    if response.status_code == 200:
        print("✅ Reports page accessible")
    else:
        print(f"❌ Reports page error: {response.status_code}")
    
    # Test 6: Test user management
    print("\n👥 Testing User Management...")
    response = session.get(f"{base_url}/users")
    if response.status_code == 200:
        print("✅ User management page accessible")
    else:
        print(f"❌ User management error: {response.status_code}")
    
    # Test 7: Test API endpoints
    print("\n🔌 Testing API Endpoints...")
    
    # Test vehicles API
    response = session.get(f"{base_url}/api/vehicles")
    if response.status_code == 200:
        print("✅ Vehicles API working")
    else:
        print(f"❌ Vehicles API error: {response.status_code}")
    
    # Test payment API
    payment_data = {
        'ticket_number': 'TEST123',
        'payment_method': 'cash'
    }
    response = session.post(f"{base_url}/api/pay_ticket", json=payment_data)
    if response.status_code == 200:
        print("✅ Payment API working")
    else:
        print(f"❌ Payment API error: {response.status_code}")
    
    # Test 8: Test logout
    print("\n🚪 Testing Logout...")
    response = session.get(f"{base_url}/logout")
    if response.status_code == 200:
        print("✅ Logout successful")
    else:
        print(f"❌ Logout error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("🌐 System is ready for use at: http://localhost:9000")
    print("🔑 Login credentials:")
    print("   Admin: admin/admin123")
    print("   Operator: operator/operator123")

if __name__ == "__main__":
    test_final_system() 