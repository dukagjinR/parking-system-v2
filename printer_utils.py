#!/usr/bin/env python3
"""
Thermal Printer Utilities for Parking Management System
"""

import os
import sys
import time
from datetime import datetime

class ThermalPrinter:
    def __init__(self, device_path="/dev/usb/lp0"):
        self.device_path = device_path
        self.is_connected = self._check_connection()
    
    def _check_connection(self):
        """Check if printer is connected"""
        try:
            return os.path.exists(self.device_path)
        except:
            return False
    
    def _send_command(self, command):
        """Send command to printer"""
        try:
            with open(self.device_path, 'wb') as printer:
                printer.write(command.encode('latin-1'))
                printer.flush()
            return True
        except Exception as e:
            print(f"Printer error: {e}")
            return False
    
    def print_ticket(self, ticket_data):
        """Print parking ticket"""
        if not self.is_connected:
            print("Printer not connected")
            return False
        
        # ESC/POS commands for thermal printer
        commands = []
        
        # Initialize printer
        commands.append('\x1B\x40')  # Initialize printer
        
        # Set alignment to center
        commands.append('\x1B\x61\x01')  # Center alignment
        
        # Print header
        commands.append('\x1B\x21\x10')  # Double height and width
        commands.append('PARKING TICKET\n')
        commands.append('\x1B\x21\x00')  # Normal text
        
        # Print ticket details
        commands.append(f"Ticket: {ticket_data['ticket_number']}\n")
        commands.append(f"Plate: {ticket_data['plate_number']}\n")
        commands.append(f"Entry: {ticket_data['entry_time']}\n")
        
        # Print QR code placeholder
        commands.append('\n[QR Code]\n')
        
        # Print footer
        commands.append('\nKeep this ticket for exit\n')
        commands.append('Thank you!\n')
        
        # Cut paper
        commands.append('\x1D\x56\x00')  # Full cut
        
        # Send all commands
        for command in commands:
            if not self._send_command(command):
                return False
            time.sleep(0.1)  # Small delay between commands
        
        return True
    
    def print_receipt(self, receipt_data):
        """Print exit receipt"""
        if not self.is_connected:
            print("Printer not connected")
            return False
        
        commands = []
        
        # Initialize printer
        commands.append('\x1B\x40')
        
        # Set alignment to center
        commands.append('\x1B\x61\x01')
        
        # Print header
        commands.append('\x1B\x21\x10')
        commands.append('PARKING RECEIPT\n')
        commands.append('\x1B\x21\x00')
        
        # Print receipt details
        commands.append(f"Ticket: {receipt_data['ticket_number']}\n")
        commands.append(f"Plate: {receipt_data['plate_number']}\n")
        commands.append(f"Entry: {receipt_data['entry_time']}\n")
        commands.append(f"Exit: {receipt_data['exit_time']}\n")
        commands.append(f"Duration: {receipt_data['duration']}\n")
        commands.append(f"Amount: €{receipt_data['amount']:.2f}\n")
        
        # Print footer
        commands.append('\nThank you for parking!\n')
        commands.append('Please come again!\n')
        
        # Cut paper
        commands.append('\x1D\x56\x00')
        
        # Send all commands
        for command in commands:
            if not self._send_command(command):
                return False
            time.sleep(0.1)
        
        return True
    
    def test_print(self):
        """Print test page"""
        if not self.is_connected:
            print("Printer not connected")
            return False
        
        test_data = {
            'ticket_number': 'TEST123',
            'plate_number': 'TEST-ABC',
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration': '1 hour',
            'amount': 2.00
        }
        
        return self.print_receipt(test_data)

def find_printer():
    """Find available printer devices"""
    possible_paths = [
        "/dev/usb/lp0",
        "/dev/usb/lp1", 
        "/dev/usb/lp2",
        "/dev/ttyUSB0",
        "/dev/ttyUSB1"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def test_printer_connection():
    """Test printer connection"""
    printer_path = find_printer()
    if printer_path:
        print(f"Printer found at: {printer_path}")
        printer = ThermalPrinter(printer_path)
        if printer.test_print():
            print("Test print successful")
            return True
        else:
            print("Test print failed")
            return False
    else:
        print("No printer found")
        return False

if __name__ == "__main__":
    # Test printer functionality
    print("Testing thermal printer...")
    test_printer_connection() 