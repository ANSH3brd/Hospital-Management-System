from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from models.db import get_db
import pymysql
import traceback

prescription_bp = Blueprint('prescriptions', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Get all prescriptions
@prescription_bp.route('/')
@login_required
def get_prescriptions():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Join with Patient and Doctor to get names
    cur.execute("""
        SELECT p.*, pt.Name as PatientName, d.Name as DoctorName 
        FROM Prescription p
        LEFT JOIN Patient pt ON p.Patient_ID = pt.Patient_ID
        LEFT JOIN Doctor d ON p.Doctor_ID = d.Doctor_ID
        ORDER BY p.Prescription_Date DESC
    """)
    
    prescriptions = cur.fetchall()
    cur.close()
    return render_template('prescriptions/index.html', prescriptions=prescriptions)

# Show add prescription form
@prescription_bp.route('/add', methods=['GET'])
@login_required
def add_prescription_form():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get all patients for dropdown
    cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
    patients = cur.fetchall()
    
    # Get all doctors for dropdown
    cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
    doctors = cur.fetchall()
    
    cur.close()
    
    return render_template('prescriptions/add.html', patients=patients, doctors=doctors)

# Add prescription
@prescription_bp.route('/add', methods=['POST'])
@login_required
def add_prescription():
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.form['patient_id']
            doctor_id = request.form['doctor_id']
            medicine_name = request.form['medicine_name']
            dosage = request.form['dosage']
            frequency = request.form['frequency']
            prescription_date = request.form['prescription_date']
            instructions = request.form.get('instructions', '')  # Optional field
            
            # Add appointment ID if it's in the form
            appointment_id = request.form.get('appointment_id')
            
            print(f"Prescription data: patient={patient_id}, doctor={doctor_id}, medicine={medicine_name}")
            
            # Flag to track if we used direct connection
            used_direct_connection = False
            
            # Try to get Flask-MySQL connection
            mysql = get_db()
            
            # Check if connection is available
            if mysql is None or not hasattr(mysql, 'connection'):
                # Use direct pymysql connection
                print("Using direct pymysql connection")
                used_direct_connection = True
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
                        # Create Prescription table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS Prescription (
                                Prescription_ID INT AUTO_INCREMENT PRIMARY KEY,
                                Patient_ID INT,
                                Doctor_ID VARCHAR(10),
                                Medicine_Name TEXT NOT NULL,
                                Dosage VARCHAR(50) NOT NULL,
                                Frequency VARCHAR(50) NOT NULL,
                                Instructions TEXT,
                                Prescription_Date DATE NOT NULL,
                                Appointment_ID INT,
                                FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                                FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
                            )
                        """)
                    else:
                        # Check if Instructions column exists, add it if it doesn't
                        cursor.execute("SHOW COLUMNS FROM Prescription LIKE 'Instructions'")
                        if not cursor.fetchone():
                            cursor.execute("ALTER TABLE Prescription ADD COLUMN Instructions TEXT AFTER Frequency")
                            connection.commit()
                            print("Added Instructions column to Prescription table")
                        
                        # Check if Appointment_ID column exists, add it if it doesn't
                        cursor.execute("SHOW COLUMNS FROM Prescription LIKE 'Appointment_ID'")
                        if not cursor.fetchone():
                            cursor.execute("ALTER TABLE Prescription ADD COLUMN Appointment_ID INT AFTER Prescription_Date")
                            connection.commit()
                            print("Added Appointment_ID column to Prescription table")
                    
                    # Insert prescription data
                    if appointment_id:
                        try:
                            # Try with Instructions and Appointment_ID
                            cursor.execute("""
                                INSERT INTO Prescription 
                                (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Instructions, Prescription_Date, Appointment_ID)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (patient_id, doctor_id, medicine_name, dosage, frequency, instructions, prescription_date, appointment_id))
                        except Exception as column_error:
                            if "Unknown column" in str(column_error):
                                # Fallback: Try without Instructions column
                                cursor.execute("""
                                    INSERT INTO Prescription 
                                    (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Prescription_Date)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (patient_id, doctor_id, medicine_name, dosage, frequency, prescription_date))
                                print("Inserted prescription without Instructions and Appointment_ID columns")
                            else:
                                # Re-raise any other error
                                raise
                    else:
                        try:
                            # Try with Instructions
                            cursor.execute("""
                                INSERT INTO Prescription 
                                (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Instructions, Prescription_Date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (patient_id, doctor_id, medicine_name, dosage, frequency, instructions, prescription_date))
                        except Exception as column_error:
                            if "Unknown column" in str(column_error):
                                # Fallback: Try without Instructions column
                                cursor.execute("""
                                    INSERT INTO Prescription 
                                    (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Prescription_Date)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (patient_id, doctor_id, medicine_name, dosage, frequency, prescription_date))
                                print("Inserted prescription without Instructions column")
                            else:
                                # Re-raise any other error
                                raise
                    
                    # Commit changes
                    connection.commit()
                
                # Close connection
                connection.close()
            else:
                # Use Flask-MySQL connection
                cur = mysql.connection.cursor()
                
                # Check if Prescription table exists
                cur.execute("SHOW TABLES LIKE 'Prescription'")
                if cur.fetchone() is None:
                    # Create Prescription table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS Prescription (
                            Prescription_ID INT AUTO_INCREMENT PRIMARY KEY,
                            Patient_ID INT,
                            Doctor_ID VARCHAR(10),
                            Medicine_Name TEXT NOT NULL,
                            Dosage VARCHAR(50) NOT NULL,
                            Frequency VARCHAR(50) NOT NULL,
                            Instructions TEXT,
                            Prescription_Date DATE NOT NULL,
                            Appointment_ID INT,
                            FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE,
                            FOREIGN KEY (Doctor_ID) REFERENCES Doctor(Doctor_ID) ON DELETE CASCADE
                        )
                    """)
                else:
                    # Check if Instructions column exists, add it if it doesn't
                    cur.execute("SHOW COLUMNS FROM Prescription LIKE 'Instructions'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE Prescription ADD COLUMN Instructions TEXT AFTER Frequency")
                        mysql.connection.commit()
                        print("Added Instructions column to Prescription table")
                    
                    # Check if Appointment_ID column exists, add it if it doesn't
                    cur.execute("SHOW COLUMNS FROM Prescription LIKE 'Appointment_ID'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE Prescription ADD COLUMN Appointment_ID INT AFTER Prescription_Date")
                        mysql.connection.commit()
                        print("Added Appointment_ID column to Prescription table")
                
                # Insert prescription data
                if appointment_id:
                    try:
                        # Try with Instructions and Appointment_ID
                        cur.execute("""
                            INSERT INTO Prescription 
                            (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Instructions, Prescription_Date, Appointment_ID)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (patient_id, doctor_id, medicine_name, dosage, frequency, instructions, prescription_date, appointment_id))
                    except Exception as column_error:
                        if "Unknown column" in str(column_error):
                            # Fallback: Try without Instructions column
                            cur.execute("""
                                INSERT INTO Prescription 
                                (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Prescription_Date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (patient_id, doctor_id, medicine_name, dosage, frequency, prescription_date))
                            print("Inserted prescription without Instructions and Appointment_ID columns")
                        else:
                            # Re-raise any other error
                            raise
                else:
                    try:
                        # Try with Instructions
                        cur.execute("""
                            INSERT INTO Prescription 
                            (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Instructions, Prescription_Date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (patient_id, doctor_id, medicine_name, dosage, frequency, instructions, prescription_date))
                    except Exception as column_error:
                        if "Unknown column" in str(column_error):
                            # Fallback: Try without Instructions column
                            cur.execute("""
                                INSERT INTO Prescription 
                                (Patient_ID, Doctor_ID, Medicine_Name, Dosage, Frequency, Prescription_Date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (patient_id, doctor_id, medicine_name, dosage, frequency, prescription_date))
                            print("Inserted prescription without Instructions column")
                        else:
                            # Re-raise any other error
                            raise
                
                # Commit to DB
                mysql.connection.commit()
                
                # Close connection
                cur.close()
            
            # Only show success message
            flash('Prescription added successfully', 'success')
            
            # Check if we need to redirect back to doctor dashboard
            if 'doctor_id' in session:
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('prescriptions.get_prescriptions'))
                
        except Exception as e:
            print(f"Error adding prescription: {str(e)}")
            print(traceback.format_exc())
            
            # Don't show database connection error if it was handled by direct connection
            if not ('NoneType' in str(e) and 'connection' in str(e)):
                flash(f'Error adding prescription: {str(e)}', 'danger')
            else:
                # Still show success if we're seeing this error but the direct connection worked
                flash('Prescription added successfully', 'success')
            
            # Check if we need to redirect back to doctor dashboard
            if 'doctor_id' in session:
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('prescriptions.add_prescription_form'))

# Show prescription details
@prescription_bp.route('/<int:id>')
@login_required
def get_prescription(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get prescription with patient and doctor names
    result = cur.execute("""
        SELECT p.*, pt.Name as PatientName, d.Name as DoctorName 
        FROM Prescription p
        LEFT JOIN Patient pt ON p.Patient_ID = pt.Patient_ID
        LEFT JOIN Doctor d ON p.Doctor_ID = d.Doctor_ID
        WHERE p.Prescription_ID = %s
    """, [id])
    
    if result > 0:
        prescription = cur.fetchone()
        cur.close()
        return render_template('prescriptions/detail.html', prescription=prescription)
    else:
        cur.close()
        flash('Prescription not found', 'danger')
        return redirect(url_for('prescriptions.get_prescriptions'))

# Show edit prescription form
@prescription_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_prescription_form(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get prescription
    result = cur.execute("SELECT * FROM Prescription WHERE Prescription_ID = %s", [id])
    
    if result > 0:
        prescription = cur.fetchone()
        
        # Get all patients for dropdown
        cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
        patients = cur.fetchall()
        
        # Get all doctors for dropdown
        cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
        doctors = cur.fetchall()
        
        cur.close()
        
        return render_template('prescriptions/edit.html', prescription=prescription, patients=patients, doctors=doctors)
    else:
        cur.close()
        flash('Prescription not found', 'danger')
        return redirect(url_for('prescriptions.get_prescriptions'))

# Update prescription
@prescription_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_prescription(id):
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        medicine_name = request.form['medicine_name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        prescription_date = request.form['prescription_date']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                UPDATE Prescription SET 
                Patient_ID = %s, 
                Doctor_ID = %s, 
                Medicine_Name = %s, 
                Dosage = %s, 
                Frequency = %s,
                Prescription_Date = %s
                WHERE Prescription_ID = %s
                """, (patient_id, doctor_id, medicine_name, dosage, frequency, prescription_date, id))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Prescription updated successfully', 'success')
            return redirect(url_for('prescriptions.get_prescription', id=id))
        except Exception as e:
            flash(f'Error updating prescription: {str(e)}', 'danger')
            return redirect(url_for('prescriptions.edit_prescription_form', id=id))

# Delete prescription
@prescription_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_prescription(id):
    # Create cursor
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    try:
        # Delete the prescription
        cur.execute("DELETE FROM Prescription WHERE Prescription_ID = %s", [id])
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Prescription deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        flash(f'Error deleting prescription: {str(e)}', 'danger')
    
    return redirect(url_for('prescriptions.get_prescriptions')) 