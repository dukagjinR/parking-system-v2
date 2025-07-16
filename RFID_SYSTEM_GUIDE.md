# 🚗 Sistemi i Menaxhimit të Kartelave RFID

## 📋 Përmbledhje

Sistemi i menaxhimit të kartelave RFID është një modul i ri i shtuar në sistemin e parkingut që lejon menaxhimin e kartelave RFID me pagesa sipas kohëzgjatjes dhe kontroll të hyrjes/daljes.

## 🎯 Veçoritë Kryesore

### ✅ **Menaxhimi i Kartelave RFID**
- Krijimi i kartelave të reja me numër unik
- Edicionimi i informacioneve të pronarit
- Kontrolli i statusit (aktive, e skaduar, e bllokuar)
- Fshirja e kartelave

### ✅ **Sistemet e Pagesës**
- **1 Muaj**: €30.00
- **3 Muaj**: €80.00  
- **6 Muaj**: €150.00
- **1 Vit**: €280.00

### ✅ **Kontrolli i Hyrjes/Daljes**
- Një hyrje, një dalje (nuk lejon 2 hyrje pa dalje)
- Kontrolli automatik i skadimit të pagesës
- Bllokimi i kartelave të skaduara
- Njoftimet për pagesat që po skadojnë

### ✅ **Siguria dhe Kontrolli**
- Kontrolli i vlefshmërisë së kartelës
- Kontrolli i statusit aktual
- Kontrolli i hyrjes së dyfishtë
- Përditësimi automatik i statusit të skadimit

## 🏗️ Arkitektura e Sistemit

### **Modeli i Të Dhënave**

```python
class RFIDCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')
    max_entries = db.Column(db.Integer, default=1000)
    current_entries = db.Column(db.Integer, default=0)
    is_inside = db.Column(db.Boolean, default=False)
    last_entry_time = db.Column(db.DateTime, nullable=True)
    last_exit_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **API Endpoints**

| Endpoint | Metoda | Përshkrimi |
|----------|--------|------------|
| `/rfid_cards` | GET | Lista e kartelave RFID |
| `/rfid_cards/add` | GET/POST | Shtimi i kartelës së re |
| `/rfid_cards/edit/<id>` | GET/POST | Edicionimi i kartelës |
| `/rfid_cards/delete/<id>` | POST | Fshirja e kartelës |
| `/api/rfid/entry` | POST | Hyrja me kartelë RFID |
| `/api/rfid/exit` | POST | Dalja me kartelë RFID |
| `/api/rfid/check` | POST | Kontrolli i statusit |
| `/rfid_test` | GET | Faqja e testimit |

## 🚀 Si të Përdoret

### **1. Hyrja në Sistem**
```
URL: http://localhost:9000
Përdoruesi Admin: admin/admin123
Përdoruesi Operator: operator/operator123
```

### **2. Menaxhimi i Kartelave RFID**

#### **Shtimi i Kartelës së Re**
1. Hyni si administrator
2. Klikoni "Kartelat RFID" në menunë
3. Klikoni "Shto Kartelë të Re"
4. Plotësoni informacionet:
   - **Numër Kartele**: Numri unik i kartelës RFID
   - **Emri i Pronarit**: Emri i plotë i pronarit
   - **Lloji i Pagesës**: Zgjidhni periudhën e pagesës
5. Klikoni "Krijo Kartelën"

#### **Edicionimi i Kartelës**
1. Në listën e kartelave, klikoni ikonën e editimit
2. Ndryshoni emrin e pronarit ose statusin
3. Klikoni "Ruaj Ndryshimet"

#### **Fshirja e Kartelës**
1. Në listën e kartelave, klikoni ikonën e fshirjes
2. Konfirmoni fshirjen në modal

### **3. Testimi i Kartelave**

#### **Përdorimi i Faqes së Testit**
1. Klikoni "Testimi RFID" në menunë
2. Shkruani numrin e kartelës RFID
3. Klikoni "Kontrollo Kartelën"
4. Përdorni "Testo Hyrjen" ose "Testo Daljen"

#### **API Testing**
```bash
# Kontrolli i statusit
curl -X POST http://localhost:9000/api/rfid/check \
  -H "Content-Type: application/json" \
  -d '{"card_number": "RFID001"}'

# Testimi i hyrjes
curl -X POST http://localhost:9000/api/rfid/entry \
  -H "Content-Type: application/json" \
  -d '{"card_number": "RFID001"}'

# Testimi i daljes
curl -X POST http://localhost:9000/api/rfid/exit \
  -H "Content-Type: application/json" \
  -d '{"card_number": "RFID001"}'
```

## 🔧 Konfigurimi

### **Çmimet e Pagesës**
Çmimet mund të ndryshohen në kodin e aplikacionit:

```python
# Në app.py, funksioni add_rfid_card()
if payment_type == '1_month':
    end_date = start_date + timedelta(days=30)
elif payment_type == '3_months':
    end_date = start_date + timedelta(days=90)
elif payment_type == '6_months':
    end_date = start_date + timedelta(days=180)
elif payment_type == '1_year':
    end_date = start_date + timedelta(days=365)
```

### **Kontrolli i Skadimit**
Sistemi përditëson automatikisht statusin e kartelave të skaduara:

```python
def update_expired_cards():
    expired_cards = RFIDCard.query.filter(
        RFIDCard.status == 'active',
        RFIDCard.end_date < datetime.utcnow()
    ).all()
    
    for card in expired_cards:
        card.status = 'expired'
```

## 🛡️ Siguria

### **Kontrolli i Hyrjes së Dyfishtë**
```python
def can_enter(self):
    """Check if card can enter (not already inside)"""
    return self.is_valid() and not self.is_inside
```

### **Validimi i Kartelës**
```python
def is_valid(self):
    """Check if card is valid and not expired"""
    return (self.status == 'active' and 
            self.end_date > datetime.utcnow() and 
            self.current_entries < self.max_entries)
```

## 📊 Raportimi

### **Statistikat e Kartelave**
- Numri i kartelave aktive
- Numri i kartelave të skaduara
- Numri i kartelave të bllokuara
- Numri i kartelave brenda parkingut

### **Informacionet e Detajuara**
- Data e krijimit
- Data e hyrjes së fundit
- Data e daljes së fundit
- Numri i hyrjeve
- Statusi aktual

## 🧪 Testimi

### **Scripti i Testit**
Ekzekutoni `test_rfid_system.py` për të testuar të gjitha funksionet:

```bash
python test_rfid_system.py
```

### **Testet e Automatizuara**
1. Krijimi i kartelave
2. Kontrolli i statusit
3. Testimi i hyrjes/daljes
4. Validimi i kartelave të pavlefshme
5. Kontrolli i hyrjes së dyfishtë

## 🔄 Integrimi me Hardware

### **RFID Reader**
Për integrimin me hardware të vërtetë, shtoni këtë kod:

```python
# Në hardware_setup.py
import serial

class RFIDReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.serial = serial.Serial(port, baudrate)
    
    def read_card(self):
        """Read RFID card number from hardware"""
        if self.serial.in_waiting:
            card_number = self.serial.readline().decode().strip()
            return card_number
        return None
```

### **Barrier Control**
```python
def open_entry_barrier():
    """Open entry barrier for RFID card"""
    if HARDWARE_AVAILABLE:
        GPIO.output(ENTRY_BARRIER, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(ENTRY_BARRIER, GPIO.LOW)
    print("🔓 Barriera e hyrjes u hap për kartelën RFID")
```

## 📝 Shënime të Rëndësishme

### **Kujdeset**
1. **Numri i Kartelës**: Duhet të jetë unik
2. **Skadimi**: Kontrollohet automatikisht
3. **Hyrja e Dyfishtë**: Nuk lejohet
4. **Backup**: Bëni backup të databazës rregullisht

### **Troubleshooting**
- **Kartela nuk pranohet**: Kontrolloni statusin dhe datën e skadimit
- **Gabim në hyrje**: Kontrolloni nëse kartela është tashmë brenda
- **Gabim në dalje**: Kontrolloni nëse kartela është brenda parkingut

## 🆘 Mbështetja

Për probleme ose pyetje:
1. Kontrolloni log-et e sistemit
2. Testoni me faqen e testimit RFID
3. Kontrolloni statusin e databazës
4. Ristartoni serverin nëse është e nevojshme

---

**Powered by fara.io** 🚀 