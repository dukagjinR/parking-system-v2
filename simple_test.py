#!/usr/bin/env python3
"""
Simple test to check basic functionality
"""

from app import app, db, Vehicle, ParkingSettings

# Test database creation
with app.app_context():
    try:
        db.create_all()
        print("✅ Database created successfully")
        
        # Test creating settings
        settings = ParkingSettings.query.first()
        if not settings:
            settings = ParkingSettings()
            db.session.add(settings)
            db.session.commit()
            print("✅ Settings created successfully")
        else:
            print("✅ Settings already exist")
        
        # Test creating a vehicle
        vehicle = Vehicle(
            plate_number="TEST123",
            ticket_number="T20250716123456",
            payment_status='unpaid'
        )
        db.session.add(vehicle)
        db.session.commit()
        print("✅ Vehicle created successfully")
        
        # Test querying vehicles
        vehicles = Vehicle.query.all()
        print(f"✅ Found {len(vehicles)} vehicles in database")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

print("✅ Basic functionality test completed") 