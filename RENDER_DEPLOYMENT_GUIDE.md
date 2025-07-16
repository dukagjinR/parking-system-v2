
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
