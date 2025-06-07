from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from models.db import get_db
import pymysql
import traceback

appointment_bp = Blueprint('appointments', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Get all appointments
@appointment_bp.route('/')
@login_required
def get_appointments():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Join with Patient and Doctor to get names
    cur.execute("""
        SELECT a.*, p.Name as PatientName, d.Name as DoctorName 
        FROM Appointment a
        LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
        LEFT JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
        ORDER BY a.Appointment_Date DESC, a.Appointment_Time DESC
    """)
    
    appointments = cur.fetchall()
    cur.close()
    return render_template('appointments/index.html', appointments=appointments)

# Show add appointment form
@appointment_bp.route('/add', methods=['GET'])
@login_required
def add_appointment_form():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get all patients for dropdown
    cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
    patients = cur.fetchall()
    
    # Get all doctors for dropdown
    cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
    doctors = cur.fetchall()
    
    cur.close()
    
    return render_template('appointments/add.html', patients=patients, doctors=doctors)

# Add appointment
@appointment_bp.route('/add', methods=['POST'])
@login_required
def add_appointment():
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        status = request.form['status']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time, Status) 
                VALUES (%s, %s, %s, %s, %s)
                """, (patient_id, doctor_id, appointment_date, appointment_time, status))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Appointment added successfully', 'success')
            return redirect(url_for('appointments.get_appointments'))
        except Exception as e:
            flash(f'Error adding appointment: {str(e)}', 'danger')
            return redirect(url_for('appointments.add_appointment_form'))

# Show appointment details
@appointment_bp.route('/<int:id>')
@login_required
def get_appointment(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get appointment with patient and doctor names
    result = cur.execute("""
        SELECT a.*, p.Name as PatientName, d.Name as DoctorName 
        FROM Appointment a
        LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
        LEFT JOIN Doctor d ON a.Doctor_ID = d.Doctor_ID
        WHERE a.Appointment_ID = %s
    """, [id])
    
    if result > 0:
        appointment = cur.fetchone()
        cur.close()
        return render_template('appointments/detail.html', appointment=appointment)
    else:
        cur.close()
        flash('Appointment not found', 'danger')
        return redirect(url_for('appointments.get_appointments'))

# Show edit appointment form
@appointment_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_appointment_form(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get appointment
    result = cur.execute("SELECT * FROM Appointment WHERE Appointment_ID = %s", [id])
    
    if result > 0:
        appointment = cur.fetchone()
        
        # Get all patients for dropdown
        cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
        patients = cur.fetchall()
        
        # Get all doctors for dropdown
        cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
        doctors = cur.fetchall()
        
        cur.close()
        
        return render_template('appointments/edit.html', appointment=appointment, patients=patients, doctors=doctors)
    else:
        cur.close()
        flash('Appointment not found', 'danger')
        return redirect(url_for('appointments.get_appointments'))

# Update appointment
@appointment_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_appointment(id):
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        status = request.form['status']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                UPDATE Appointment SET 
                Patient_ID = %s, 
                Doctor_ID = %s, 
                Appointment_Date = %s, 
                Appointment_Time = %s, 
                Status = %s
                WHERE Appointment_ID = %s
                """, (patient_id, doctor_id, appointment_date, appointment_time, status, id))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Appointment updated successfully', 'success')
            return redirect(url_for('appointments.get_appointment', id=id))
        except Exception as e:
            flash(f'Error updating appointment: {str(e)}', 'danger')
            return redirect(url_for('appointments.edit_appointment_form', id=id))

# Update appointment status (for doctors to mark as Completed or Cancelled)
@appointment_bp.route('/update-status/<int:id>/<string:status>')
@login_required
def update_appointment_status(id, status):
    # Validate status
    if status not in ['Scheduled', 'Completed', 'Cancelled']:
        flash('Invalid status value', 'danger')
        return redirect(url_for('doctor_dashboard'))
    
    try:
        # Get database connection
        mysql = get_db()
        if mysql is None or not hasattr(mysql, 'connection'):
            # Direct approach with pymysql if mysql connection fails
            print("Using direct pymysql connection for updating appointment status")
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='iAf_49512',
                database='hospital_db',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with connection.cursor() as cursor:
                # Update appointment status
                cursor.execute("""
                    UPDATE Appointment 
                    SET Status = %s 
                    WHERE Appointment_ID = %s
                """, (status, id))
                
                connection.commit()
            
            connection.close()
        else:
            # Use Flask-MySQL connection
            cur = mysql.connection.cursor()
            
            # Update appointment status
            cur.execute("""
                UPDATE Appointment 
                SET Status = %s 
                WHERE Appointment_ID = %s
            """, (status, id))
            
            mysql.connection.commit()
            cur.close()
        
        flash(f'Appointment status updated to {status}', 'success')
    except Exception as e:
        print(f"Error updating appointment status: {str(e)}")
        print(traceback.format_exc())
        flash(f'Error updating appointment status: {str(e)}', 'danger')
    
    # Redirect back to doctor dashboard
    return redirect(url_for('doctor_dashboard'))

# Delete appointment
@appointment_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    # Create cursor
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    try:
        # Delete the appointment
        cur.execute("DELETE FROM Appointment WHERE Appointment_ID = %s", [id])
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Appointment deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        flash(f'Error deleting appointment: {str(e)}', 'danger')
    
    return redirect(url_for('appointments.get_appointments')) 