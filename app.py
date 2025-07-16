from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import cv2
import os
import json
import qrcode
from PIL import Image
import threading
import time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Try to import hardware dependencies, but don't fail if they're not available
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    print("⚠️  RPi.GPIO not available - running in test mode")
    HARDWARE_AVAILABLE = False

try:
    from pyzbar.pyzbar import decode
    BARCODE_AVAILABLE = True
except ImportError:
    print("⚠️  pyzbar not available - barcode scanning disabled")
    BARCODE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# GPIO Configuration (only if hardware is available)
if HARDWARE_AVAILABLE:
    GPIO.setmode(GPIO.BCM)
    ENTRY_BUTTON = 17  # GPIO 17 for entry button
    EXIT_BUTTON = 18   # GPIO 18 for exit button
    BARRIER_RELAY = 19   # GPIO 19 for entry barrier relay
    BARRIER_RELAY_EXIT = 20  # GPIO 20 for exit barrier relay

    GPIO.setup(ENTRY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(EXIT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BARRIER_RELAY, GPIO.OUT)
    GPIO.setup(BARRIER_RELAY_EXIT, GPIO.OUT)
else:
    # Mock GPIO pins for testing
    ENTRY_BUTTON = None
    EXIT_BUTTON = None
    BARRIER_RELAY = None
    BARRIER_RELAY_EXIT = None

# Database Models
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    entry_photo = db.Column(db.String(200), nullable=True)
    exit_photo = db.Column(db.String(200), nullable=True)
    is_inside = db.Column(db.Boolean, default=True)
    total_payment = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, used
    payment_time = db.Column(db.DateTime, nullable=True)
    payment_method = db.Column(db.String(20), nullable=True)  # cash, card, etc.

class ParkingSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hourly_rate = db.Column(db.Float, default=2.0)
    daily_rate = db.Column(db.Float, default=20.0)
    max_capacity = db.Column(db.Integer, default=50)
    camera_ip = db.Column(db.String(50), default='192.168.1.100')
    camera_username = db.Column(db.String(50), default='admin')
    camera_password = db.Column(db.String(50), default='admin')
    ticket_text = db.Column(db.Text, default='Faleminderit që përdorët parkingun tonë!')

class ParkingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(20))  # 'entry', 'exit', 'payment'
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    photo_path = db.Column(db.String(200), nullable=True)
    details = db.Column(db.Text, nullable=True)  # Additional details like payment amount, method, etc.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='operator')  # 'admin' or 'operator'
    name = db.Column(db.String(100), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RFIDCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(50), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # '1_month', '3_months', '6_months', '1_year'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'expired', 'blocked'
    max_entries = db.Column(db.Integer, default=1000)
    current_entries = db.Column(db.Integer, default=0)
    is_inside = db.Column(db.Boolean, default=False)  # True if card is currently inside parking
    last_entry_time = db.Column(db.DateTime, nullable=True)
    last_exit_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if card is valid and not expired"""
        return (self.status == 'active' and 
                self.end_date > datetime.utcnow() and 
                self.current_entries < self.max_entries)
    
    def can_enter(self):
        """Check if card can enter (not already inside)"""
        return self.is_valid() and not self.is_inside
    
    def can_exit(self):
        """Check if card can exit (currently inside)"""
        return self.is_inside
    
    def enter_parking(self):
        """Record entry"""
        if self.can_enter():
            self.is_inside = True
            self.last_entry_time = datetime.utcnow()
            self.current_entries += 1
            return True
        return False
    
    def exit_parking(self):
        """Record exit"""
        if self.can_exit():
            self.is_inside = False
            self.last_exit_time = datetime.utcnow()
            return True
        return False

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Ju nuk keni të drejta për të aksesuar këtë faqe', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize camera
def init_camera():
    try:
        # Try IP camera first
        settings = ParkingSettings.query.first()
        if settings and settings.camera_ip:
            camera_url = f"http://{settings.camera_username}:{settings.camera_password}@{settings.camera_ip}/video"
            cap = cv2.VideoCapture(camera_url)
        else:
            # Fallback to USB camera
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return None
        return cap
    except Exception as e:
        print(f"Camera initialization error: {e}")
        return None

# Capture photo
def capture_photo(vehicle_id, action):
    cap = init_camera()
    if cap is None:
        # Create a mock photo file for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photos/{action}_{vehicle_id}_{timestamp}.jpg"
        os.makedirs("photos", exist_ok=True)
        
        # Create a simple mock image
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (640, 480), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f"Mock Photo: {action} - Vehicle {vehicle_id}", fill='black')
            draw.text((50, 100), f"Timestamp: {timestamp}", fill='black')
            img.save(filename)
            return filename
        except Exception as e:
            print(f"Error creating mock photo: {e}")
            return None
    
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photos/{action}_{vehicle_id}_{timestamp}.jpg"
        os.makedirs("photos", exist_ok=True)
        cv2.imwrite(filename, frame)
        cap.release()
        return filename
    cap.release()
    return None

# Generate ticket with QR code
def generate_ticket(vehicle):
    ticket_data = {
        'ticket_number': vehicle.ticket_number,
        'plate_number': vehicle.plate_number,
        'entry_time': vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
        'entry_photo': vehicle.entry_photo
    }
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(ticket_data))
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_filename = f"tickets/{vehicle.ticket_number}.png"
    os.makedirs("tickets", exist_ok=True)
    qr_image.save(qr_filename)
    
    return qr_filename

# Calculate parking fee
def calculate_fee(entry_time, exit_time):
    duration = exit_time - entry_time
    hours = duration.total_seconds() / 3600
    
    settings = ParkingSettings.query.first()
    if not settings:
        return 0.0
    
    if hours <= 24:
        return hours * settings.hourly_rate
    else:
        days = duration.days + (duration.seconds / 86400)
        return days * settings.daily_rate

# GPIO Event Handlers
def entry_button_callback(channel):
    print("🔘 Butoni i hyrjes u shtyp!")
    # This will trigger ticket generation and barrier opening
    process_entry_button()

def exit_button_callback(channel):
    print("🔘 Butoni i daljes u shtyp!")
    # This will trigger ticket scanning and verification
    process_exit_button()

def process_entry_button():
    """Process entry button press - generate ticket and open barrier"""
    try:
        # Generate unique ticket number
        ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create vehicle entry (without plate number for now)
        vehicle = Vehicle(
            plate_number=f"UNKNOWN_{ticket_number[-6:]}",  # Temporary plate
            ticket_number=ticket_number,
            is_inside=True,
            payment_status='unpaid'
        )
        
        # Capture entry photo
        photo_path = capture_photo(vehicle.id, 'entry')
        if photo_path:
            vehicle.entry_photo = photo_path
        
        db.session.add(vehicle)
        db.session.commit()
        
        # Generate ticket with QR code
        ticket_path = generate_ticket(vehicle)
        
        # Print ticket
        print_ticket(vehicle)
        
        # Open barrier
        open_entry_barrier()
        
        print(f"✅ Bileta u gjenerua: {ticket_number}")
        
    except Exception as e:
        print(f"❌ Gabim në procesimin e hyrjes: {e}")

def process_exit_button():
    """Process exit button press - scan ticket and verify payment"""
    try:
        # Simulate QR code scanning
        scanned_ticket = scan_ticket()
        
        if scanned_ticket:
            vehicle = Vehicle.query.filter_by(ticket_number=scanned_ticket).first()
            
            if vehicle and vehicle.is_inside:
                if vehicle.payment_status == 'paid':
                    # Process exit
                    vehicle.exit_time = datetime.utcnow()
                    vehicle.is_inside = False
                    vehicle.payment_status = 'used'
                    
                    # Capture exit photo
                    photo_path = capture_photo(vehicle.id, 'exit')
                    if photo_path:
                        vehicle.exit_photo = photo_path
                    
                    db.session.commit()
                    
                    # Open exit barrier
                    open_exit_barrier()
                    
                    print(f"✅ Automjeti doli: {vehicle.plate_number}")
                else:
                    print(f"❌ Bileta nuk është paguar: {scanned_ticket}")
                    # Could add LED indicator or sound here
            else:
                print(f"❌ Bileta e pavlefshme: {scanned_ticket}")
        else:
            print("❌ Nuk u skanua asnjë bileta")
            
    except Exception as e:
        print(f"❌ Gabim në procesimin e daljes: {e}")

def scan_ticket():
    """Simulate QR code scanning - returns ticket number or None"""
    # In real implementation, this would read from QR scanner
    # For testing, return a random existing ticket
    vehicle = Vehicle.query.filter_by(is_inside=True).first()
    if vehicle:
        return vehicle.ticket_number
    return None

def print_ticket(vehicle):
    """Print ticket with QR code"""
    print("🖨️ Duke printuar billetën:")
    settings = ParkingSettings.query.first()
    ticket_text = settings.ticket_text if settings and settings.ticket_text else 'Faleminderit që përdorët parkingun tonë!'
    print(f"  Bileta: {vehicle.ticket_number}")
    print(f"  Koha e hyrjes: {vehicle.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  QR Code: tickets/{vehicle.ticket_number}.png")
    print(f"  Targa: {vehicle.plate_number}")
    print(f"  {ticket_text}")
    return True

def open_entry_barrier():
    if HARDWARE_AVAILABLE:
        GPIO.output(BARRIER_RELAY, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(BARRIER_RELAY, GPIO.LOW)
    else:
        print("🔓 Barriera e hyrjes u hap (simuluar)")
        time.sleep(2)
        print("🔒 Barriera e hyrjes u mbyll (simuluar)")

def open_exit_barrier():
    if HARDWARE_AVAILABLE:
        GPIO.output(BARRIER_RELAY_EXIT, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(BARRIER_RELAY_EXIT, GPIO.LOW)
    else:
        print("🔓 Barriera e daljes u hap (simuluar)")
        time.sleep(2)
        print("🔒 Barriera e daljes u mbyll (simuluar)")

# Routes
@app.route('/')
@login_required
def dashboard():
    vehicles_inside = Vehicle.query.filter_by(is_inside=True).count()
    unpaid_tickets = Vehicle.query.filter_by(is_inside=True, payment_status='unpaid').count()
    settings = ParkingSettings.query.first()
    max_capacity = settings.max_capacity if settings else 50
    
    recent_entries = Vehicle.query.filter_by(is_inside=True).order_by(Vehicle.entry_time.desc()).limit(10).all()
    recent_exits = Vehicle.query.filter_by(is_inside=False).order_by(Vehicle.exit_time.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         vehicles_inside=vehicles_inside,
                         unpaid_tickets=unpaid_tickets,
                         max_capacity=max_capacity,
                         recent_entries=recent_entries,
                         recent_exits=recent_exits)

@app.route('/entry', methods=['GET', 'POST'])
@login_required
def vehicle_entry():
    if request.method == 'POST':
        plate_number = request.form.get('plate_number')
        
        if not plate_number:
            flash('Ju lutem shkruani numrin e targës', 'error')
            return redirect(url_for('vehicle_entry'))
        
        # Check if vehicle is already inside
        existing_vehicle = Vehicle.query.filter_by(plate_number=plate_number, is_inside=True).first()
        if existing_vehicle:
            flash('Automjeti është tashmë brenda parkingut', 'error')
            return redirect(url_for('vehicle_entry'))
        
        # Create new vehicle entry
        ticket_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        vehicle = Vehicle(plate_number=plate_number, ticket_number=ticket_number, payment_status='unpaid')
        
        # Capture entry photo
        photo_path = capture_photo(vehicle.id, 'entry')
        if photo_path:
            vehicle.entry_photo = photo_path
        
        db.session.add(vehicle)
        db.session.commit()
        
        # Generate ticket
        ticket_path = generate_ticket(vehicle)
        
        # Open barrier
        open_entry_barrier()
        
        flash(f'Automjeti {plate_number} u regjistrua me sukses. Bileta: {ticket_number}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('entry.html')

@app.route('/exit', methods=['GET', 'POST'])
@login_required
def vehicle_exit():
    if request.method == 'POST':
        ticket_number = request.form.get('ticket_number')
        
        if not ticket_number:
            flash('Ju lutem shkruani numrin e biletës', 'error')
            return redirect(url_for('vehicle_exit'))
        
        vehicle = Vehicle.query.filter_by(ticket_number=ticket_number, is_inside=True).first()
        if not vehicle:
            flash('Numri i biletës është i pavlefshëm ose automjeti ka dalë tashmë', 'error')
            return redirect(url_for('vehicle_exit'))
        
        # Check if payment is made
        if vehicle.payment_status != 'paid':
            flash('Bileta nuk është paguar. Ju lutem kryeni pagesën te kabina e pagesave.', 'error')
            return redirect(url_for('vehicle_exit'))
        
        # Calculate fee
        vehicle.exit_time = datetime.utcnow()
        vehicle.total_payment = calculate_fee(vehicle.entry_time, vehicle.exit_time)
        vehicle.is_inside = False
        vehicle.payment_status = 'used'
        
        # Capture exit photo
        photo_path = capture_photo(vehicle.id, 'exit')
        if photo_path:
            vehicle.exit_photo = photo_path
        
        db.session.commit()
        
        # Open exit barrier
        open_exit_barrier()
        
        flash(f'Automjeti {vehicle.plate_number} doli. Tarifa: €{vehicle.total_payment:.2f}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('exit.html')

# New API endpoints for real system
@app.route('/api/verify_ticket', methods=['POST'])
def verify_ticket():
    """Verify ticket for exit"""
    data = request.get_json()
    ticket_number = data.get('ticket_number')
    
    if not ticket_number:
        return jsonify({'success': False, 'message': 'Numri i biletës është i detyrueshëm'})
    
    vehicle = Vehicle.query.filter_by(ticket_number=ticket_number, is_inside=True).first()
    
    if not vehicle:
        return jsonify({'success': False, 'message': 'Bileta e pavlefshme'})
    
    if vehicle.payment_status != 'paid':
        return jsonify({
            'success': False, 
            'message': 'Bileta nuk është paguar',
            'ticket_number': ticket_number,
            'entry_time': vehicle.entry_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'success': True,
        'message': 'Bileta e vlefshme',
        'ticket_number': ticket_number,
        'plate_number': vehicle.plate_number
    })

@app.route('/api/pay_ticket', methods=['POST'])
def pay_ticket():
    """Pay for ticket"""
    data = request.get_json()
    ticket_number = data.get('ticket_number')
    payment_method = data.get('payment_method', 'cash')
    
    if not ticket_number:
        return jsonify({'success': False, 'message': 'Numri i biletës është i detyrueshëm'})
    
    vehicle = Vehicle.query.filter_by(ticket_number=ticket_number, is_inside=True).first()
    
    if not vehicle:
        return jsonify({'success': False, 'message': 'Bileta e pavlefshme'})
    
    if vehicle.payment_status == 'paid':
        return jsonify({'success': False, 'message': 'Bileta është paguar tashmë'})
    
    # Calculate fee
    exit_time = datetime.utcnow()
    fee = calculate_fee(vehicle.entry_time, exit_time)
    
    # Update payment status
    vehicle.total_payment = fee
    vehicle.payment_status = 'paid'
    vehicle.payment_time = datetime.utcnow()
    vehicle.payment_method = payment_method
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Pagesa u krye me sukses',
        'ticket_number': ticket_number,
        'fee': fee,
        'payment_method': payment_method
    })

@app.route('/api/entry_button', methods=['POST'])
def entry_button():
    """Handle entry button press"""
    process_entry_button()
    return jsonify({'success': True, 'message': 'Butoni i hyrjes u shtyp'})

@app.route('/api/exit_button', methods=['POST'])
def exit_button():
    """Handle exit button press"""
    process_exit_button()
    return jsonify({'success': True, 'message': 'Butoni i daljes u shtyp'})

@app.route('/payment')
@login_required
def payment_page():
    """Payment page for operator"""
    unpaid_tickets = Vehicle.query.filter_by(is_inside=True, payment_status='unpaid').all()
    return render_template('payment.html', unpaid_tickets=unpaid_tickets)

@app.route('/api/vehicles')
def api_vehicles():
    """API endpoint to get all vehicles"""
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id,
        'plate_number': v.plate_number,
        'ticket_number': v.ticket_number,
        'entry_time': v.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
        'exit_time': v.exit_time.strftime('%Y-%m-%d %H:%M:%S') if v.exit_time else None,
        'is_inside': v.is_inside,
        'payment_status': v.payment_status,
        'total_payment': v.total_payment
    } for v in vehicles])

@app.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    try:
        if request.method == 'POST':
            settings = ParkingSettings.query.first()
            if not settings:
                settings = ParkingSettings()
                db.session.add(settings)
            settings.hourly_rate = float(request.form.get('hourly_rate', 2.0))
            settings.daily_rate = float(request.form.get('daily_rate', 20.0))
            settings.max_capacity = int(request.form.get('max_capacity', 50))
            settings.ticket_text = request.form.get('ticket_text', 'Faleminderit që përdorët parkingun tonë!')
            db.session.commit()
            flash('Cilësimet u ruajtën me sukses', 'success')
            return redirect(url_for('settings'))
        
        settings = ParkingSettings.query.first()
        if not settings:
            settings = ParkingSettings()
            db.session.add(settings)
            db.session.commit()
        return render_template('settings.html', settings=settings)
    except Exception as e:
        print(f"❌ Error in settings route: {e}")
        flash('Gabim në ngarkimin e cilësimeve', 'error')
        return redirect(url_for('dashboard'))

@app.route('/reports')
@admin_required
def reports():
    """Reports page"""
    try:
        total_vehicles = Vehicle.query.count()
        vehicles_inside = Vehicle.query.filter_by(is_inside=True).count()
        unpaid_tickets = Vehicle.query.filter_by(is_inside=True, payment_status='unpaid').count()
        total_revenue = db.session.query(db.func.sum(Vehicle.total_payment)).filter_by(payment_status='paid').scalar() or 0
        
        # Calculate today's exits
        today = datetime.now().date()
        today_exits = Vehicle.query.filter(
            Vehicle.exit_time >= today,
            Vehicle.is_inside == False
        ).count()
        
        return render_template('reports.html', 
                             total_vehicles=total_vehicles,
                             vehicles_inside=vehicles_inside,
                             unpaid_tickets=unpaid_tickets,
                             total_revenue=total_revenue,
                             today_exits=today_exits)
    except Exception as e:
        print(f"❌ Error in reports route: {e}")
        flash('Gabim në ngarkimin e raporteve', 'error')
        return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Mirëseerdhët, {user.name or user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Emri i përdoruesit ose fjalëkalimi është i gabuar', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Ju u çkyçët me sukses', 'success')
    return redirect(url_for('login'))

@app.route('/users')
@admin_required
def users():
    """User management page"""
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role', 'operator')
        
        if User.query.filter_by(username=username).first():
            flash('Emri i përdoruesit ekziston tashmë', 'error')
            return redirect(url_for('add_user'))
        
        user = User(username=username, name=name, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Përdoruesi {username} u shtua me sukses', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.name = request.form.get('name')
        user.role = request.form.get('role', 'operator')
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        db.session.commit()
        
        flash(f'Përdoruesi {user.username} u përditësua me sukses', 'success')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == session.get('user_id'):
        flash('Nuk mund të fshini llogarinë tuaj', 'error')
        return redirect(url_for('users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Përdoruesi {user.username} u fshi me sukses', 'success')
    return redirect(url_for('users'))

# RFID Card Management Routes
@app.route('/rfid_cards')
@admin_required
def rfid_cards():
    """RFID cards management page"""
    try:
        cards = RFIDCard.query.order_by(RFIDCard.created_at.desc()).all()
        return render_template('rfid_cards.html', cards=cards, now=datetime.utcnow())
    except Exception as e:
        print(f"❌ Error in rfid_cards route: {e}")
        flash('Gabim në ngarkimin e kartelave RFID', 'error')
        return redirect(url_for('dashboard'))

@app.route('/rfid_cards/add', methods=['GET', 'POST'])
@admin_required
def add_rfid_card():
    """Add new RFID card"""
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        owner_name = request.form.get('owner_name')
        payment_type = request.form.get('payment_type')
        
        if not all([card_number, owner_name, payment_type]):
            flash('Të gjitha fushat janë të detyrueshme', 'error')
            return redirect(url_for('add_rfid_card'))
        
        # Check if card number already exists
        if RFIDCard.query.filter_by(card_number=card_number).first():
            flash('Numri i kartelës ekziston tashmë', 'error')
            return redirect(url_for('add_rfid_card'))
        
        # Calculate end date based on payment type
        start_date = datetime.utcnow()
        if payment_type == '1_month':
            end_date = start_date + timedelta(days=30)
        elif payment_type == '3_months':
            end_date = start_date + timedelta(days=90)
        elif payment_type == '6_months':
            end_date = start_date + timedelta(days=180)
        elif payment_type == '1_year':
            end_date = start_date + timedelta(days=365)
        else:
            flash('Lloji i pagesës është i pavlefshëm', 'error')
            return redirect(url_for('add_rfid_card'))
        
        card = RFIDCard(
            card_number=card_number,
            owner_name=owner_name,
            payment_type=payment_type,
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(card)
        db.session.commit()
        flash('Kartela RFID u shtua me sukses', 'success')
        return redirect(url_for('rfid_cards'))
    
    return render_template('add_rfid_card.html')

@app.route('/rfid_cards/edit/<int:card_id>', methods=['GET', 'POST'])
@admin_required
def edit_rfid_card(card_id):
    """Edit RFID card"""
    card = RFIDCard.query.get_or_404(card_id)
    
    if request.method == 'POST':
        card.owner_name = request.form.get('owner_name')
        card.status = request.form.get('status')
        
        db.session.commit()
        flash('Kartela RFID u përditësua me sukses', 'success')
        return redirect(url_for('rfid_cards'))
    
    return render_template('edit_rfid_card.html', card=card)

@app.route('/rfid_cards/delete/<int:card_id>', methods=['POST'])
@admin_required
def delete_rfid_card(card_id):
    """Delete RFID card"""
    card = RFIDCard.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    flash('Kartela RFID u fshi me sukses', 'success')
    return redirect(url_for('rfid_cards'))

# RFID Card Entry/Exit API
@app.route('/api/rfid/entry', methods=['POST'])
def rfid_entry():
    """Handle RFID card entry"""
    data = request.get_json()
    card_number = data.get('card_number')
    
    if not card_number:
        return jsonify({'success': False, 'message': 'Numri i kartelës është i detyrueshëm'})
    
    card = RFIDCard.query.filter_by(card_number=card_number).first()
    
    if not card:
        return jsonify({'success': False, 'message': 'Kartela RFID nuk u gjet'})
    
    if not card.is_valid():
        if card.status == 'expired':
            return jsonify({'success': False, 'message': 'Kartela ka skaduar'})
        elif card.status == 'blocked':
            return jsonify({'success': False, 'message': 'Kartela është e bllokuar'})
        else:
            return jsonify({'success': False, 'message': 'Kartela nuk është e vlefshme'})
    
    if not card.can_enter():
        return jsonify({'success': False, 'message': 'Kartela është tashmë brenda parkingut'})
    
    if card.enter_parking():
        db.session.commit()
        open_entry_barrier()
        return jsonify({
            'success': True,
            'message': f'Mirëseerdhët, {card.owner_name}!',
            'card_number': card_number,
            'owner_name': card.owner_name
        })
    else:
        return jsonify({'success': False, 'message': 'Nuk mund të hyrë në parking'})

@app.route('/api/rfid/exit', methods=['POST'])
def rfid_exit():
    """Handle RFID card exit"""
    data = request.get_json()
    card_number = data.get('card_number')
    
    if not card_number:
        return jsonify({'success': False, 'message': 'Numri i kartelës është i detyrueshëm'})
    
    card = RFIDCard.query.filter_by(card_number=card_number).first()
    
    if not card:
        return jsonify({'success': False, 'message': 'Kartela RFID nuk u gjet'})
    
    if not card.can_exit():
        return jsonify({'success': False, 'message': 'Kartela nuk është brenda parkingut'})
    
    if card.exit_parking():
        db.session.commit()
        open_exit_barrier()
        return jsonify({
            'success': True,
            'message': f'Mirëupafshëm, {card.owner_name}!',
            'card_number': card_number,
            'owner_name': card.owner_name
        })
    else:
        return jsonify({'success': False, 'message': 'Nuk mund të dalë nga parkingu'})

@app.route('/rfid_test')
@login_required
def rfid_test():
    """RFID card testing page"""
    return render_template('rfid_test.html')

@app.route('/api/rfid/check', methods=['POST'])
def rfid_check():
    """Check RFID card status"""
    data = request.get_json()
    card_number = data.get('card_number')
    
    if not card_number:
        return jsonify({'success': False, 'message': 'Numri i kartelës është i detyrueshëm'})
    
    card = RFIDCard.query.filter_by(card_number=card_number).first()
    
    if not card:
        return jsonify({'success': False, 'message': 'Kartela RFID nuk u gjet'})
    
    # Update card status if expired
    if card.status == 'active' and card.end_date < datetime.utcnow():
        card.status = 'expired'
        db.session.commit()
    
    return jsonify({
        'success': True,
        'card': {
            'card_number': card.card_number,
            'owner_name': card.owner_name,
            'status': card.status,
            'is_valid': card.is_valid(),
            'can_enter': card.can_enter(),
            'can_exit': card.can_exit(),
            'is_inside': card.is_inside,
            'payment_type': card.payment_type,
            'start_date': card.start_date.strftime('%d/%m/%Y'),
            'end_date': card.end_date.strftime('%d/%m/%Y'),
            'current_entries': card.current_entries,
            'max_entries': card.max_entries
        }
    })

def update_expired_cards():
    """Update status of expired cards"""
    expired_cards = RFIDCard.query.filter(
        RFIDCard.status == 'active',
        RFIDCard.end_date < datetime.utcnow()
    ).all()
    
    for card in expired_cards:
        card.status = 'expired'
    
    if expired_cards:
        db.session.commit()
        print(f"✅ {len(expired_cards)} kartela të skaduara u përditësuan")

def check_and_fix_database():
    """Check and fix database issues automatically"""
    try:
        with app.app_context():
            # Check if database exists and is accessible
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful")
            
            # Check if all tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            required_tables = ['user', 'vehicle', 'parking_settings', 'parking_log', 'rfid_card']
            
            missing_tables = []
            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("🔄 Recreating database...")
                db.drop_all()
                db.create_all()
                print("✅ Database recreated successfully")
                return True
            
            # Check for missing columns
            try:
                # Test Vehicle model
                Vehicle.query.first()
                print("✅ Vehicle table OK")
            except Exception as e:
                print(f"⚠️  Vehicle table issue: {e}")
                print("🔄 Recreating database...")
                db.drop_all()
                db.create_all()
                print("✅ Database recreated successfully")
                return True
            
            try:
                # Test ParkingSettings model
                ParkingSettings.query.first()
                print("✅ ParkingSettings table OK")
            except Exception as e:
                print(f"⚠️  ParkingSettings table issue: {e}")
                print("🔄 Recreating database...")
                db.drop_all()
                db.create_all()
                print("✅ Database recreated successfully")
                return True
            
            try:
                # Test RFIDCard model
                RFIDCard.query.first()
                print("✅ RFIDCard table OK")
            except Exception as e:
                print(f"⚠️  RFIDCard table issue: {e}")
                print("🔄 Recreating database...")
                db.drop_all()
                db.create_all()
                print("✅ Database recreated successfully")
                return True
            
            print("✅ All database tables are OK")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("🔄 Recreating database...")
        try:
            with app.app_context():
                db.drop_all()
                db.create_all()
                print("✅ Database recreated successfully")
                return True
        except Exception as e2:
            print(f"❌ Failed to recreate database: {e2}")
            return False

def create_default_data():
    """Create default data after database recreation"""
    try:
        with app.app_context():
            # Create default users
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', name='Administrator', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                print("✅ Admin user created: admin/admin123")
            
            if not User.query.filter_by(username='operator').first():
                operator = User(username='operator', name='Operator', role='operator')
                operator.set_password('operator123')
                db.session.add(operator)
                print("✅ Operator user created: operator/operator123")
            
            # Create default settings
            if not ParkingSettings.query.first():
                settings = ParkingSettings(
                    hourly_rate=2.0,
                    daily_rate=20.0,
                    max_capacity=50,
                    ticket_text='Faleminderit që përdorët parkingun tonë!'
                )
                db.session.add(settings)
                print("✅ Default settings created")
            
            db.session.commit()
            print("✅ Default data created successfully")
            
    except Exception as e:
        print(f"❌ Error creating default data: {e}")

if __name__ == '__main__':
    print("🚗 Starting Parking Management System...")
    print("=" * 50)
    
    # Check and fix database
    db_recreated = check_and_fix_database()
    
    # Create default data if database was recreated
    if db_recreated:
        create_default_data()
    
    # Create default data if it doesn't exist
    with app.app_context():
        create_default_data()
        
        # Update expired cards
        try:
            update_expired_cards()
        except Exception as e:
            print(f"⚠️  Error updating expired cards: {e}")
        
        # Add GPIO event detection
        if HARDWARE_AVAILABLE:
            try:
                GPIO.add_event_detect(ENTRY_BUTTON, GPIO.FALLING, callback=entry_button_callback, bouncetime=300)
                GPIO.add_event_detect(EXIT_BUTTON, GPIO.FALLING, callback=exit_button_callback, bouncetime=300)
                print("✅ GPIO event detection configured")
            except Exception as e:
                print(f"⚠️  GPIO configuration error: {e}")
    
    print("✅ System initialization complete")
    print("🌐 Starting web server...")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=9000, debug=True) 