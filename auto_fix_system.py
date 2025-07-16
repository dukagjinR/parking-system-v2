#!/usr/bin/env python3
"""
Automatic System Fixer for Parking Management System
Checks and repairs common issues automatically
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def check_database_integrity():
    """Check and fix database integrity issues"""
    print("🔍 Kontrollimi i integritetit të databazës...")
    
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if database is corrupted
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] != 'ok':
                print(f"❌ Database {db_file} është e dëmtuar")
                backup_file = f"{db_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(db_file, backup_file)
                print(f"✅ Backup u krijua: {backup_file}")
                os.remove(db_file)
                print(f"🗑️  Database e dëmtuar u fshi: {db_file}")
            else:
                print(f"✅ Database {db_file} është në rregull")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Gabim në kontrollin e {db_file}: {e}")
            try:
                backup_file = f"{db_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(db_file, backup_file)
                print(f"✅ Backup u krijua: {backup_file}")
                os.remove(db_file)
                print(f"🗑️  Database problematike u fshi: {db_file}")
            except:
                print(f"⚠️  Nuk mund të fshihet {db_file}")

def check_required_files():
    """Check if all required files exist"""
    print("📁 Kontrollimi i file-ve të nevojshme...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/login.html',
        'templates/settings.html',
        'templates/reports.html',
        'templates/rfid_cards.html',
        'templates/add_rfid_card.html',
        'templates/edit_rfid_card.html',
        'templates/rfid_test.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"❌ Mungon: {file}")
        else:
            print(f"✅ Ekziston: {file}")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} file janë munguar!")
        return False
    else:
        print("✅ Të gjitha file-t e nevojshme ekzistojnë")
        return True

def check_directories():
    """Check and create required directories"""
    print("📂 Kontrollimi i direktoriave...")
    
    required_dirs = [
        'photos',
        'tickets', 
        'backups',
        'logs',
        'test_photos'
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ U krijua: {directory}")
        else:
            print(f"✅ Ekziston: {directory}")

def check_dependencies():
    """Check if required Python packages are installed"""
    print("📦 Kontrollimi i varësive...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'werkzeug',
        'jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Instaloni paketat munguese:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ Të gjitha varësitë janë instaluar")
        return True

def clean_temp_files():
    """Clean temporary files that might cause issues"""
    print("🧹 Pastrimi i file-ve të përkohshme...")
    
    temp_extensions = ['.pyc', '.pyo', '__pycache__']
    
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_dir = os.path.join(root, dir_name)
                shutil.rmtree(cache_dir)
                print(f"🗑️  U fshi: {cache_dir}")
        
        # Remove .pyc and .pyo files
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"🗑️  U fshi: {file_path}")

def create_startup_script():
    """Create a startup script that handles errors"""
    print("🚀 Krijimi i script-it të fillimit...")
    
    startup_script = '''#!/usr/bin/env python3
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
        print(f"\\n🔄 Përpjekja {attempt + 1}/{max_attempts}...")
        
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
    
    print("\\n🌐 Sistemi është gati në http://localhost:9000")

if __name__ == "__main__":
    main()
'''
    
    with open('start_system.py', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("✅ Script-i i fillimit u krijua: start_system.py")

def main():
    """Main function to run all checks and fixes"""
    print("🔧 Auto-Fix System për Parking Management")
    print("=" * 50)
    
    # Step 1: Clean temporary files
    clean_temp_files()
    
    # Step 2: Check database integrity
    check_database_integrity()
    
    # Step 3: Check required files
    files_ok = check_required_files()
    
    # Step 4: Check directories
    check_directories()
    
    # Step 5: Check dependencies
    deps_ok = check_dependencies()
    
    # Step 6: Create startup script
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("✅ Auto-fix përfundoi!")
    
    if files_ok and deps_ok:
        print("🎯 Sistemi është gati për startim")
        print("🚀 Ekzekutoni: python app.py")
        print("🌐 Ose: python start_system.py")
    else:
        print("⚠️  Ka probleme që duhen rregulluar manualisht")
        if not files_ok:
            print("   - Kontrolloni file-t munguese")
        if not deps_ok:
            print("   - Instaloni varësitë munguese")
    
    print("\n📋 Rekomandimet:")
    print("   1. Përdorni start_system.py për startim të sigurt")
    print("   2. Kontrolloni log-et nëse ka probleme")
    print("   3. Bëni backup të databazës rregullisht")

if __name__ == "__main__":
    main() 