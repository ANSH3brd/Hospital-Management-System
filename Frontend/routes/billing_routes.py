from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from models.db import get_db

billing_bp = Blueprint('billing', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Get all bills
@billing_bp.route('/')
@login_required
def get_bills():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Join with Patient and Appointment
    cur.execute("""
        SELECT b.*, p.Name as PatientName, 
        CONCAT(a.Appointment_Date, ' ', a.Appointment_Time) as AppointmentDateTime
        FROM Billing b
        LEFT JOIN Patient p ON b.Patient_ID = p.Patient_ID
        LEFT JOIN Appointment a ON b.Appointment_ID = a.Appointment_ID
        ORDER BY b.Bill_Date DESC
    """)
    
    bills = cur.fetchall()
    cur.close()
    return render_template('billing/index.html', bills=bills)

# Show add bill form
@billing_bp.route('/add', methods=['GET'])
@login_required
def add_bill_form():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get all patients for dropdown
    cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
    patients = cur.fetchall()
    
    # Get all appointments for dropdown
    cur.execute("""
        SELECT a.Appointment_ID, p.Name as PatientName, 
        CONCAT(a.Appointment_Date, ' ', a.Appointment_Time) as AppointmentDateTime 
        FROM Appointment a
        LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
        ORDER BY a.Appointment_Date DESC, a.Appointment_Time DESC
    """)
    appointments = cur.fetchall()
    
    cur.close()
    
    return render_template('billing/add.html', patients=patients, appointments=appointments)

# Add bill
@billing_bp.route('/add', methods=['POST'])
@login_required
def add_bill():
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        appointment_id = request.form['appointment_id']
        total_amount = request.form['total_amount']
        payment_status = request.form['payment_status']
        bill_date = request.form['bill_date']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                INSERT INTO Billing (Patient_ID, Appointment_ID, Total_Amount, Payment_Status, Bill_Date) 
                VALUES (%s, %s, %s, %s, %s)
                """, (patient_id, appointment_id, total_amount, payment_status, bill_date))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Bill added successfully', 'success')
            return redirect(url_for('billing.get_bills'))
        except Exception as e:
            flash(f'Error adding bill: {str(e)}', 'danger')
            return redirect(url_for('billing.add_bill_form'))

# Show bill details
@billing_bp.route('/<int:id>')
@login_required
def get_bill(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get bill with patient and appointment details
    result = cur.execute("""
        SELECT b.*, p.Name as PatientName, 
        CONCAT(a.Appointment_Date, ' ', a.Appointment_Time) as AppointmentDateTime
        FROM Billing b
        LEFT JOIN Patient p ON b.Patient_ID = p.Patient_ID
        LEFT JOIN Appointment a ON b.Appointment_ID = a.Appointment_ID
        WHERE b.Bill_ID = %s
    """, [id])
    
    if result > 0:
        bill = cur.fetchone()
        cur.close()
        return render_template('billing/detail.html', bill=bill)
    else:
        cur.close()
        flash('Bill not found', 'danger')
        return redirect(url_for('billing.get_bills'))

# Show edit bill form
@billing_bp.route('/edit/<int:id>', methods=['GET'])
@login_required
def edit_bill_form(id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get bill
    result = cur.execute("SELECT * FROM Billing WHERE Bill_ID = %s", [id])
    
    if result > 0:
        bill = cur.fetchone()
        
        # Get all patients for dropdown
        cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
        patients = cur.fetchall()
        
        # Get all appointments for dropdown
        cur.execute("""
            SELECT a.Appointment_ID, p.Name as PatientName, 
            CONCAT(a.Appointment_Date, ' ', a.Appointment_Time) as AppointmentDateTime 
            FROM Appointment a
            LEFT JOIN Patient p ON a.Patient_ID = p.Patient_ID
            ORDER BY a.Appointment_Date DESC, a.Appointment_Time DESC
        """)
        appointments = cur.fetchall()
        
        cur.close()
        
        return render_template('billing/edit.html', bill=bill, patients=patients, appointments=appointments)
    else:
        cur.close()
        flash('Bill not found', 'danger')
        return redirect(url_for('billing.get_bills'))

# Update bill
@billing_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def update_bill(id):
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        appointment_id = request.form['appointment_id']
        total_amount = request.form['total_amount']
        payment_status = request.form['payment_status']
        bill_date = request.form['bill_date']
        
        # Create cursor
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Execute query
        try:
            cur.execute("""
                UPDATE Billing SET 
                Patient_ID = %s, 
                Appointment_ID = %s, 
                Total_Amount = %s, 
                Payment_Status = %s, 
                Bill_Date = %s
                WHERE Bill_ID = %s
                """, (patient_id, appointment_id, total_amount, payment_status, bill_date, id))
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close connection
            cur.close()
            
            flash('Bill updated successfully', 'success')
            return redirect(url_for('billing.get_bill', id=id))
        except Exception as e:
            flash(f'Error updating bill: {str(e)}', 'danger')
            return redirect(url_for('billing.edit_bill_form', id=id))

# Delete bill
@billing_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_bill(id):
    # Create cursor
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    try:
        # Delete the bill
        cur.execute("DELETE FROM Billing WHERE Bill_ID = %s", [id])
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Bill deleted successfully', 'success')
    except Exception as e:
        # Rollback in case of error
        mysql.connection.rollback()
        flash(f'Error deleting bill: {str(e)}', 'danger')
    
    return redirect(url_for('billing.get_bills')) 