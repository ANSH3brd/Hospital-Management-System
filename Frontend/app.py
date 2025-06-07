from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
import os
from functools import wraps
import secrets
import datetime
import random
import string
import traceback
import pymysql

# Import routes
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp
from routes.medical_record_routes import medical_record_bp
from routes.billing_routes import billing_bp
from routes.staff_routes import staff_bp, init_mysql
from routes.prescription_routes import prescription_bp

# Import get_db from models.db
from models.db import get_db, init_app

app = Flask(__name__)

# Secret key for session
app.secret_key = secrets.token_hex(16)

# MySQL Configuration - Updated to use the user's database with fallback to default
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # MySQL username
app.config['MYSQL_PASSWORD'] = 'iAf_49512'  # MySQL password
app.config['MYSQL_DB'] = 'hospital_db'  # Updated database name
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Check if the database exists, if not create it
def create_database_if_not_exists():
    try:
        # Connect to MySQL without specifying a database first
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check if hospital_db database exists
            cursor.execute("SHOW DATABASES LIKE 'hospital_db'")
            result = cursor.fetchone()
            
            if not result:
                print("Creating hospital_db database...")
                cursor.execute("CREATE DATABASE hospital_db")
                print("Database hospital_db created successfully")
            else:
                print("Database hospital_db already exists")
                
        connection.close()
        return True
    except Exception as e:
        print(f"Error checking/creating database: {str(e)}")
        print(traceback.format_exc())
        return False

# Create database if needed
create_database_if_not_exists()

# Initialize MySQL
mysql = MySQL(app)

# Register blueprints
app.register_blueprint(patient_bp, url_prefix='/patients')
app.register_blueprint(doctor_bp, url_prefix='/doctors')
app.register_blueprint(appointment_bp, url_prefix='/appointments')
app.register_blueprint(medical_record_bp, url_prefix='/medical-records')
app.register_blueprint(prescription_bp, url_prefix='/prescriptions')
app.register_blueprint(billing_bp, url_prefix='/billing')
app.register_blueprint(staff_bp, url_prefix='/staff')

# Initialize route modules with MySQL
init_mysql(mysql)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Doctor login required decorator
def doctor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('is_doctor') != True:
            flash('Please login as a doctor to access this page', 'danger')
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated_function

# Staff login required decorator
def staff_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('user_type') != 'staff':
            flash('Please login as staff to access this page', 'danger')
            return redirect(url_for('staff.login'))
        return f(*args, **kwargs)
    return decorated_function

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Handle database connection
def get_db_connection():
    try:
        conn = mysql.connection
        # Test the connection
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return conn
    except Exception as e:
        error_msg = f"Database connection error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return None

# Generate unique Patient ID - UPDATED to return integer
def generate_patient_id():
    # Get the current highest patient ID
    try:
        conn = mysql.connection
        if not conn:
            return 1  # Default if connection fails
            
        cur = conn.cursor()
        
        # First check if the Patient table exists
        cur.execute("SHOW TABLES LIKE 'Patient'")
        if cur.fetchone() is None:
            cur.close()
            return 1  # Default if table doesn't exist
            
        # Get the highest Patient_ID 
        cur.execute("SELECT MAX(Patient_ID) as max_id FROM Patient")
        result = cur.fetchone()
        
        if result and result['max_id']:
            # If there are existing patients, increment the ID
            next_id = int(result['max_id']) + 1
        else:
            # If no patients exist, start with 1
            next_id = 1
        
        cur.close()
        return next_id
        
    except Exception as e:
        # If query fails, use default
        print(f"Error in generate_patient_id: {str(e)}")
        print(traceback.format_exc())
        return 1

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form['dob']
            
            # Calculate age
            dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
            today = datetime.date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            
            contact_number = request.form['contact_number']
            address = request.form['address']
            email = request.form['email']
            blood_group = request.form['blood_group']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validate password match
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html', error='Passwords do not match')
            
            # Direct approach with self-contained execution
            try:
                print("Attempting registration with direct database access...")
                
                # Step 1: First ensure database exists
                # Connect to MySQL without specifying a database
                print("Checking if database exists...")
                conn_params = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'iAf_49512',
                    'charset': 'utf8mb4'
                }
                
                # Create the database if it doesn't exist
                connection = pymysql.connect(**conn_params)
                with connection.cursor() as cursor:
                    cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_db")
                connection.close()
                
                # Step 2: Connect to the database and ensure tables exist
                conn_params['database'] = 'hospital_db'
                conn_params['cursorclass'] = pymysql.cursors.DictCursor
                
                connection = pymysql.connect(**conn_params)
                with connection.cursor() as cursor:
                    # Create the tables with proper types if they don't exist
                    print("Creating tables if they don't exist...")
                    
                    # Create Patient table with INT Patient_ID
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Patient (
                            Patient_ID INT PRIMARY KEY,
                            Name VARCHAR(100) NOT NULL,
                            Gender VARCHAR(10),
                            Date_of_Birth DATE,
                            Age INT,
                            Contact_Number VARCHAR(15),
                            Address TEXT,
                            Email VARCHAR(100),
                            Blood_Group VARCHAR(5),
                            Medical_History TEXT,
                            Insurance_Details TEXT
                        )
                    """)
                    
                    # Create Patient_Login table with INT Patient_ID
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS Patient_Login (
                            Patient_ID INT PRIMARY KEY,
                            Passcode VARCHAR(100) NOT NULL
                        )
                    """)
                    
                    # Generate a unique patient ID (integer)
                    print("Generating unique patient ID...")
                    cursor.execute("SELECT MAX(Patient_ID) as max_id FROM Patient")
                    result = cursor.fetchone()
                    
                    if result and result['max_id'] is not None:
                        # Extract the number part and increment
                        patient_id = int(result['max_id']) + 1
                    else:
                        # No existing patients
                        patient_id = 1
                    
                    print(f"Generated Patient ID: {patient_id}")
                    
                    # Insert the new patient
                    print("Inserting new patient record...")
                    cursor.execute("""
                        INSERT INTO Patient (
                            Patient_ID, Name, Gender, Date_of_Birth, Age, 
                            Contact_Number, Address, Email, Blood_Group, 
                            Medical_History, Insurance_Details
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        patient_id, name, gender, dob, age, 
                        contact_number, address, email, blood_group, 
                        '', ''  # Empty medical history and insurance details
                    ))
                    
                    # Insert login credentials
                    print("Inserting login credentials...")
                    cursor.execute("""
                        INSERT INTO Patient_Login (Patient_ID, Passcode)
                        VALUES (%s, %s)
                    """, (patient_id, password))
                    
                    # Commit all changes
                    connection.commit()
                
                # Close the connection
                connection.close()
                
                # Success message
                flash(f'Registration successful! Your Patient ID is: {patient_id}', 'success')
                flash('Please login with your Patient ID and password', 'info')
                return redirect(url_for('login'))
                
            except Exception as e:
                error_msg = f"Registration error: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                flash(error_msg, 'danger')
                return render_template('register.html', error=error_msg)
                
        except Exception as e:
            # Catch any other exceptions
            error_msg = f"Unexpected error during registration: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return render_template('register.html', error=error_msg)
    
    # GET request - show registration form
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Get form fields
            username = request.form['username']
            password = request.form['password']
            
            print(f"Login attempt with Patient ID: {username}")
            
            # We need to ensure the database exists first
            if not create_database_if_not_exists():
                # Don't show error message
                return render_template('login.html')
                
            # Create direct MySQL connection using pymysql
            try:
                print("Getting direct database connection for login...")
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='iAf_49512',
                    database='hospital_db',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                print("Direct database connection established for login")
                
                with connection.cursor() as cursor:
                    # Check if Patient_Login table exists
                    print("Checking if Patient_Login table exists...")
                    cursor.execute("SHOW TABLES LIKE 'Patient_Login'")
                    if cursor.fetchone() is None:
                        print("Patient_Login table does not exist")
                        # Try checking for Patient table and direct Password field
                        cursor.execute("SHOW TABLES LIKE 'Patient'")
                        if cursor.fetchone() is None:
                            print("Patient table does not exist either")
                            connection.close()
                            return render_template('login.html')
                        
                        # Verify password
                        cursor.execute("DESCRIBE Patient")
                        columns = cursor.fetchall()
                        has_password = any(col['Field'] == 'Passcode' for col in columns)

                        if has_password:
                            # Get user directly from Patient table
                            try:
                                patient_id = int(username)
                            except ValueError:
                                print("Patient ID must be a number")
                                connection.close()
                                return render_template('login.html')

                            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [patient_id])
                            result = cursor.fetchone()

                            if result and 'Passcode' in result and result['Passcode'] == password:
                                # Login successful using Patient table Passcode
                                session['logged_in'] = True
                                session['username'] = username
                                session['user_type'] = 'patient'

                                print("Login successful via Patient table")
                                connection.close()
                                return redirect(url_for('dashboard'))
                            else:
                                print("Invalid credentials via Patient table")
                                connection.close()
                                return render_template('login.html')
                        else:
                            print("No Passcode field in Patient table")
                            connection.close()
                            return render_template('login.html')
                    
                    # Get user by username (Patient_ID) from Patient_Login table
                    print(f"Looking up Patient_ID in Patient_Login: {username}")

                    # Convert the username to integer for lookup
                    try:
                        patient_id = int(username)
                    except ValueError:
                        print("Patient ID must be a number")
                        connection.close()
                        return render_template('login.html')

                    cursor.execute("SELECT * FROM Patient_Login WHERE Patient_ID = %s", [patient_id])
                    result = cursor.fetchone()

                    if result:
                        # Get stored password - check both password and Passcode fields
                        stored_password = None
                        if 'Passcode' in result and result['Passcode']:
                            stored_password = result['Passcode']
                        elif 'password' in result and result['password']:
                            stored_password = result['password']
                        elif 'Password' in result and result['Password']:
                            stored_password = result['Password']

                        print(f"User found, comparing passwords. Input: {password}, Stored: {stored_password}")

                        # Compare passwords
                        if password == stored_password:
                            # Passed
                            session.clear()  # Clear any existing session data
                            session['logged_in'] = True
                            session['username'] = username
                            session['user_type'] = 'patient'
                            session['patient_id'] = patient_id
                            
                            print(f"Login successful! Session data: {session}")
                            # flash('You are now logged in', 'success')
                            connection.close()
                            return redirect(url_for('dashboard'))
                        else:
                            print("Invalid password")
                            connection.close()
                            return render_template('login.html')
                    else:
                        print("Patient ID not found in Patient_Login table")
                        connection.close()
                        return render_template('login.html')
                        
            except Exception as e:
                error_msg = f"Login database error: {str(e)}"
                print(error_msg)
                print(traceback.format_exc())
                return render_template('login.html')
                
        except Exception as e:
            error_msg = f"Unexpected error during login: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return render_template('login.html')
    
    return render_template('login.html')

# Doctor Login Route
@app.route('/doctor-login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        try:
            # Get form data
            doctor_id = request.form['doctor_id']
            password = request.form['doctor_password']
            
            # Ensure database exists
            if not create_database_if_not_exists():
                return render_template('doctor_login.html')
            
            # Connect to database directly to ensure it works
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='iAf_49512',
                database='hospital_db',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with connection.cursor() as cursor:
                # Get doctor by ID
                cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [doctor_id])
                doctor = cursor.fetchone()
                
                if doctor:
                    # Verify password
                    if password == doctor['Passcode']:
                        # Set session variables
                        session['logged_in'] = True
                        session['is_doctor'] = True
                        session['doctor_id'] = doctor['Doctor_ID']
                        session['doctor_name'] = doctor['Name']
                        session['user_type'] = 'doctor'
                        
                        print(f"Doctor login successful. Session data: {session}")
                        connection.close()
                        
                        # Redirect to doctor dashboard
                        return redirect(url_for('doctor_dashboard'))
                    else:
                        connection.close()
                        return render_template('doctor_login.html')
                else:
                    connection.close()
                    return render_template('doctor_login.html')
                    
        except Exception as e:
            print(f"Doctor login error: {str(e)}")
            print(traceback.format_exc())
            return render_template('doctor_login.html')
    
    return render_template('doctor_login.html')

# Dashboard route - UPDATED to show only patient data
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        print(f"Dashboard access - Session data: {session}")
        
        # We need to ensure the database exists first
        if not create_database_if_not_exists():
            print("Failed to connect to database")
            return render_template('dashboard.html', 
                                  patient_details={},
                                  appointments=[],
                                  bills=[],
                                  doctors=[],
                                  prescriptions=[])
            
        # Get logged in user's Patient_ID
        try:
            patient_id = int(session['username'])
            print(f"Patient ID from session: {patient_id}")
        except (KeyError, ValueError) as e:
            print(f"Error getting patient ID from session: {str(e)}")
            print(f"Session data: {session}")
            if 'patient_id' in session:
                patient_id = session['patient_id']
                print(f"Using patient_id from session: {patient_id}")
            else:
                print("No valid patient ID found in session")
                return redirect(url_for('login'))
        
        # Create direct MySQL connection using pymysql
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Get patient details
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [patient_id])
            patient_details = cursor.fetchone()
            
            if not patient_details:
                print(f"No patient found with ID {patient_id}")
                connection.close()
                return redirect(url_for('login'))
                
            print(f"Patient details found: {patient_details['Name']}")
            
            # Get all appointments for this patient
            cursor.execute("SHOW TABLES LIKE 'Appointment'")
            if cursor.fetchone() is None:
                appointments = []
            else:
                # Get all appointments for this patient
                cursor.execute("""
                    SELECT a.*, p.Name as PatientName, d.Name as DoctorName 
                    FROM Appointment a
                    LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
                    LEFT JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
                    WHERE a.Patient_ID = %s
                    ORDER BY a.Appointment_Date DESC, a.Appointment_Time DESC
                """, [patient_id])
                appointments = cursor.fetchall()
            
            # Get all bills for this patient
            cursor.execute("SHOW TABLES LIKE 'Billing'")
            if cursor.fetchone() is None:
                bills = []
            else:
                cursor.execute("""
                    SELECT b.*, p.Name as PatientName
                    FROM Billing b
                    LEFT JOIN Patient p ON b.Patient_ID = p.Patient_ID
                    WHERE b.Patient_ID = %s
                    ORDER BY b.Bill_Date DESC
                """, [patient_id])
                bills = cursor.fetchall()
            
            # Get all prescriptions for this patient
            cursor.execute("SHOW TABLES LIKE 'Prescription'")
            if cursor.fetchone() is None:
                prescriptions = []
            else:
                cursor.execute("""
                    SELECT p.*, d.Name as DoctorName, d.Specialization 
                    FROM Prescription p
                    LEFT JOIN Doctor d ON p.Doctor_ID = d.Doctor_ID
                    WHERE p.Patient_ID = %s
                    ORDER BY p.Prescription_Date DESC
                """, [patient_id])
                prescriptions = cursor.fetchall()
            
            # Get doctors for appointment booking
            cursor.execute("SHOW TABLES LIKE 'Doctor'")
            if cursor.fetchone() is None:
                doctors = []
            else:
                cursor.execute("SELECT * FROM Doctor ORDER BY Name")
                doctors = cursor.fetchall()
        
        # Close connection
        connection.close()
        
        print("Successfully loaded dashboard data, rendering template")
        return render_template('dashboard.html', 
                              patient_details=patient_details,
                              appointments=appointments,
                              bills=bills,
                              doctors=doctors,
                              prescriptions=prescriptions)
                              
    except Exception as e:
        error_msg = f'Error retrieving dashboard data: {str(e)}'
        print(error_msg)
        print(traceback.format_exc())
        
        # Render an empty dashboard rather than redirecting
        return render_template('dashboard.html', 
                              patient_details={},
                              appointments=[],
                              bills=[],
                              doctors=[],
                              prescriptions=[])

# Doctor Dashboard route
@app.route('/doctor-dashboard')
@doctor_login_required
def doctor_dashboard():
    try:
        print(f"Session data: {session}")

        # Ensure database exists
        if not create_database_if_not_exists():
            # Don't flash error, just render dashboard
            return render_template('doctor_dashboard.html', 
                doctor_details={"Doctor_ID": session.get('doctor_id'), "Name": session.get('doctor_name')},
                appointments=[], 
                today_appointments=0,
                total_patients=0,
                pending_appointments=0,
                today=datetime.datetime.now().strftime('%Y-%m-%d')
            )

        # Connect to database directly to ensure it works
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Get today's date for prescription form
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        with connection.cursor() as cursor:
            # Get doctor details
            doctor_id = session.get('doctor_id')
            cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [doctor_id])
            doctor_details = cursor.fetchone()
            
            if not doctor_details:
                connection.close()
                # Create a default doctor details object from session
                doctor_details = {
                    "Doctor_ID": session.get('doctor_id'),
                    "Name": session.get('doctor_name'),
                    "Specialization": "Unknown",
                    "Experience": 0,
                    "Email": "",
                    "Contact_Number": ""
                }
            
            # Get doctor's appointments with patient details
            cursor.execute("SHOW TABLES LIKE 'Appointment'")
            if cursor.fetchone() is None:
                appointments = []
            else:
                try:
                    cursor.execute("""
                        SELECT a.*, p.Name as PatientName, p.Age, p.Gender, p.Contact_Number, p.Blood_Group
                        FROM Appointment a
                        JOIN Patient p ON a.Patient_ID = p.Patient_ID
                        WHERE a.Doctor_ID = %s
                        ORDER BY a.Appointment_Date DESC, a.Appointment_Time DESC
                    """, [doctor_id])
                    appointments = cursor.fetchall()
                except Exception as e:
                    print(f"Error fetching appointments: {str(e)}")
                    appointments = []
            
            # Set default values for stats
            today_appointments = 0
            total_patients = 0
            pending_appointments = 0
        
        # Close connection
        connection.close()
        
        return render_template('doctor_dashboard.html', 
                            doctor_details=doctor_details,
                            appointments=appointments,
                            today_appointments=today_appointments,
                            total_patients=total_patients,
                            pending_appointments=pending_appointments,
                            today=today)
                            
    except Exception as e:
        error_msg = f'Error retrieving doctor dashboard data: {str(e)}'
        print(error_msg)
        print(traceback.format_exc())
        
        # Just render the dashboard with minimal data
        return render_template('doctor_dashboard.html',
                            doctor_details={"Doctor_ID": session.get('doctor_id'), "Name": session.get('doctor_name')},
                            appointments=[],
                            today_appointments=0,
                            total_patients=0,
                            pending_appointments=0,
                            today=datetime.datetime.now().strftime('%Y-%m-%d'))

# Book Appointment route with billing based on doctor's charges - fixed for case sensitivity
@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    try:
        # Get logged in user's Patient_ID
        patient_id = int(session['username'])
        
        # Create direct MySQL connection using pymysql
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        if request.method == 'POST':
            # Process the appointment booking form
            doctor_id = request.form['doctor_id']
            appointment_date = request.form['appointment_date']
            appointment_time = request.form['appointment_time']
            reason = request.form['reason']
            
            with connection.cursor() as cursor:
                # Get doctor details including charges
                cursor.execute("SELECT Name, Specialization, Charges FROM Doctor WHERE Doctor_ID = %s", [doctor_id])
                doctor = cursor.fetchone()
                doctor_name = doctor['Name'] if doctor else "Unknown Doctor"
                doctor_specialization = doctor['Specialization'] if doctor else "Unknown Specialization"
                
                # Debug output to check what's in the doctor record
                print(f"Doctor details: {doctor}")
                
                # Use doctor's charges or default if not available
                doctor_charges = 500.00  # Default value
                if doctor and 'Charges' in doctor and doctor['Charges'] is not None:
                    try:
                        doctor_charges = float(doctor['Charges'])
                        print(f"Using doctor charges: {doctor_charges}")
                    except (ValueError, TypeError) as e:
                        print(f"Error converting Charges to float: {e}. Using default of 500.00")
                else:
                    print("Doctor Charges not found. Using default of 500.00")
                
                # 1. Insert new appointment
                cursor.execute("""
                    INSERT INTO Appointment 
                    (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time, Status, Reason) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    patient_id, doctor_id, appointment_date, appointment_time, 'Scheduled', reason
                ))
                connection.commit()
                
                # Get the last inserted appointment ID
                appointment_id = cursor.lastrowid
                
                # 2. Check the exact column names in the Billing table
                cursor.execute("DESCRIBE Billing")
                columns = cursor.fetchall()
                
                # Create a case-insensitive mapping of column names
                column_map = {}
                for col in columns:
                    column_map[col['Field'].lower()] = col['Field']
                
                print(f"Actual billing table columns: {column_map}")
                
                # Find the actual column names (respecting case)
                total_amount_col = column_map.get('total_amount') or column_map.get('total_amount')
                purpose_col = column_map.get('purpose')
                patient_id_col = column_map.get('patient_id')
                appointment_id_col = column_map.get('appointment_id')
                bill_date_col = column_map.get('bill_date')
                payment_status_col = column_map.get('payment_status')
                
                # Build the SQL query with the exact column names
                fields = []
                values = []
                
                if patient_id_col:
                    fields.append(patient_id_col)
                    values.append(patient_id)
                
                if appointment_id_col:
                    fields.append(appointment_id_col)
                    values.append(appointment_id)
                
                if bill_date_col:
                    fields.append(bill_date_col)
                    values.append(datetime.datetime.now().strftime('%Y-%m-%d'))
                
                if total_amount_col:
                    fields.append(total_amount_col)
                    values.append(doctor_charges)
                
                if payment_status_col:
                    fields.append(payment_status_col)
                    values.append('Pending')
                
                if purpose_col:
                    fields.append(purpose_col)
                    values.append("Registration fees")
                
                # Construct and execute the SQL query
                if fields and values:
                    fields_str = ', '.join(fields)
                    placeholders = ', '.join(['%s'] * len(values))
                    
                    sql = f"INSERT INTO Billing ({fields_str}) VALUES ({placeholders})"
                    print(f"Executing SQL: {sql}")
                    cursor.execute(sql, values)
                    connection.commit()
                    print(f"Billing record created with fields: {fields}")
                else:
                    print("No valid fields found for Billing table.")
            
            # Close connection
            connection.close()
            
            flash('Appointment booked successfully! A consultation fee has been added to your billing.', 'success')
            return redirect(url_for('dashboard'))
        
        # GET request - display the booking form
        with connection.cursor() as cursor:
            # Get available doctors with their charges
            cursor.execute("SELECT * FROM Doctor ORDER BY Name")
            doctors = cursor.fetchall()
            
            # Get patient details
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [patient_id])
            patient = cursor.fetchone()
        
        # Close connection
        connection.close()
        
        # Check if doctors exist
        if not doctors:
            flash('No doctors available in the system. Please contact the administrator.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Get today's date for the date input's min attribute
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        return render_template('book_appointment.html', doctors=doctors, patient=patient, today=today)
    
    except Exception as e:
        error_msg = f"Error processing appointment booking: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))

# Reset database route - for fixing schema issues
@app.route('/reset-database', methods=['GET'])
def reset_database():
    try:
        # Connect to MySQL without database first
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # First ensure the database exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_db")
        
        connection.close()
        
        # Now connect to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            print("Recreating database schema...")
            
            # Drop existing tables in reverse order to avoid foreign key constraints
            cursor.execute("DROP TABLE IF EXISTS Patient_Login")
            cursor.execute("DROP TABLE IF EXISTS Patient")
            
            # Create the Patient table with INT Patient_ID
            print("Creating Patient table...")
            cursor.execute("""
                CREATE TABLE Patient (
                    Patient_ID INT PRIMARY KEY,
                    Name VARCHAR(100) NOT NULL,
                    Gender VARCHAR(10),
                    Date_of_Birth DATE,
                    Age INT,
                    Contact_Number VARCHAR(15),
                    Address TEXT,
                    Email VARCHAR(100),
                    Blood_Group VARCHAR(5),
                    Medical_History TEXT,
                    Insurance_Details TEXT
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Create the Patient_Login table with INT Patient_ID
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Patient_Login (
                    Patient_ID INT PRIMARY KEY,
                    Passcode VARCHAR(100) NOT NULL,
                    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Create Doctor table
            print("Creating Doctor table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Doctor (
                    Doctor_ID VARCHAR(10) PRIMARY KEY,
                    Name VARCHAR(100) NOT NULL,
                    Specialization VARCHAR(100),
                    Phone VARCHAR(15),
                    Email VARCHAR(100),
                    Charges DECIMAL(10,2),
                    Passcode VARCHAR(100)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Create Appointment table with proper column names
            print("Creating Appointment table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Appointment (
                    Appointment_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Patient_ID INT,
                    Doctor_ID VARCHAR(10),
                    Appointment_Date DATE,
                    Appointment_Time TIME,
                    Status VARCHAR(20),
                    Reason TEXT,
                    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                    FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Create Billing table with proper column names
            print("Creating Billing table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Billing (
                    Bill_ID INT AUTO_INCREMENT PRIMARY KEY,
                    Patient_ID INT,
                    Appointment_ID INT NULL,
                    Bill_Date DATE,
                    Total_Amount DECIMAL(10,2),
                    Purpose VARCHAR(255),
                    Payment_Status VARCHAR(20),
                    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                    FOREIGN KEY (Appointment_ID) REFERENCES Appointment(Appointment_ID) ON DELETE SET NULL
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            """)
            
            # Commit changes
            connection.commit()
        
        # Close connection
        connection.close()
        
        flash('Database tables reset successfully', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        error_msg = f"Error resetting database: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('index'))

# Create doctor_login.html template route (for development only - remove in production)
@app.route('/create-doctor-login-template')
def create_doctor_login_template():
    try:
        with open('templates/doctor_login.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Login - Hospital Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .login-container {
            max-width: 500px;
            margin: 100px auto;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            border-radius: 10px 10px 0 0;
            font-weight: bold;
        }
        .btn-success {
            background-color: #198754;
            border: none;
        }
        .btn-success:hover {
            background-color: #157347;
        }
    </style>
</head>
<body>
    <div class="container login-container">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h3 class="text-center"><i class="fas fa-user-md me-2"></i>Doctor Login</h3>
            </div>
            <div class="card-body">
                {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                {% endif %}
                
                <form action="{{ url_for('doctor_login') }}" method="post">
                    <div class="mb-3">
                        <label for="doctor_id" class="form-label">Doctor ID</label>
                        <input type="text" class="form-control" id="doctor_id" name="doctor_id" placeholder="Enter your Doctor ID" required>
                    </div>
                    <div class="mb-3">
                        <label for="doctor_password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="doctor_password" name="doctor_password" placeholder="Enter your password" required>
                    </div>
                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-success btn-lg">Login</button>
                    </div>
                </form>
                
                <div class="mt-3 text-center">
                    <a href="{{ url_for('index') }}" class="text-decoration-none">Back to Home</a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')
        
        flash('Doctor login template created successfully', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        error_msg = f"Error creating template: {str(e)}"
        print(error_msg)
        return error_msg

# Create doctor_dashboard.html template route (for development only - remove in production)
@app.route('/create-doctor-dashboard-template')
def create_doctor_dashboard_template():
    try:
        with open('templates/doctor_dashboard.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Dashboard - Hospital Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .dashboard-header {
            background-color: #198754;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
        }
        .card-header {
            border-radius: 10px 10px 0 0;
            font-weight: bold;
        }
        .table-responsive {
            padding: 0 15px;
        }
        .doctor-info {
            background-color: #f1fff8;
            border-left: 4px solid #198754;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 5px;
        }
        .btn-success {
            background-color: #198754;
            border: none;
        }
        .btn-success:hover {
            background-color: #157347;
        }
        .doctor-id {
            font-weight: bold;
            color: #198754;
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">Hospital Management System</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="{{ url_for('doctor_dashboard') }}">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Dashboard Header -->
    <div class="dashboard-header">
        <div class="container">
            <h1><i class="fas fa-user-md me-2"></i>Doctor Dashboard</h1>
            <p class="lead">Welcome to your professional dashboard, Dr. {{ doctor_details.Name }}</p>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Doctor Information -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="doctor-info">
                    <h4>Doctor Information</h4>
                    <div class="row">
                        <div class="col-md-3">
                            <p><strong>ID:</strong> <span class="doctor-id">{{ doctor_details.Doctor_ID }}</span></p>
                        </div>
                        <div class="col-md-3">
                            <p><strong>Name:</strong> {{ doctor_details.Name }}</p>
                        </div>
                        <div class="col-md-3">
                            <p><strong>Specialization:</strong> {{ doctor_details.Specialization }}</p>
                        </div>
                        <div class="col-md-3">
                            <p><strong>Contact:</strong> {{ doctor_details.Phone }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card text-center bg-light">
                    <div class="card-body">
                        <h5 class="card-title text-success">Today's Appointments</h5>
                        <h1 class="display-4">{{ todays_count }}</h1>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card text-center bg-light">
                    <div class="card-body">
                        <h5 class="card-title text-success">Total Patients</h5>
                        <h1 class="display-4">{{ total_patients }}</h1>
                    </div>
                </div>
            </div>
        </div>

        <!-- Appointments Section -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4><i class="fas fa-calendar-check me-2"></i>Your Appointments</h4>
                    </div>
                    <div class="card-body">
                        {% if appointments %}
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead>
                                        <tr>
                                            <th>Patient Name</th>
                                            <th>Age</th>
                                            <th>Gender</th>
                                            <th>Contact</th>
                                            <th>Blood Group</th>
                                            <th>Date</th>
                                            <th>Time</th>
                                            <th>Reason</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for appointment in appointments %}
                                            <tr>
                                                <td>{{ appointment.PatientName }}</td>
                                                <td>{{ appointment.Age }}</td>
                                                <td>{{ appointment.Gender }}</td>
                                                <td>{{ appointment.Contact_Number }}</td>
                                                <td>{{ appointment.Blood_Group }}</td>
                                                <td>{{ appointment.Appointment_Date }}</td>
                                                <td>{{ appointment.Appointment_Time }}</td>
                                                <td>{{ appointment.Reason }}</td>
                                                <td>
                                                    <span class="badge {% if appointment.Status == 'Scheduled' %}bg-primary{% elif appointment.Status == 'Completed' %}bg-success{% else %}bg-danger{% endif %}">
                                                        {{ appointment.Status }}
                                                    </span>
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <div class="alert alert-info">
                                You have no appointments scheduled.
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')
        
        flash('Doctor dashboard template created successfully', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        error_msg = f"Error creating template: {str(e)}"
        print(error_msg)
        return error_msg

# Debug route to check session
@app.route('/debug-session')
def debug_session():
    session_info = {key: str(value) for key, value in session.items()}
    return jsonify(session_info)

# Debug route to create a test patient with ID 110
@app.route('/create-test-patient')
def create_test_patient():
    try:
        # Connect to database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Create a test patient with ID 110 if it doesn't exist
        with connection.cursor() as cursor:
            # Check if Patient table exists, create if not
            cursor.execute("SHOW TABLES LIKE 'Patient'")
            if cursor.fetchone() is None:
                cursor.execute("""
                    CREATE TABLE Patient (
                        Patient_ID INT PRIMARY KEY,
                        Name VARCHAR(100) NOT NULL,
                        Gender VARCHAR(10),
                        Date_of_Birth DATE,
                        Age INT,
                        Contact_Number VARCHAR(15),
                        Address TEXT,
                        Email VARCHAR(100),
                        Blood_Group VARCHAR(5),
                        Medical_History TEXT,
                        Insurance_Details TEXT
                    )
                """)
                connection.commit()
                
            # Check if patient with ID 110 exists
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = 110")
            if not cursor.fetchone():
                # Insert test patient with ID 110
                cursor.execute("""
                    INSERT INTO Patient (
                        Patient_ID, Name, Gender, Date_of_Birth, Age, 
                        Contact_Number, Address, Email, Blood_Group, 
                        Medical_History, Insurance_Details
                    ) VALUES (
                        110, 'Priyanshu Kumar Singh', 'Male', '2000-01-01', 23,
                        '9876543210', '123 Test Address', 'priyanshu@example.com', 'O+',
                        'No significant medical history', 'Insurance ID: 12345'
                    )
                """)
                connection.commit()
                result = "Test patient created with ID 110"
            else:
                # Update existing patient with ID 110 to ensure all data is set correctly
                cursor.execute("""
                    UPDATE Patient SET
                        Name = 'Priyanshu Kumar Singh',
                        Gender = 'Male',
                        Date_of_Birth = '2000-01-01',
                        Age = 23,
                        Contact_Number = '9876543210',
                        Address = '123 Test Address',
                        Email = 'priyanshu@example.com',
                        Blood_Group = 'O+',
                        Medical_History = 'No significant medical history',
                        Insurance_Details = 'Insurance ID: 12345'
                    WHERE Patient_ID = 110
                """)
                connection.commit()
                result = "Existing patient with ID 110 updated with complete information"
                
        # Close connection
        connection.close()
        
        return result
        
    except Exception as e:
        error_msg = f'Error creating/updating test patient: {str(e)}'
        print(error_msg)
        print(traceback.format_exc())
        return error_msg

# Debug route to check patient data
@app.route('/debug-patient/<int:id>')
def debug_patient(id):
    try:
        # Connect to database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Prepare result
        result = {
            'status': 'success',
            'message': 'Patient data check'
        }
        
        with connection.cursor() as cursor:
            # Check if Patient table exists
            cursor.execute("SHOW TABLES LIKE 'Patient'")
            if cursor.fetchone() is None:
                result['error'] = 'Patient table does not exist'
                return jsonify(result), 500
            
            # Get table structure
            cursor.execute("DESCRIBE Patient")
            columns = cursor.fetchall()
            result['table_structure'] = [{'name': col['Field'], 'type': col['Type']} for col in columns]
            
            # Check for patient with specified ID
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [id])
            patient = cursor.fetchone()
            
            if patient:
                # Convert any non-serializable types (like datetime) to string
                for key, value in patient.items():
                    if hasattr(value, 'isoformat'):  # datetime objects
                        patient[key] = value.isoformat()
                result['patient_data'] = patient
            else:
                result['error'] = f'No patient found with ID {id}'
                
            # Get all patient IDs for reference
            cursor.execute("SELECT Patient_ID FROM Patient")
            patients = cursor.fetchall()
            result['all_patient_ids'] = [p['Patient_ID'] for p in patients]
        
        # Close connection
        connection.close()
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'Error in debug route: {str(e)}'
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': error_msg,
            'traceback': traceback.format_exc()
        }), 500

# Get patient data as JSON for doctors dashboard
@app.route('/patients/api/<int:id>')
def get_patient_api(id):
    # Removed login_required to make debugging easier
    try:
        # Simple direct database connection
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Use a simplified query that doesn't rely on table joins or complex logic
        with connection.cursor() as cursor:
            # Query the patient by ID - being explicit about which columns we want
            cursor.execute("""
                SELECT 
                    Patient_ID, 
                    Name, 
                    Gender, 
                    Age, 
                    Contact_Number, 
                    Blood_Group, 
                    Medical_History
                FROM Patient 
                WHERE Patient_ID = %s
            """, [id])
            patient_data = cursor.fetchone()
            
            # If patient not found, return a 404
            if not patient_data:
                connection.close()
                return jsonify({"error": "Patient not found"}), 404
        
        # Close the connection
        connection.close()
        
        # Print the data we received from the database for debugging
        print(f"Patient data received from database: {patient_data}")
        
        # Format the response exactly as the frontend expects it, using the exact column names
        response = {
            "Patient_ID": patient_data.get("Patient_ID", id),
            "Name": patient_data.get("Name", "Unknown"),
            "Age": patient_data.get("Age", "N/A"),
            "Gender": patient_data.get("Gender", "N/A"),
            "Blood_Group": patient_data.get("Blood_Group", "N/A"),
            "Contact_Number": patient_data.get("Contact_Number", "N/A"),
            "Medical_History": patient_data.get("Medical_History", "No medical history available")
        }
        
        # Print the final response for debugging
        print(f"Sending response: {response}")
        
        # Return the response
        return jsonify(response)
    
    except Exception as e:
        # Log the error details
        print(f"Error in patient API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a friendly error response
        return jsonify({"error": "Database error", "message": str(e)}), 500

# Test API route
@app.route('/test-api')
def test_api():
    return render_template('test_api.html')

# API endpoint for doctor dashboard to get patient details
@app.route('/doctor/patient-details/<int:id>')
def doctor_get_patient_details(id):
    try:
        # Connect directly to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Get patient details with fixed column selection
            cursor.execute("""
                SELECT 
                    Patient_ID, 
                    Name, 
                    Age, 
                    Gender, 
                    Blood_Group, 
                    Contact_Number, 
                    Email,
                    Address,
                    Medical_History
                FROM Patient 
                WHERE Patient_ID = %s
            """, [id])
            patient = cursor.fetchone()
            
            if not patient:
                connection.close()
                return jsonify({
                    "error": "Patient not found",
                    "Patient_ID": id,
                    "Name": "Unknown",
                    "Age": "N/A",
                    "Gender": "N/A",
                    "Blood_Group": "N/A",
                    "Contact_Number": "N/A",
                    "Email": "N/A",
                    "Address": "N/A",
                    "Medical_History": "No medical history available"
                }), 404
        
        # Close the connection
        connection.close()
        
        # Debugging
        print(f"Patient data for doctor dashboard: {patient}")
        
        # Return the patient data
        return jsonify(patient)
        
    except Exception as e:
        print(f"Error fetching patient details for doctor: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return default values on error
        return jsonify({
            "error": str(e),
            "Patient_ID": id,
            "Name": "Error",
            "Age": "N/A",
            "Gender": "N/A",
            "Blood_Group": "N/A",
            "Contact_Number": "N/A",
            "Email": "N/A",
            "Address": "N/A",
            "Medical_History": "Error loading patient data"
        }), 500

# Staff login route (to handle the url_for in the template)
@app.route('/staff-login')
def staff_login():
    return redirect(url_for('staff.login'))

# Get patient prescriptions for doctor dashboard
@app.route('/prescriptions/patient/<int:id>')
def get_patient_prescriptions(id):
    try:
        # Connect directly to the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check if Prescription table exists
            cursor.execute("SHOW TABLES LIKE 'Prescription'")
            if cursor.fetchone() is None:
                # No Prescription table
                connection.close()
                return jsonify([])
                
            # Get all prescriptions for this patient with doctor name
            cursor.execute("""
                SELECT p.*, d.Name as DoctorName, d.Specialization 
                FROM Prescription p
                LEFT JOIN Doctor d ON p.Doctor_ID = d.Doctor_ID
                WHERE p.Patient_ID = %s
                ORDER BY p.Prescription_Date DESC
            """, [id])
            prescriptions = cursor.fetchall()
            
            # Convert date objects to strings
            for prescription in prescriptions:
                if 'Prescription_Date' in prescription and prescription['Prescription_Date']:
                    if hasattr(prescription['Prescription_Date'], 'isoformat'):
                        prescription['Prescription_Date'] = prescription['Prescription_Date'].isoformat()
        
        # Close connection
        connection.close()
        
        # Return the prescription data
        return jsonify(prescriptions)
        
    except Exception as e:
        print(f"Error fetching patient prescriptions: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return empty array on error
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)