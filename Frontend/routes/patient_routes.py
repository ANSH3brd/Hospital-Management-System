from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from models.db import get_db

patient_bp = Blueprint('patients', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Handle database connection errors
def get_db_connection():
    mysql = get_db()
    try:
        return mysql.connection
    except Exception as e:
        flash(f'Database connection error: {str(e)}', 'danger')
        return None

# Get all patients
@patient_bp.route('/')
@login_required
def get_patients():
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))
        
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Patient")
        patients = cur.fetchall()
        return render_template('patients/index.html', patients=patients)
    except Exception as e:
        flash(f'Error retrieving patients: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        cur.close()

# Show add patient form
@patient_bp.route('/add', methods=['GET'])
@login_required
def add_patient_form():
    return render_template('patients/add.html')

# Add patient
@patient_bp.route('/add', methods=['POST'])
@login_required
def add_patient():
    if request.method == 'POST':
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
        medical_history = request.form['medical_history']
        insurance_details = request.form['insurance_details']
        
        # Get database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('patients.add_patient_form'))
            
        # Create cursor
        cur = conn.cursor()
        
        # Execute query
        try:
            cur.execute("""
                INSERT INTO Patient (Name, Gender, Date_of_Birth, Age, Contact_Number, Address, 
                Email, Blood_Group, Medical_History, Insurance_Details) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, gender, dob, age, contact_number, address, email, blood_group, medical_history, insurance_details))
            
            # Commit to DB
            conn.commit()
            
            flash('Patient added successfully', 'success')
            return redirect(url_for('patients.get_patients'))
        except Exception as e:
            conn.rollback()
            flash(f'Error adding patient: {str(e)}', 'danger')
            return redirect(url_for('patients.add_patient_form'))
        finally:
            # Close connection
            cur.close()

# Show patient details
@patient_bp.route('/<int:id>')
@login_required
def get_patient(id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('patients.get_patients'))
        
    cur = conn.cursor()
    
    try:
        # Get patient
        result = cur.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [id])
        
        if result > 0:
            patient = cur.fetchone()
            return render_template('patients/detail.html', patient=patient)
        else:
            flash('Patient not found', 'danger')
            return redirect(url_for('patients.get_patients'))
    except Exception as e:
        flash(f'Error retrieving patient details: {str(e)}', 'danger')
        return redirect(url_for('patients.get_patients'))
    finally:
        cur.close()

# Show edit patient form
@patient_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_patient_form(id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('patients.get_patients'))
        
    cur = conn.cursor()
    
    try:
        # Get patient
        result = cur.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [id])
        
        if result > 0:
            patient = cur.fetchone()
            return render_template('patients/edit.html', patient=patient)
        else:
            flash('Patient not found', 'danger')
            return redirect(url_for('patients.get_patients'))
    except Exception as e:
        flash(f'Error retrieving patient for editing: {str(e)}', 'danger')
        return redirect(url_for('patients.get_patients'))
    finally:
        cur.close()

# Update patient
@patient_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_patient(id):
    if request.method == 'POST':
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
        medical_history = request.form['medical_history']
        insurance_details = request.form['insurance_details']
        
        # Get database connection
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('patients.edit_patient_form', id=id))
            
        # Create cursor
        cur = conn.cursor()
        
        # Execute query
        try:
            cur.execute("""
                UPDATE Patient SET 
                Name = %s, 
                Gender = %s, 
                Date_of_Birth = %s, 
                Age = %s, 
                Contact_Number = %s, 
                Address = %s, 
                Email = %s, 
                Blood_Group = %s, 
                Medical_History = %s, 
                Insurance_Details = %s 
                WHERE Patient_ID = %s
                """, (name, gender, dob, age, contact_number, address, email, blood_group, medical_history, insurance_details, id))
            
            # Commit to DB
            conn.commit()
            
            flash('Patient updated successfully', 'success')
            return redirect(url_for('patients.get_patient', id=id))
        except Exception as e:
            conn.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
            return redirect(url_for('patients.edit_patient_form', id=id))
        finally:
            # Close connection
            cur.close()

# Delete patient
@patient_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_patient(id):
    # Get database connection
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('patients.get_patients'))
        
    # Create cursor
    cur = conn.cursor()
    
    # First, back up the patient data to Updated_Patient table
    try:
        # Check if Updated_Patient table exists
        cur.execute("SHOW TABLES LIKE 'Updated_Patient'")
        if cur.fetchone() is None:
            # Create Updated_Patient table
            cur.execute("""
                CREATE TABLE Updated_Patient (
                    Patient_ID VARCHAR(10) PRIMARY KEY,
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
            conn.commit()
            
        # Get the patient data
        cur.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [id])
        patient = cur.fetchone()
        
        if not patient:
            flash('Patient not found', 'danger')
            cur.close()
            return redirect(url_for('patients.get_patients'))
            
        # Insert into updated_patient table
        cur.execute("""
            INSERT INTO Updated_Patient
            (Patient_ID, Name, Gender, Date_of_Birth, Age, Contact_Number, Address, 
            Email, Blood_Group, Medical_History, Insurance_Details)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                patient['Patient_ID'], 
                patient['Name'], 
                patient['Gender'], 
                patient['Date_of_Birth'], 
                patient['Age'], 
                patient['Contact_Number'], 
                patient['Address'], 
                patient['Email'], 
                patient['Blood_Group'], 
                patient['Medical_History'], 
                patient['Insurance_Details']
            ))
        
        # Delete the patient
        cur.execute("DELETE FROM Patient WHERE Patient_ID = %s", [id])
        
        # Commit to DB
        conn.commit()
        
        flash('Patient deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        flash(f'Error deleting patient: {str(e)}', 'danger')
    finally:
        # Close connection
        cur.close()
    
    return redirect(url_for('patients.get_patients'))

# Get patient data as JSON (API endpoint for AJAX)
@patient_bp.route('/api/<int:id>')
@login_required
def get_patient_api(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Patient WHERE Patient_ID = %s", [id])
        patient = cur.fetchone()
        
        if patient:
            return jsonify(patient)
        else:
            return jsonify({'error': 'Patient not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close() 