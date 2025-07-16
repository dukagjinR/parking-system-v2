# 🧪 Test Environment Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Environment
```bash
python run_test.py
```

### 3. Access Test Interface
- **Main System**: http://localhost:5000
- **Test Dashboard**: http://localhost:5000/test

## 🎯 What You Can Test

### Hardware Simulation
- ✅ **Entry Barrier** - Simulates opening/closing entry barrier
- ✅ **Exit Barrier** - Simulates opening/closing exit barrier  
- ✅ **Camera Capture** - Simulates taking photos
- ✅ **Ticket Printing** - Simulates printing parking tickets
- ✅ **Receipt Printing** - Simulates printing exit receipts
- ✅ **Barcode Scanning** - Simulates scanning QR codes

### System Functions
- ✅ **Vehicle Entry** - Complete entry process simulation
- ✅ **Vehicle Exit** - Complete exit process with payment
- ✅ **Dashboard** - Real-time statistics and monitoring
- ✅ **Reports** - Revenue tracking and analytics
- ✅ **Settings** - System configuration

## 🎮 Interactive Test Features

### Test Dashboard (`/test`)
- **Hardware Test Controls** - Buttons to test each hardware component
- **Mock Hardware Status** - Shows status of all simulated devices
- **Test Statistics** - Live data from test environment
- **Test Forms** - Simulate vehicle entry/exit
- **Console Output** - Real-time feedback from all operations

### Test API Endpoints
```
GET  /test/api/barrier/entry     - Test entry barrier
GET  /test/api/barrier/exit      - Test exit barrier  
GET  /test/api/printer/ticket    - Test ticket printing
GET  /test/api/printer/receipt   - Test receipt printing
GET  /test/api/camera/capture    - Test camera capture
GET  /test/api/scan             - Test barcode scanning
```

## 📊 Test Data

The system automatically generates test data:
- **3 Test Vehicles** with different entry times
- **Mock Settings** with default parking rates
- **Sample Photos** in test_photos/ directory
- **Sample Tickets** in tickets/ directory

## 🔧 How It Works

### Mock Hardware Class
```python
class MockHardware:
    def open_entry_barrier(self):
        print("🔓 Entry barrier opened")
        time.sleep(2)
        print("🔒 Entry barrier closed")
    
    def print_ticket(self, ticket_data):
        print("🖨️ Printing ticket:")
        print(f"  Ticket: {ticket_data['ticket_number']}")
        # ... more details
```

### Console Output
All hardware operations show in the console:
```
[10:30:15] 🔓 Entry barrier test: Entry barrier opened
[10:30:17] 🖨️ Ticket print test: Ticket printed
[10:30:18] 📷 Camera capture test: Photo saved to test_photos/entry_1_20240101_103018.jpg
```

## 🎯 Test Scenarios

### Scenario 1: Vehicle Entry
1. Go to `/test` dashboard
2. Click "Test Entry Barrier" - See console output
3. Click "Test Print Ticket" - See ticket details
4. Click "Test Camera Capture" - See photo saved
5. Use "Test Vehicle Entry" form - Complete simulation

### Scenario 2: Vehicle Exit  
1. Go to `/test` dashboard
2. Click "Test Barcode Scan" - See ticket found
3. Click "Test Print Receipt" - See receipt details
4. Click "Test Exit Barrier" - See barrier open/close
5. Use "Test Vehicle Exit" form - Complete simulation

### Scenario 3: System Monitoring
1. Go to main dashboard `/`
2. See real-time statistics
3. Check "Recent Entries" and "Recent Exits"
4. View "Reports" for analytics
5. Configure "Settings"

## 📁 Generated Files

### Test Photos
```
test_photos/
├── entry_1_20240101_103018.jpg
├── exit_1_20240101_104530.jpg
└── test_1_20240101_102045.jpg
```

### Test Tickets
```
tickets/
├── T20240101120000.png
├── T20240101130000.png
└── T20240101140000.png
```

### Database
```
parking.db - SQLite database with test data
```

## 🚨 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
pip install flask flask-sqlalchemy pillow opencv-python pyzbar qrcode
```

#### Port 5000 already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

#### Database errors
```bash
# Remove old database
rm parking.db
# Restart test environment
python run_test.py
```

### Debug Commands
```bash
# Check if Flask is installed
python -c "import flask; print('Flask OK')"

# Check if all files exist
ls -la app.py requirements.txt templates/

# Test database creation
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 🎯 Expected Behavior

### Console Output Examples
```
🚗 Parking System Test Environment Started
✅ Mock hardware initialized
✅ Test data generated
🌐 Web interface available at http://localhost:5000

🔓 Entry barrier opened
🔒 Entry barrier closed
🖨️ Printing ticket:
  Ticket: T20240101120000
  Plate: TEST-123
  Entry: 2024-01-01 12:00:00
📷 Camera capture test: Photo saved to test_photos/entry_1_20240101_120000.jpg
```

### Web Interface Features
- **Real-time updates** - Statistics refresh automatically
- **Interactive buttons** - All hardware functions testable
- **Visual feedback** - Status indicators show device states
- **Form validation** - Input validation for test forms
- **Responsive design** - Works on desktop and mobile

## 🎉 Success Indicators

✅ **Test Environment Running**
- Server starts without errors
- Console shows "Mock hardware initialized"
- Web interface accessible at http://localhost:5000

✅ **Hardware Simulation Working**
- Barrier buttons show console output
- Printer functions display ticket/receipt details
- Camera capture creates test photo files
- Barcode scan returns test ticket data

✅ **System Functions Working**
- Dashboard shows test statistics
- Entry/exit forms process data
- Reports display test analytics
- Settings save configuration

## 🚀 Next Steps

After testing the environment:
1. **Review the code** - Understand how each component works
2. **Modify settings** - Try different configurations
3. **Add test data** - Create more test scenarios
4. **Deploy to Raspberry Pi** - Use the real hardware setup
5. **Customize features** - Adapt to your specific needs

---

**Happy Testing! 🚗💻** 