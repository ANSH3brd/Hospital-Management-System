from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
import traceback
import pymysql
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from models.db import get_db_connection

doctor_bp = Blueprint('doctor', __name__)

# Doctor login required decorator
def doctor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('is_doctor'):
            flash('Please login as a doctor to access this page', 'danger')
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/doctors')
@doctor_login_required
def get_doctors():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
            
        cur = conn.cursor()
        cur.execute("SELECT * FROM Doctor")
        doctors = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('doctors_list.html', doctors=doctors)
    except Exception as e:
        error_msg = f"Error fetching doctors: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('index'))

@doctor_bp.route('/add', methods=['GET', 'POST'])
@doctor_login_required
def add_doctor():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            specialization = request.form['specialization']
            contact = request.form['contact']
            email = request.form['email']
            address = request.form['address']
            
            # Connect to database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('doctor.dashboard'))
                
            cur = conn.cursor()
            
            # Insert doctor data
            cur.execute("""
                INSERT INTO Doctor (Name, Specialization, Contact_Number, Email, Address)
                VALUES (%s, %s, %s, %s, %s)
            """, [name, specialization, contact, email, address])
            
            # Get the last inserted doctor ID
            doctor_id = cur.lastrowid
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash(f'Doctor added successfully with ID: {doctor_id}', 'success')
            # Redirect to dashboard instead of trying to show all doctors
            return redirect(url_for('doctor.dashboard'))
            
        except Exception as e:
            error_msg = f"Error adding doctor: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return redirect(url_for('doctor.dashboard'))
    
    # GET request - render the add doctor form
    return render_template('doctor_add.html')

# Show doctor details
@doctor_bp.route('/<int:id>')
@doctor_login_required
def get_doctor(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get doctor
    result = cur.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [id])
    
    if result > 0:
        doctor = cur.fetchone()
        cur.close()
        return render_template('doctors/detail.html', doctor=doctor)
    else:
        cur.close()
        flash('Doctor not found', 'danger')
        return redirect(url_for('doctors.get_doctors'))

# Show edit doctor form
@doctor_bp.route('/edit/<int:id>', methods=['GET'])
@doctor_login_required
def edit_doctor_form(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get doctor
    result = cur.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [id])
    
    if result > 0:
        doctor = cur.fetchone()
        cur.close()
        return render_template('doctors/edit.html', doctor=doctor)
    else:
        cur.close()
        flash('Doctor not found', 'danger')
        return redirect(url_for('doctors.get_doctors'))

# Update doctor
@doctor_bp.route('/edit/<int:id>', methods=['POST'])
@doctor_login_required
def update_doctor(id):
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
            specialization = request.form['specialization']
            qualifications = request.form['qualifications']
            role = request.form.get('role', 'Doctor')
            shift_timing = request.form.get('shift_timing', 'Day Shift')
            
            # Get experience from form
            try:
                experience = int(request.form.get('experience', '0'))
            except ValueError:
                experience = 0
                
            # Default values for required fields - keep existing values
            availability_status = 'Available'  # This should ideally be fetched from the existing record
            department_id = 0  # This should ideally be fetched from the existing record
            
            # Get new fields
            charges = request.form.get('charges', '500')
            # Only update passcode if provided
            passcode_update = ''
            passcode_param = []
            
            if 'pass_code' in request.form and request.form['pass_code'].strip():
                passcode_update = 'Passcode = %s,'
                passcode_param = [request.form['pass_code']]

            # Create cursor
            import pymysql
            mysql = get_db()
            
            if mysql is None:
                # Direct connection if get_db fails
                try:
                    connection = pymysql.connect(
                        host='localhost',
                        user='root',
                        password='iAf_49512',
                        database='hospital_db',
                        cursorclass=pymysql.cursors.DictCursor
                    )
                    
                    with connection.cursor() as cursor:
                        # Create base query
                        query = """
                            UPDATE Doctor SET
                            Name = %s,
                            Gender = %s,
                            Date_of_Birth = %s,
                            Age = %s,
                            Contact_Number = %s,
                            Address = %s,
                            Email = %s,
                            Specialization = %s,
                            Qualifications = %s,
                            Experience = %s,
                            Role = %s,
                            Shift_Timing = %s,
                            Charges = %s
                            """
                            
                        # Add passcode update if provided
                        if passcode_update:
                            query = query.replace('Charges = %s', 'Charges = %s,\n                            ' + passcode_update.strip(','))
                            
                        # Add WHERE clause
                        query += "\nWHERE Doctor_ID = %s"
                        
                        # Create params list
                        params = [name, gender, dob, age, contact_number, address, email, specialization, 
                                 qualifications, experience, role, shift_timing, charges]
                                
                        # Add passcode param if provided
                        if passcode_param:
                            params.extend(passcode_param)
                            
                        # Add ID param
                        params.append(id)
                        
                        # Execute query
                        cursor.execute(query, tuple(params))
                        connection.commit()
                        connection.close()
                        
                    flash('Doctor updated successfully', 'success')
                    return redirect(url_for('doctors.get_doctor', id=id))
                except Exception as e:
                    flash(f'Error updating doctor: {str(e)}', 'danger')
                    return redirect(url_for('doctors.edit_doctor_form', id=id))
            
            # Execute query using Flask-MySQLdb
            try:
                cur = mysql.connection.cursor()
                
                # Create base query
                query = """
                    UPDATE Doctor SET
                    Name = %s,
                    Gender = %s,
                    Date_of_Birth = %s,
                    Age = %s,
                    Contact_Number = %s,
                    Address = %s,
                    Email = %s,
                    Specialization = %s,
                    Qualifications = %s,
                    Experience = %s,
                    Role = %s,
                    Shift_Timing = %s,
                    Charges = %s
                    """
                    
                # Add passcode update if provided
                if passcode_update:
                    query = query.replace('Charges = %s', 'Charges = %s,\n                    ' + passcode_update.strip(','))
                    
                # Add WHERE clause
                query += "\nWHERE Doctor_ID = %s"
                
                # Create params list
                params = [name, gender, dob, age, contact_number, address, email, specialization, 
                         qualifications, experience, role, shift_timing, charges]
                        
                # Add passcode param if provided
                if passcode_param:
                    params.extend(passcode_param)
                    
                # Add ID param
                params.append(id)
                
                # Execute query
                cur.execute(query, tuple(params))

                # Commit to DB
                mysql.connection.commit()

                # Close connection
                cur.close()

                flash('Doctor updated successfully', 'success')
                return redirect(url_for('doctors.get_doctor', id=id))
            except Exception as e:
                flash(f'Error updating doctor: {str(e)}', 'danger')
                return redirect(url_for('doctors.edit_doctor_form', id=id))
                
        except Exception as e:
            import traceback
            print("Exception in update_doctor:", str(e))
            print(traceback.format_exc())
            flash(f'Error updating doctor: {str(e)}', 'danger')
            return redirect(url_for('doctors.edit_doctor_form', id=id))

# Delete doctor
@doctor_bp.route('/delete/<int:id>', methods=['POST'])
@doctor_login_required
def delete_doctor(id):
    # Create cursor
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # First, back up the doctor data to Updated_Doctor table
    try:
        # Get the doctor data
        cur.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [id])
        doctor = cur.fetchone()
        
        # Insert into updated_doctor table
        cur.execute("""
            INSERT INTO Updated_Doctor
            (Doctor_ID, Name, Gender, Date_of_Birth, Age, Contact_Number, Address, 
            Email, Specialization, Qualifications, Experience, Availability_Status, Department_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doctor['Doctor_ID'], 
                doctor['Name'], 
                doctor['Gender'], 
                doctor['Date_of_Birth'], 
                doctor['Age'], 
                doctor['Contact_Number'], 
                doctor['Address'], 
                doctor['Email'], 
                doctor['Specialization'], 
                doctor['Qualifications'], 
                0,  # Experience (not in the original table)
                'Unavailable',  # Availability_Status (not in the original table)
                0  # Department_ID (not in the original table)
            ))
        
        # Delete the doctor
        cur.execute("DELETE FROM Doctor WHERE Doctor_ID = %s", [id])
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Doctor deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        flash(f'Error deleting doctor: {str(e)}', 'danger')
    
    return redirect(url_for('doctors.get_doctors'))

@doctor_bp.route('/dashboard')
@doctor_login_required
def dashboard():
    try:
        # Get doctor info
        doctor_id = session.get('doctor_id')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
            
        cur = conn.cursor()
        
        # Get doctor information
        cur.execute("SELECT * FROM Doctor WHERE Doctor_ID = %s", [doctor_id])
        doctor = cur.fetchone()
        
        # Get appointments for this doctor
        cur.execute("""
            SELECT a.*, p.Name as PatientName 
            FROM Appointments a
            LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
            WHERE a.Doctor_ID = %s
            ORDER BY a.Appointment_Date DESC
        """, [doctor_id])
        appointments = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('doctor_dashboard.html', doctor=doctor, appointments=appointments)
    except Exception as e:
        error_msg = f"Error loading dashboard: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('index')) 