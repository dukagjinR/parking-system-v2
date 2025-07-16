#!/usr/bin/env python3
"""
System Status Checker for Parking Management System
Verifies all components are working correctly
"""

import requests
import time
import sys

def check_server_status():
    """Check if the server is running and responding"""
    try:
        response = requests.get('http://localhost:9000', timeout=5)
        if response.status_code == 200:
            print("✅ Main Dashboard: http://localhost:9000")
            return True
        else:
            print(f"❌ Main Dashboard: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Main Dashboard: Connection failed - {e}")
        return False

def check_test_dashboard():
    """Check if the test dashboard is working"""
    try:
        response = requests.get('http://localhost:9000/test', timeout=5)
        if response.status_code == 200:
            print("✅ Test Dashboard: http://localhost:9000/test")
            return True
        else:
            print(f"❌ Test Dashboard: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Test Dashboard: Connection failed - {e}")
        return False

def check_api_endpoints():
    """Check if the test API endpoints are working"""
    endpoints = [
        '/test/api/barrier/entry',
        '/test/api/barrier/exit', 
        '/test/api/printer/ticket',
        '/test/api/printer/receipt',
        '/test/api/camera/capture',
        '/test/api/scan'
    ]
    
    working_endpoints = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:9000{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ API {endpoint}")
                working_endpoints += 1
            else:
                print(f"❌ API {endpoint}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ API {endpoint}: Connection failed")
    
    return working_endpoints == len(endpoints)

def main():
    print("🔍 Parking System Status Check")
    print("=" * 40)
    
    # Check if requests module is available
    try:
        import requests
    except ImportError:
        print("❌ requests module not available")
        print("Install with: pip install requests")
        return
    
    # Check server status
    main_ok = check_server_status()
    test_ok = check_test_dashboard()
    api_ok = check_api_endpoints()
    
    print("\n📊 Summary:")
    print("=" * 40)
    
    if main_ok and test_ok and api_ok:
        print("🎉 All systems operational!")
        print("\n🌐 Access your parking system at:")
        print("   Main Dashboard: http://localhost:9000")
        print("   Test Dashboard: http://localhost:9000/test")
        print("\n📋 Available features:")
        print("   - Vehicle entry/exit management")
        print("   - Mock hardware testing")
        print("   - Photo capture simulation")
        print("   - Ticket and receipt printing")
        print("   - Barrier control testing")
        print("   - Barcode scanning simulation")
    else:
        print("⚠️  Some components may not be working properly")
        if not main_ok:
            print("   - Main dashboard is not accessible")
        if not test_ok:
            print("   - Test dashboard is not accessible")
        if not api_ok:
            print("   - Some API endpoints are not responding")
        
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure the server is running: python run_test.py")
        print("   2. Check if port 9000 is available")
        print("   3. Verify all dependencies are installed")

if __name__ == "__main__":
    main() 