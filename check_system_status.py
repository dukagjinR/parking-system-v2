#!/usr/bin/env python3
"""
Simple System Status Checker
Checks if the parking system is running and accessible
"""

import requests
import time
import sys

def check_system():
    """Check if the system is running"""
    print("🔍 Kontrollimi i statusit të sistemit...")
    
    try:
        # Try to connect to the main page
        response = requests.get("http://localhost:9000", timeout=5)
        
        if response.status_code == 200:
            print("✅ Sistemi është duke punuar!")
            print("🌐 Hapni http://localhost:9000 për të përdorur sistemin")
            print("👤 Admin: admin/admin123")
            print("👤 Operator: operator/operator123")
            return True
        else:
            print(f"⚠️  Sistemi është duke punuar por ka probleme (Status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Sistemi nuk është duke punuar")
        print("🚀 Ekzekutoni: python app.py")
        return False
    except Exception as e:
        print(f"❌ Gabim në kontrollin: {e}")
        return False

def main():
    print("🚗 Parking System Status Checker")
    print("=" * 40)
    
    # Wait a bit for system to start
    print("⏳ Duke pritur 3 sekonda...")
    time.sleep(3)
    
    success = check_system()
    
    if success:
        print("\n🎉 Sistemi është gati për përdorim!")
    else:
        print("\n🔧 Nëse ka probleme, ekzekutoni:")
        print("   1. python auto_fix_system.py")
        print("   2. python app.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 