#!/usr/bin/env python3
"""
Test Environment for Parking Management System
Simulates all functions without requiring actual hardware
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import threading

# Mock hardware functions for testing
class MockHardware:
    def __init__(self):
        self.camera_connected = True
        self.printer_connected = True
        self.barrier_entry_open = False
        self.barrier_exit_open = False
        self.button_pressed = False
        self.status_led = False
        
    def capture_photo(self, vehicle_id, action):
        """Simulate photo capture"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_photos/{action}_{vehicle_id}_{timestamp}.jpg"
        os.makedirs("test_photos", exist_ok=True)
        
        # Create a mock photo file
        with open(filename, 'w') as f:
            f.write(f"Mock photo for {action} - Vehicle {vehicle_id} - {timestamp}")
        
        return filename
    
    def open_entry_barrier(self):
        """Simulate opening entry barrier"""
        self.barrier_entry_open = True
        print("🔓 Barriera e hyrjes u hap")
        time.sleep(2)
        self.barrier_entry_open = False
        print("🔒 Barriera e hyrjes u mbyll")
    
    def open_exit_barrier(self):
        """Simulate opening exit barrier"""
        self.barrier_exit_open = True
        print("🔓 Barriera e daljes u hap")
        time.sleep(2)
        self.barrier_exit_open = False
        print("🔒 Barriera e daljes u mbyll")
    
    def print_ticket(self, ticket_data):
        """Simulate printing ticket"""
        print("🖨️ Duke printuar billetën:")
        print(f"  Bileta: {ticket_data['ticket_number']}")
        print(f"  Targa: {ticket_data['plate_number']}")
        print(f"  Hyrja: {ticket_data['entry_time']}")
        return True
    
    def print_receipt(self, receipt_data):
        """Simulate printing receipt"""
        print("🖨️ Duke printuar faturën:")
        print(f"  Bileta: {receipt_data['ticket_number']}")
        print(f"  Targa: {receipt_data['plate_number']}")
        print(f"  Shuma: €{receipt_data['amount']:.2f}")
        return True
    
    def scan_barcode(self):
        """Simulate barcode scanning"""
        # This will be called from the main app context
        return {'error': 'No tickets available for scanning'}

# Create mock hardware instance
mock_hardware = MockHardware()

# Mock functions that will be used by the main app
def mock_capture_photo(vehicle_id, action):
    return mock_hardware.capture_photo(vehicle_id, action)

def mock_open_barrier():
    return mock_hardware.open_entry_barrier()

def mock_open_exit_barrier():
    return mock_hardware.open_exit_barrier()

def mock_generate_ticket(vehicle):
    ticket_data = {
        'ticket_number': vehicle.ticket_number,
        'plate_number': vehicle.plate_number,
        'entry_time': vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    mock_hardware.print_ticket(ticket_data)
    return f"tickets/{vehicle.ticket_number}.png"

def mock_scan_barcode():
    return mock_hardware.scan_barcode()

# Function to setup test environment
def setup_test_environment(app, db, Vehicle, ParkingSettings, ParkingLog):
    """Setup test environment by overriding hardware functions"""
    
    # Override the main app functions
    import app as main_app
    main_app.capture_photo = mock_capture_photo
    main_app.open_barrier = mock_open_barrier
    main_app.open_exit_barrier = mock_open_exit_barrier
    main_app.generate_ticket = mock_generate_ticket
    
    # Add test routes
    @app.route('/test')
    def test_dashboard():
        """Test dashboard with mock data"""
        return render_template('test_dashboard.html')
    
    @app.route('/test/entry')
    def test_entry():
        """Test entry page"""
        return render_template('test_entry.html')
    
    @app.route('/test/exit')
    def test_exit():
        """Test exit page"""
        return render_template('test_exit.html')
    
    @app.route('/test/hardware')
    def test_hardware():
        """Test hardware status"""
        return render_template('test_hardware.html', hardware=mock_hardware)
    
    @app.route('/test/api/scan')
    def test_scan():
        """Test barcode scanning"""
        # Return a random existing ticket for testing
        vehicle = Vehicle.query.filter_by(is_inside=True).first()
        if vehicle:
            return jsonify({
                'success': True,
                'ticket_number': vehicle.ticket_number,
                'plate_number': vehicle.plate_number,
                'entry_time': vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({'error': 'No tickets available for scanning'})
    
    @app.route('/test/api/barrier/entry')
    def test_entry_barrier():
        """Test entry barrier"""
        mock_hardware.open_entry_barrier()
        return jsonify({'success': True, 'message': 'Entry barrier opened'})
    
    @app.route('/test/api/barrier/exit')
    def test_exit_barrier():
        """Test exit barrier"""
        mock_hardware.open_exit_barrier()
        return jsonify({'success': True, 'message': 'Exit barrier opened'})
    
    @app.route('/test/api/printer/ticket')
    def test_print_ticket():
        """Test ticket printing"""
        ticket_data = {
            'ticket_number': 'TEST123',
            'plate_number': 'TEST-ABC',
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        success = mock_hardware.print_ticket(ticket_data)
        return jsonify({'success': success, 'message': 'Ticket printed'})
    
    @app.route('/test/api/printer/receipt')
    def test_print_receipt():
        """Test receipt printing"""
        receipt_data = {
            'ticket_number': 'TEST123',
            'plate_number': 'TEST-ABC',
            'entry_time': '2024-01-01 10:00:00',
            'exit_time': '2024-01-01 12:00:00',
            'duration': '2 hours',
            'amount': 4.00
        }
        success = mock_hardware.print_receipt(receipt_data)
        return jsonify({'success': success, 'message': 'Receipt printed'})
    
    @app.route('/test/api/camera/capture')
    def test_camera_capture():
        """Test camera capture"""
        photo_path = mock_hardware.capture_photo(1, 'test')
        return jsonify({'success': True, 'photo_path': photo_path})

# Add test data generation
def generate_test_data(app, db, Vehicle, ParkingSettings, ParkingLog):
    """Generate test data for demonstration"""
    with app.app_context():
        # Create test settings
        settings = ParkingSettings.query.first()
        if not settings:
            settings = ParkingSettings()
            db.session.add(settings)
            db.session.commit()
        
        # Create some test vehicles
        test_vehicles = [
            {'plate': 'ABC-123', 'hours_ago': 2},
            {'plate': 'XYZ-789', 'hours_ago': 1},
            {'plate': 'DEF-456', 'hours_ago': 0.5},
        ]
        
        for vehicle_data in test_vehicles:
            # Check if vehicle already exists
            existing = Vehicle.query.filter_by(plate_number=vehicle_data['plate']).first()
            if not existing:
                entry_time = datetime.now() - timedelta(hours=vehicle_data['hours_ago'])
                vehicle = Vehicle(
                    plate_number=vehicle_data['plate'],
                    ticket_number=f"T{entry_time.strftime('%Y%m%d%H%M%S')}",
                    entry_time=entry_time,
                    is_inside=True
                )
                db.session.add(vehicle)
        
        db.session.commit()
        print("✅ Test data generated successfully")

if __name__ == '__main__':
    # Create test directories
    os.makedirs("test_photos", exist_ok=True)
    os.makedirs("tickets", exist_ok=True)
    
    print("🚗 Parking System Test Environment")
    print("=" * 40)
    print("✅ Mock hardware initialized")
    print("✅ Test functions ready")
    print("\n📋 This module provides test functions for the main app")
    print("   Run the main app with: python run_test.py") 