#!/usr/bin/env python3
"""
Simple Test Runner for Parking Management System
Runs the system without hardware dependencies for testing
"""

import os
import sys
from datetime import datetime

def main():
    print("🚗 Parking System Test Environment")
    print("=" * 40)
    
    # Check if required files exist
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/base.html',
        'templates/dashboard.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are present before running the test environment.")
        return
    
    print("✅ All required files found")
    
    # Create necessary directories
    directories = ['photos', 'tickets', 'backups', 'logs', 'test_photos']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import flask
        import flask_sqlalchemy
        print("✅ Flask dependencies already installed")
    except ImportError:
        print("⚠️  Flask not found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return
    
    # Start the test environment
    print("\n🌐 Starting test environment...")
    print("   Access the system at: http://localhost:9000")
    print("   Test dashboard at: http://localhost:9000/test")
    print("\n📋 Available test features:")
    print("   - Mock hardware simulation")
    print("   - Test vehicle entry/exit")
    print("   - Simulated camera capture")
    print("   - Mock printer functions")
    print("   - Barrier control testing")
    print("   - Barcode scanning simulation")
    
    print("\n🔧 Test API endpoints:")
    print("   - /test/api/barrier/entry - Test entry barrier")
    print("   - /test/api/barrier/exit - Test exit barrier")
    print("   - /test/api/printer/ticket - Test ticket printing")
    print("   - /test/api/printer/receipt - Test receipt printing")
    print("   - /test/api/camera/capture - Test camera capture")
    print("   - /test/api/scan - Test barcode scanning")
    
    print("\n🚀 Starting server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Import and run the test environment
    try:
        # Import the main app
        from app import app, db, Vehicle, ParkingSettings, ParkingLog
        
        # Import test environment functions
        from test_environment import setup_test_environment, generate_test_data
        
        # Setup test environment
        setup_test_environment(app, db, Vehicle, ParkingSettings, ParkingLog)
        
        # Initialize database
        with app.app_context():
            db.create_all()
            print("✅ Database initialized")
        
        # Generate test data
        with app.app_context():
            generate_test_data(app, db, Vehicle, ParkingSettings, ParkingLog)
        
        # Run the application on port 9000
        app.run(host='0.0.0.0', port=9000, debug=True)
        
    except Exception as e:
        print(f"❌ Error starting test environment: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all files are present")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check if port 9000 is available")

if __name__ == "__main__":
    main() 