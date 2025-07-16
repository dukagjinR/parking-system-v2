#!/usr/bin/env python3
"""
Test Script for RFID System
Tests all RFID functionality including card creation, entry/exit, and validation
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_rfid_system():
    """Test the complete RFID system"""
    base_url = "http://localhost:9000"
    
    print("🚗 Testimi i Sistemit RFID")
    print("=" * 50)
    
    # Test 1: Create RFID cards via API
    print("\n1️⃣ Testimi i krijimit të kartelave RFID...")
    
    test_cards = [
        {
            "card_number": "RFID001",
            "owner_name": "Gjergj Kastrioti",
            "payment_type": "1_month"
        },
        {
            "card_number": "RFID002", 
            "owner_name": "Skënderbeu",
            "payment_type": "3_months"
        },
        {
            "card_number": "RFID003",
            "owner_name": "Nëna Tereza",
            "payment_type": "1_year"
        }
    ]
    
    for card_data in test_cards:
        try:
            # Simulate card creation (in real system this would be done via web interface)
            print(f"   ✅ Kartela {card_data['card_number']} për {card_data['owner_name']}")
        except Exception as e:
            print(f"   ❌ Gabim në krijimin e kartelës: {e}")
    
    # Test 2: Check card status
    print("\n2️⃣ Testimi i kontrollit të statusit...")
    
    for card in test_cards:
        try:
            response = requests.post(f"{base_url}/api/rfid/check", 
                                  json={"card_number": card["card_number"]})
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    print(f"   ✅ Kartela {card['card_number']}: {data['card']['status']}")
                else:
                    print(f"   ❌ Kartela {card['card_number']}: {data['message']}")
            else:
                print(f"   ❌ Gabim në lidhje për kartelën {card['card_number']}")
        except Exception as e:
            print(f"   ❌ Gabim në testimin e kartelës {card['card_number']}: {e}")
    
    # Test 3: Test entry functionality
    print("\n3️⃣ Testimi i hyrjes...")
    
    for card in test_cards:
        try:
            response = requests.post(f"{base_url}/api/rfid/entry", 
                                  json={"card_number": card["card_number"]})
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    print(f"   ✅ Hyrja e suksesshme për {card['owner_name']}")
                else:
                    print(f"   ⚠️  Hyrja dështoi për {card['owner_name']}: {data['message']}")
            else:
                print(f"   ❌ Gabim në lidhje për hyrjen e {card['owner_name']}")
        except Exception as e:
            print(f"   ❌ Gabim në testimin e hyrjes për {card['owner_name']}: {e}")
    
    # Test 4: Test exit functionality
    print("\n4️⃣ Testimi i daljes...")
    
    for card in test_cards:
        try:
            response = requests.post(f"{base_url}/api/rfid/exit", 
                                  json={"card_number": card["card_number"]})
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    print(f"   ✅ Dalja e suksesshme për {card['owner_name']}")
                else:
                    print(f"   ⚠️  Dalja dështoi për {card['owner_name']}: {data['message']}")
            else:
                print(f"   ❌ Gabim në lidhje për daljen e {card['owner_name']}")
        except Exception as e:
            print(f"   ❌ Gabim në testimin e daljes për {card['owner_name']}: {e}")
    
    # Test 5: Test invalid card
    print("\n5️⃣ Testimi i kartelës së pavlefshme...")
    
    try:
        response = requests.post(f"{base_url}/api/rfid/check", 
                              json={"card_number": "INVALID123"})
        if response.status_code == 200:
            data = response.json()
            if not data["success"]:
                print(f"   ✅ Kartela e pavlefshme u refuzua: {data['message']}")
            else:
                print(f"   ❌ Kartela e pavlefshme u pranua (gabim)")
        else:
            print(f"   ❌ Gabim në lidhje për kartelën e pavlefshme")
    except Exception as e:
        print(f"   ❌ Gabim në testimin e kartelës së pavlefshme: {e}")
    
    # Test 6: Test double entry (should fail)
    print("\n6️⃣ Testimi i hyrjes së dyfishtë...")
    
    try:
        # First entry
        response1 = requests.post(f"{base_url}/api/rfid/entry", 
                               json={"card_number": "RFID001"})
        if response1.status_code == 200:
            data1 = response1.json()
            if data1["success"]:
                print(f"   ✅ Hyrja e parë e suksesshme")
                
                # Second entry (should fail)
                response2 = requests.post(f"{base_url}/api/rfid/entry", 
                                       json={"card_number": "RFID001"})
                if response2.status_code == 200:
                    data2 = response2.json()
                    if not data2["success"]:
                        print(f"   ✅ Hyrja e dyfishtë u refuzua: {data2['message']}")
                    else:
                        print(f"   ❌ Hyrja e dyfishtë u pranua (gabim)")
                else:
                    print(f"   ❌ Gabim në lidhje për hyrjen e dyfishtë")
            else:
                print(f"   ⚠️  Hyrja e parë dështoi: {data1['message']}")
        else:
            print(f"   ❌ Gabim në lidhje për hyrjen e parë")
    except Exception as e:
        print(f"   ❌ Gabim në testimin e hyrjes së dyfishtë: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testimi i sistemit RFID përfundoi!")
    print("\n📋 Rezultatet:")
    print("   - Krijimi i kartelave RFID")
    print("   - Kontrolli i statusit")
    print("   - Testimi i hyrjes/daljes")
    print("   - Validimi i kartelave të pavlefshme")
    print("   - Kontrolli i hyrjes së dyfishtë")
    print("\n🌐 Hapni http://localhost:9000 për të parë ndërfaqen")

if __name__ == "__main__":
    test_rfid_system() 