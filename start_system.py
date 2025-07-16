#!/usr/bin/env python3
"""
Parking System Startup Script
Automatically handles errors and starts the system
"""

import os
import sys
import subprocess
import time

def main():
    print("🚗 Parking Management System")
    print("=" * 40)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py nuk u gjet!")
        return
    
    # Try to start the system
    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"\n🔄 Përpjekja {attempt + 1}/{max_attempts}...")
        
        try:
            # Start the application
            result = subprocess.run([sys.executable, 'app.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Sistemi u startua me sukses!")
                break
            else:
                print(f"❌ Gabim në startim: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - sistemi po ngarkon...")
            break
        except Exception as e:
            print(f"❌ Gabim: {e}")
        
        if attempt < max_attempts - 1:
            print("⏳ Duke pritur 5 sekonda...")
            time.sleep(5)
    
    print("\n🌐 Sistemi është gati në http://localhost:9000")

if __name__ == "__main__":
    main()
