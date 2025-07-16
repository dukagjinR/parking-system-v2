#!/usr/bin/env python3
"""
Quick test to verify footer with fara.io trademark
"""

import requests

def test_footer():
    base_url = "http://localhost:9000"
    
    print("🧪 Testing Footer with fara.io trademark")
    print("=" * 50)
    
    # Test login page
    response = requests.get(f"{base_url}/login")
    if response.status_code == 200:
        content = response.text
        if "fara.io" in content:
            print("✅ Footer with fara.io trademark found in login page")
        else:
            print("❌ Footer with fara.io trademark not found in login page")
        
        if "Powered by" in content:
            print("✅ 'Powered by' text found")
        else:
            print("❌ 'Powered by' text not found")
            
        if "Secure Parking Management" in content:
            print("✅ Security text found")
        else:
            print("❌ Security text not found")
    else:
        print(f"❌ Login page error: {response.status_code}")

if __name__ == "__main__":
    test_footer() 