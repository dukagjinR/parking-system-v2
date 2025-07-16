#!/usr/bin/env python3
"""
Quick test for web pages
"""

import requests

def test_pages():
    base_url = "http://localhost:9000"
    
    pages = [
        ('/', 'Dashboard'),
        ('/payment', 'Kabina e Pagesave'),
        ('/entry', 'Hyrja e Automjetit'),
        ('/exit', 'Dalja e Automjetit'),
        ('/settings', 'Cilësimet'),
        ('/reports', 'Raportet')
    ]
    
    print("🌐 Duke testuar faqet web...")
    
    for page, name in pages:
        try:
            response = requests.get(f"{base_url}{page}")
            if response.status_code == 200:
                print(f"✅ {name} - Faqja u ngarkua")
            else:
                print(f"❌ {name} - Gabim: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - Gabim: {e}")

if __name__ == "__main__":
    test_pages() 