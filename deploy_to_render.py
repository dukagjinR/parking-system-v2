#!/usr/bin/env python3
"""
Deploy to Render.com Helper Script
This script helps with deploying the parking system to Render.com
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_render_requirements():
    """Check if all requirements for Render.com deployment are met"""
    print("🔍 Kontrollimi i kërkesave për Render.com...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'render.yaml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Skedarët e munguar:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Të gjitha skedarët e nevojshëm janë të pranishëm")
    return True

def create_render_deployment_guide():
    """Create a deployment guide for Render.com"""
    guide = """
# 🚀 UDHËZIMI PËR DEPLOY NË RENDER.COM

## Hapat për të bërë deploy sistemin online:

### 1. Krijo një llogari në Render.com
- Shko në https://render.com
- Kliko "Get Started" ose "Sign Up"
- Regjistrohu me email-in tënd
- Lidh llogarinë tënde GitHub

### 2. Krijo një Web Service
- Në dashboard-in e Render.com, kliko "New +"
- Zgjidh "Web Service"
- Lidh repository-n tënd: `dukagjinR/parking-system`
- Zgjidh branch: `main`

### 3. Konfigurimi i Web Service
- **Name:** `parking-system` (ose çfarëdo emri)
- **Environment:** `Python 3`
- **Region:** Zgjidh më të afërtin (p.sh. Frankfurt)
- **Branch:** `main`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --config gunicorn_config.py`

### 4. Deploy
- Kliko "Create Web Service"
- Render.com do të shkarkojë kodin dhe do ta deploy-oj automatikisht
- Do të marrësh një URL si: `https://parking-system-xxxx.onrender.com`

### 5. Testimi
- Hap linkun që të dha Render.com
- Testo login-in: admin/admin123 ose operator/operator123
- Testo të gjitha funksionet

## 🔗 Linku për klientin
Pasi të jetë gati, do të marrësh një link si:
`https://parking-system-xxxx.onrender.com`

Ky link mund ta dërgosh klientit për testim.

## 📋 Informacion për klientin
- **Link:** [Linku që do të marrësh nga Render.com]
- **Admin:** admin/admin123
- **Operator:** operator/operator123
- **Funksionet:** Hyrje/dalje, pagesa, RFID, raporte

## ⚠️ Shënim
- Kodi mbetet privat në GitHub
- Vetëm platforma është e qasshme online
- Klienti sheh vetëm ndërfaqen web, jo kodin
"""
    
    with open('RENDER_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Udhëzimi u ruajt në RENDER_DEPLOYMENT_GUIDE.md")

def main():
    print("🚗 Parking System - Deploy to Render.com")
    print("=" * 50)
    
    # Check requirements
    if not check_render_requirements():
        print("\n❌ Ju lutem rregulloni skedarët e munguar para se të vazhdoni")
        return
    
    # Create deployment guide
    create_render_deployment_guide()
    
    print("\n✅ Gjithçka është gati për deploy!")
    print("\n📋 Hapat e ardhshëm:")
    print("1. Hap https://render.com")
    print("2. Regjistrohu dhe lidh GitHub")
    print("3. Krijo Web Service")
    print("4. Konfiguro siç është në udhëzimin")
    print("5. Deploy dhe testo")
    
    print("\n📖 Udhëzimi i plotë u ruajt në RENDER_DEPLOYMENT_GUIDE.md")
    print("\n🎯 Pasi të jetë gati, do të marrësh linkun për klientin!")

if __name__ == "__main__":
    main() 