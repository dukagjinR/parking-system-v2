#!/usr/bin/env python3
"""
Web System Tester for Parking Management System
Automatically tests all web pages and reports issues
"""

import requests
import time
import sys
from datetime import datetime

def test_web_system():
    """Test the complete web system"""
    base_url = "http://localhost:9000"
    
    print("🌐 Testimi i Sistemit Web")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Duke pritur që serveri të startojë...")
    time.sleep(5)
    
    # Test endpoints
    endpoints = [
        ('/', 'Dashboard'),
        ('/login', 'Login'),
        ('/settings', 'Settings'),
        ('/reports', 'Reports'),
        ('/rfid_cards', 'RFID Cards'),
        ('/rfid_test', 'RFID Test'),
        ('/users', 'Users'),
        ('/payment', 'Payment'),
        ('/entry', 'Entry'),
        ('/exit', 'Exit')
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        try:
            print(f"\n🔍 Testimi i {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
                results.append((name, True, "OK"))
            elif response.status_code == 302:  # Redirect (login required)
                print(f"⚠️  {name}: Redirect (302) - login required")
                results.append((name, True, "Redirect"))
            elif response.status_code == 404:
                print(f"❌ {name}: Not Found (404)")
                results.append((name, False, "Not Found"))
            else:
                print(f"❌ {name}: Error ({response.status_code})")
                results.append((name, False, f"Error {response.status_code}"))
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Nuk mund të lidhet me serverin")
            results.append((name, False, "Connection Error"))
        except requests.exceptions.Timeout:
            print(f"❌ {name}: Timeout")
            results.append((name, False, "Timeout"))
        except Exception as e:
            print(f"❌ {name}: Gabim - {e}")
            results.append((name, False, str(e)))
    
    # Test API endpoints
    print("\n🔍 Testimi i API endpoints...")
    api_endpoints = [
        ('/api/vehicles', 'Vehicles API'),
        ('/api/rfid/check', 'RFID Check API'),
    ]
    
    for endpoint, name in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code in [200, 401, 403]:  # OK or auth required
                print(f"✅ {name}: OK")
                results.append((name, True, "OK"))
            else:
                print(f"❌ {name}: Error ({response.status_code})")
                results.append((name, False, f"Error {response.status_code}"))
        except Exception as e:
            print(f"❌ {name}: Gabim - {e}")
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REZULTATET E TESTIT")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for name, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")
        if success:
            successful += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📈 Total: {len(results)}")
    print(f"✅ Sukses: {successful}")
    print(f"❌ Dështuar: {failed}")
    
    if failed == 0:
        print("\n🎉 Sistemi web funksionon perfektisht!")
        print("🌐 Hapni http://localhost:9000 për të përdorur sistemin")
    elif failed <= 2:
        print("\n⚠️  Sistemi funksionon me probleme të vogla")
        print("🔧 Kontrolloni log-et për detaje")
    else:
        print("\n❌ Sistemi ka probleme të mëdha")
        print("🔧 Ekzekutoni auto_fix_system.py për të rregulluar")
    
    return failed == 0

def test_database_connection():
    """Test database connection"""
    print("\n🗄️  Testimi i lidhjes me databazën...")
    
    try:
        from app import app, db
        with app.app_context():
            # Test basic database operations
            db.engine.execute('SELECT 1')
            print("✅ Lidhja me databazën është OK")
            return True
    except Exception as e:
        print(f"❌ Gabim në databazë: {e}")
        return False

def main():
    """Main function"""
    print("🚗 Parking System Web Tester")
    print("=" * 50)
    
    # Test database first
    db_ok = test_database_connection()
    
    if not db_ok:
        print("❌ Problemet me databazën parandalojnë testimin e web")
        print("🔧 Ekzekutoni auto_fix_system.py")
        return False
    
    # Test web system
    web_ok = test_web_system()
    
    if web_ok:
        print("\n🎯 Sistemi është gati për përdorim!")
        print("👤 Përdoruesi Admin: admin/admin123")
        print("👤 Përdoruesi Operator: operator/operator123")
    else:
        print("\n⚠️  Ka probleme që duhen rregulluar")
    
    return web_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 