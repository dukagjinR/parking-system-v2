# Hardware Setup Guide

## Overview
This guide explains how to connect all hardware components to your Raspberry Pi for the parking management system.

## Required Components

### Core Components
- **Raspberry Pi 4** (4GB RAM recommended)
- **MicroSD Card** (32GB Class 10)
- **Power Supply** (5V 3A)
- **USB Camera** or **IP Camera**
- **USB Thermal Printer** (80mm paper)
- **Barcode Scanner** (USB)

### GPIO Components
- **2x Relay Modules** (5V, for barriers)
- **1x Push Button** (for printer trigger)
- **1x LED** (for status indicator)
- **Breadboard** and **Jumper Wires**
- **GPIO Extension Board** (optional)

## GPIO Pin Assignments

| Component | GPIO Pin | Type | Description |
|-----------|----------|------|-------------|
| Entry Barrier | GPIO 18 | Output | Controls entry barrier relay |
| Exit Barrier | GPIO 19 | Output | Controls exit barrier relay |
| Printer Button | GPIO 17 | Input | Manual printer trigger |
| Status LED | GPIO 13 | Output | System status indicator |

## Connection Diagram

```
Raspberry Pi 4
├── GPIO 17 ── Push Button ── GND
├── GPIO 18 ── Relay Module 1 ── Entry Barrier
├── GPIO 19 ── Relay Module 2 ── Exit Barrier
├── GPIO 13 ── LED ── GND (with 220Ω resistor)
├── USB 1 ──── USB Camera
├── USB 2 ──── USB Thermal Printer
└── USB 3 ──── Barcode Scanner
```

## Step-by-Step Setup

### 1. Power Supply
- Connect 5V 3A power supply to Raspberry Pi
- Ensure stable power for reliable operation

### 2. Camera Setup
**Option A: USB Camera**
- Connect USB camera to any USB port
- Test with: `lsusb` and `v4l2-ctl --list-devices`

**Option B: IP Camera**
- Connect IP camera to network
- Configure IP address in settings
- Test connection in web interface

### 3. Printer Setup
- Connect USB thermal printer
- Install printer drivers if needed
- Test with: `lsusb | grep printer`
- Configure in system settings

### 4. Barcode Scanner
- Connect USB barcode scanner
- Test scanning functionality
- Configure for QR code reading

### 5. GPIO Connections

#### Entry Barrier Relay (GPIO 18)
```
Raspberry Pi ── GPIO 18 ── Relay IN1
                GND ──── Relay GND
                VCC ──── Relay VCC
Relay COM ──── Entry Barrier Power
Relay NO ──── Entry Barrier Control
```

#### Exit Barrier Relay (GPIO 19)
```
Raspberry Pi ── GPIO 19 ── Relay IN2
                GND ──── Relay GND
                VCC ──── Relay VCC
Relay COM ──── Exit Barrier Power
Relay NO ──── Exit Barrier Control
```

#### Printer Button (GPIO 17)
```
Raspberry Pi ── GPIO 17 ── Button Pin 1
                GND ──── Button Pin 2
```

#### Status LED (GPIO 13)
```
Raspberry Pi ── GPIO 13 ── 220Ω Resistor ── LED Anode
                GND ──── LED Cathode
```

## Testing Connections

### 1. Test GPIO Pins
```bash
# Test output pins
echo "18" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio18/direction
echo "1" > /sys/class/gpio/gpio18/value
echo "0" > /sys/class/gpio/gpio18/value

# Test input pin
echo "17" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio17/direction
cat /sys/class/gpio/gpio17/value
```

### 2. Test Camera
```bash
# USB Camera
fswebcam test.jpg

# IP Camera
curl -o test.jpg http://camera-ip/snapshot
```

### 3. Test Printer
```bash
# Send test print
echo "Test Print" > /dev/usb/lp0
```

### 4. Test Barcode Scanner
- Scan a QR code
- Check if data appears in terminal

## Safety Considerations

### Electrical Safety
- Use appropriate voltage levels (5V for relays)
- Add fuses for barrier power circuits
- Ensure proper grounding
- Use surge protection for power circuits

### Mechanical Safety
- Secure barrier mechanisms properly
- Add emergency stop functionality
- Install safety sensors
- Regular maintenance schedule

### Software Safety
- Add timeout mechanisms for barriers
- Implement error handling
- Log all operations
- Backup system regularly

## Troubleshooting

### Common Issues

#### GPIO Not Working
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
# Reboot required after this change
```

#### Camera Not Detected
```bash
# Check USB devices
lsusb
# Check video devices
ls /dev/video*
# Test camera
v4l2-ctl --list-devices
```

#### Printer Not Working
```bash
# Check USB devices
lsusb | grep printer
# Check printer permissions
sudo usermod -a -G lp $USER
```

#### Barrier Not Responding
- Check relay connections
- Verify power supply
- Test relay manually
- Check GPIO pin assignments

### Debug Commands
```bash
# Check system status
sudo systemctl status parking-system

# View logs
tail -f logs/parking.log

# Test GPIO
gpio readall

# Check network
ip addr show

# Test web interface
curl http://localhost:5000
```

## Maintenance

### Regular Checks
- Clean camera lens monthly
- Test barrier operation weekly
- Check printer paper supply
- Verify backup system
- Update system software

### Backup Procedures
```bash
# Backup database
cp parking.db backups/parking_$(date +%Y%m%d).db

# Backup configuration
cp config.ini backups/config_$(date +%Y%m%d).ini

# Backup photos
tar -czf backups/photos_$(date +%Y%m%d).tar.gz photos/
```

## Advanced Configuration

### Multiple Cameras
- Configure multiple camera inputs
- Use different GPIO pins for each
- Implement camera switching logic

### Network Integration
- Connect to existing network infrastructure
- Configure VLAN for security
- Implement remote monitoring

### Power Management
- Add UPS for power backup
- Implement graceful shutdown
- Monitor power consumption

## Support

For hardware issues:
1. Check all connections
2. Verify power supply
3. Test individual components
4. Check system logs
5. Contact technical support

For software issues:
1. Check application logs
2. Verify configuration
3. Test in debug mode
4. Update software
5. Restore from backup 