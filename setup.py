#!/usr/bin/env python3
"""
Parking Management System Setup Script
For Raspberry Pi Installation
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "photos",
        "tickets", 
        "backups",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Update package list
    if not run_command("sudo apt-get update", "Updating package list"):
        return False
    
    # Install system dependencies
    system_packages = [
        "python3-pip",
        "python3-venv",
        "libopencv-dev",
        "python3-opencv",
        "libzbar0",
        "libzbar-dev",
        "python3-dev",
        "build-essential"
    ]
    
    for package in system_packages:
        if not run_command(f"sudo apt-get install -y {package}", f"Installing {package}"):
            return False
    
    # Create virtual environment
    if not run_command("python3 -m venv venv", "Creating virtual environment"):
        return False
    
    # Activate virtual environment and install Python packages
    activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    if not run_command(activate_cmd, "Installing Python packages"):
        return False
    
    return True

def setup_gpio():
    """Setup GPIO configuration"""
    print("🔌 Setting up GPIO...")
    
    # Add user to gpio group
    if not run_command("sudo usermod -a -G gpio $USER", "Adding user to gpio group"):
        return False
    
    # Create GPIO configuration file
    gpio_config = """# GPIO Configuration for Parking System
# Entry barrier relay
GPIO_ENTRY_BARRIER=18
# Exit barrier relay  
GPIO_EXIT_BARRIER=19
# Printer button
GPIO_PRINTER_BUTTON=17
# Status LED
GPIO_STATUS_LED=13
"""
    
    with open("gpio_config.txt", "w") as f:
        f.write(gpio_config)
    
    print("✅ GPIO configuration created")
    return True

def setup_camera():
    """Setup camera configuration"""
    print("📷 Setting up camera...")
    
    # Enable camera interface
    if not run_command("sudo raspi-config nonint do_camera 0", "Enabling camera interface"):
        return False
    
    # Install camera dependencies
    camera_packages = [
        "fswebcam",
        "v4l-utils"
    ]
    
    for package in camera_packages:
        if not run_command(f"sudo apt-get install -y {package}", f"Installing {package}"):
            return False
    
    print("✅ Camera setup completed")
    return True

def create_service():
    """Create systemd service for auto-start"""
    print("⚙️ Creating systemd service...")
    
    service_content = """[Unit]
Description=Parking Management System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/parking-system
Environment=PATH=/home/pi/parking-system/venv/bin
ExecStart=/home/pi/parking-system/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open("parking-system.service", "w") as f:
        f.write(service_content)
    
    # Copy service file to systemd directory
    if not run_command("sudo cp parking-system.service /etc/systemd/system/", "Copying service file"):
        return False
    
    # Enable and start service
    if not run_command("sudo systemctl daemon-reload", "Reloading systemd"):
        return False
    
    if not run_command("sudo systemctl enable parking-system", "Enabling service"):
        return False
    
    print("✅ Systemd service created and enabled")
    return True

def create_startup_script():
    """Create startup script"""
    print("🚀 Creating startup script...")
    
    startup_script = """#!/bin/bash
# Parking System Startup Script

cd /home/pi/parking-system

# Activate virtual environment
source venv/bin/activate

# Start the application
python app.py
"""
    
    with open("start.sh", "w") as f:
        f.write(startup_script)
    
    # Make executable
    if not run_command("chmod +x start.sh", "Making startup script executable"):
        return False
    
    print("✅ Startup script created")
    return True

def create_config_file():
    """Create configuration file"""
    print("⚙️ Creating configuration file...")
    
    config_content = """# Parking System Configuration

[DATABASE]
# SQLite database file
database_path = parking.db

[CAMERA]
# Camera settings
camera_type = ip  # ip or usb
camera_ip = 192.168.1.100
camera_username = admin
camera_password = admin
camera_port = 80

[GPIO]
# GPIO pin assignments
entry_barrier_pin = 18
exit_barrier_pin = 19
printer_button_pin = 17
status_led_pin = 13

[PRICING]
# Parking rates
hourly_rate = 2.0
daily_rate = 20.0
max_capacity = 50

[SYSTEM]
# System settings
debug_mode = false
auto_backup = true
backup_interval = 24  # hours
"""
    
    with open("config.ini", "w") as f:
        f.write(config_content)
    
    print("✅ Configuration file created")
    return True

def setup_firewall():
    """Setup firewall rules"""
    print("🔥 Setting up firewall...")
    
    # Allow web interface
    if not run_command("sudo ufw allow 5000", "Allowing port 5000"):
        return False
    
    # Enable firewall
    if not run_command("sudo ufw --force enable", "Enabling firewall"):
        return False
    
    print("✅ Firewall configured")
    return True

def create_readme():
    """Create README file"""
    print("📖 Creating README...")
    
    readme_content = """# Parking Management System

## Overview
A comprehensive parking management system designed for Raspberry Pi with automatic barrier control, camera integration, and web-based dashboard.

## Features
- Vehicle entry/exit management
- Automatic barrier control
- Camera photo capture
- QR code ticket generation
- Barcode scanning for exit
- Real-time dashboard
- Revenue tracking and reports
- USB thermal printer support
- IP camera integration

## Hardware Requirements
- Raspberry Pi 4 (recommended)
- USB camera or IP camera
- 2x Relay modules for barriers
- USB thermal printer
- Barcode scanner (for exit)
- GPIO buttons and LEDs

## Installation
1. Clone this repository
2. Run: python3 setup.py
3. Configure settings in config.ini
4. Start the system: ./start.sh

## Web Interface
Access the dashboard at: http://raspberry-pi-ip:5000

## GPIO Connections
- GPIO 17: Printer button (input)
- GPIO 18: Entry barrier relay (output)
- GPIO 19: Exit barrier relay (output)
- GPIO 13: Status LED (output)

## Configuration
Edit config.ini to customize:
- Parking rates
- Camera settings
- GPIO pin assignments
- System parameters

## Support
For issues and questions, check the logs in the logs/ directory.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ README created")

def main():
    """Main setup function"""
    print("🚗 Parking Management System Setup")
    print("=" * 40)
    
    # Check if running on Raspberry Pi
    if not os.path.exists("/proc/device-tree/model"):
        print("⚠️  Warning: This script is designed for Raspberry Pi")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup components
    if not setup_gpio():
        print("❌ Failed to setup GPIO")
        sys.exit(1)
    
    if not setup_camera():
        print("❌ Failed to setup camera")
        sys.exit(1)
    
    if not create_service():
        print("❌ Failed to create systemd service")
        sys.exit(1)
    
    if not create_startup_script():
        print("❌ Failed to create startup script")
        sys.exit(1)
    
    if not create_config_file():
        print("❌ Failed to create config file")
        sys.exit(1)
    
    if not setup_firewall():
        print("❌ Failed to setup firewall")
        sys.exit(1)
    
    create_readme()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config.ini with your settings")
    print("2. Connect hardware components")
    print("3. Start the system: ./start.sh")
    print("4. Access web interface: http://your-pi-ip:5000")
    print("\nFor troubleshooting, check the logs in logs/ directory")

if __name__ == "__main__":
    main() 