from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from models.db import get_db

medical_record_bp = Blueprint('medical_records', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Get all medical records
@medical_record_bp.route('/')
@login_required
def get_medical_records():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Join with Patient and Doctor to get names
    cur.execute("""
        SELECT mr.*, p.Name as PatientName, d.Name as DoctorName 
        FROM Medical_Record mr
        LEFT JOIN Patient p ON mr.Patient_ID = p.Patient_ID
        LEFT JOIN Doctor d ON mr.Doctor_ID = d.Doctor_ID
        ORDER BY mr.Visit_Date DESC
    """)
    
    medical_records = cur.fetchall()
    cur.close()
    return render_template('medical_records/index.html', medical_records=medical_records)

# Show add medical record form
@medical_record_bp.route('/add', methods=['GET'])
@login_required
def add_medical_record_form():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get all patients for dropdown
    cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
    patients = cur.fetchall()
    
    # Get all doctors for dropdown
    cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
    doctors = cur.fetchall()
    
    cur.close()
    
    return render_template('medical_records/add.html', patients=patients, doctors=doctors)

# Add medical record
@medical_record_bp.route('/add', methods=['POST'])
@login_required
def add_medical_record():
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        diagnosis = request.form['diagnosis']
        treatment_details = request.form['treatment_details']
        visit_date = request.form['visit_date']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                INSERT INTO Medical_Record (Patient_ID, Doctor_ID, Diagnosis, Treatment_Details, Visit_Date) 
                VALUES (%s, %s, %s, %s, %s)
                """, (patient_id, doctor_id, diagnosis, treatment_details, visit_date))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Medical record added successfully', 'success')
            return redirect(url_for('medical_records.get_medical_records'))
        except Exception as e:
            flash(f'Error adding medical record: {str(e)}', 'danger')
            return redirect(url_for('medical_records.add_medical_record_form'))

# Show medical record details
@medical_record_bp.route('/<int:id>')
@login_required
def get_medical_record(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get medical record with patient and doctor names
    result = cur.execute("""
        SELECT mr.*, p.Name as PatientName, d.Name as DoctorName 
        FROM Medical_Record mr
        LEFT JOIN Patient p ON mr.Patient_ID = p.Patient_ID
        LEFT JOIN Doctor d ON mr.Doctor_ID = d.Doctor_ID
        WHERE mr.Record_ID = %s
    """, [id])
    
    if result > 0:
        medical_record = cur.fetchone()
        cur.close()
        return render_template('medical_records/detail.html', medical_record=medical_record)
    else:
        cur.close()
        flash('Medical record not found', 'danger')
        return redirect(url_for('medical_records.get_medical_records'))

# Show edit medical record form
@medical_record_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_medical_record_form(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get medical record
    result = cur.execute("SELECT * FROM Medical_Record WHERE Record_ID = %s", [id])
    
    if result > 0:
        medical_record = cur.fetchone()
        
        # Get all patients for dropdown
        cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
        patients = cur.fetchall()
        
        # Get all doctors for dropdown
        cur.execute("SELECT Doctor_ID, Name, Specialization FROM Doctor ORDER BY Name")
        doctors = cur.fetchall()
        
        cur.close()
        
        return render_template('medical_records/edit.html', medical_record=medical_record, patients=patients, doctors=doctors)
    else:
        cur.close()
        flash('Medical record not found', 'danger')
        return redirect(url_for('medical_records.get_medical_records'))

# Update medical record
@medical_record_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_medical_record(id):
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        diagnosis = request.form['diagnosis']
        treatment_details = request.form['treatment_details']
        visit_date = request.form['visit_date']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                UPDATE Medical_Record SET 
                Patient_ID = %s, 
                Doctor_ID = %s, 
                Diagnosis = %s, 
                Treatment_Details = %s, 
                Visit_Date = %s
                WHERE Record_ID = %s
                """, (patient_id, doctor_id, diagnosis, treatment_details, visit_date, id))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Medical record updated successfully', 'success')
            return redirect(url_for('medical_records.get_medical_record', id=id))
        except Exception as e:
            flash(f'Error updating medical record: {str(e)}', 'danger')
            return redirect(url_for('medical_records.edit_medical_record_form', id=id))

# Delete medical record
@medical_record_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_medical_record(id):
    # Create cursor
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    try:
        # Delete the medical record
        cur.execute("DELETE FROM Medical_Record WHERE Record_ID = %s", [id])
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Medical record deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        flash(f'Error deleting medical record: {str(e)}', 'danger')
    
    return redirect(url_for('medical_records.get_medical_records')) 