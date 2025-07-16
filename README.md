# 🚗 Parking Management System

Sistemi i menaxhimit të parkingut me ndërfaqe web në shqip, i krijuar për menaxhimin e automjeteve, biletave, pagesave dhe kartelave RFID.

## 🌟 Karakteristikat

- **Menaxhimi i automjeteve** - Hyrje/dalje me fotografi
- **Sistemi i biletave** - Printimi automatik me QR kode
- **Pagesa online** - Verifikimi dhe pagesa e biletave
- **Kartela RFID** - Menaxhimi i kartelave me kohëzgjatje
- **Raporte** - Statistikat dhe raportet e parkingut
- **Autentifikimi** - Role-based access (admin/operator)
- **Testimi i hardware** - Simulimi i printerit, kamerës, barrierave

## 🚀 Instalimi

### Kërkesat
- Python 3.7+
- Flask
- SQLAlchemy
- Pillow (për fotografi)

### Hapat e instalimit

1. **Klononi repozitorin:**
```bash
git clone https://github.com/dukagjinR/parking-system.git
cd parking-system
```

2. **Instaloni varësitë:**
```bash
pip install -r requirements.txt
```

3. **Startoni sistemin:**
```bash
python app.py
```

4. **Hapni në browser:**
```
http://localhost:9000
```

## 👤 Përdorimi

### Kredencialet e paracaktuara
- **Admin:** `admin` / `admin123`
- **Operator:** `operator` / `operator123`

### Funksionet kryesore

#### 🚪 Hyrja e automjeteve
- Shtypni butonin për të hapur barrierën
- Automjeti fotografohet automatikisht
- Bileta printohet me QR kod

#### 🚪 Dalja e automjeteve
- Skanoni QR kodin e biletës
- Verifikoni pagesën
- Hapni barrierën e daljes

#### 💳 Sistemi RFID
- Menaxhoni kartela RFID
- Vendosni kohëzgjatje (1 muaj, 1 vit, etj.)
- Kontrolloni statusin e kartelave

#### 📊 Raportet
- Numri total i automjeteve
- Automjetet brenda parkingut
- Të ardhurat totale
- Statistikat ditore

## 🔧 Konfigurimi

### Cilësimet e sistemit
- Çmimi për orë: €2.00
- Çmimi për ditë: €20.00
- Kapaciteti maksimal: 50 automjete
- Teksti i biletës: Personalizueshëm

### Hardware (opsional)
- **Raspberry Pi** për barrierat
- **Printer** për biletat
- **Kamera** për fotografi
- **QR Scanner** për dalje

## 🌐 Deploy online

Sistemi është i konfiguruar për deploy në platforma si:
- **Render.com** (falas)
- **PythonAnywhere** (falas)
- **Heroku** (falas)

## 📱 API Endpoints

### Automjetet
- `GET /api/vehicles` - Lista e automjeteve
- `POST /api/entry` - Hyrja e automjetit
- `POST /api/exit` - Dalja e automjetit

### Pagesat
- `POST /api/pay_ticket` - Pagesa e biletës
- `POST /api/verify_ticket` - Verifikimi i biletës

### RFID
- `POST /api/rfid/entry` - Hyrja me RFID
- `POST /api/rfid/exit` - Dalja me RFID
- `GET /api/rfid/status` - Statusi i kartelës

## 🛠️ Zhvillimi

### Struktura e projektit
```
parking-system/
├── app.py                 # Aplikacioni kryesor
├── requirements.txt       # Varësitë
├── templates/            # Template-t HTML
├── static/              # CSS, JS, imazhe
├── photos/              # Fotografitë e automjeteve
├── tickets/             # Biletat e printuara
└── backups/             # Backup-et e databazës
```

### Testimi
```bash
python run_test.py
```

## 📞 Kontakti

Për pyetje dhe mbështetje:
- **Email:** dukagjin@example.com
- **GitHub:** [@dukagjinR](https://github.com/dukagjinR)

## 📄 Licenca

Ky projekt është i krijuar për qëllime edukative dhe komerciale.

---

**Powered by fara.io** 🚀 