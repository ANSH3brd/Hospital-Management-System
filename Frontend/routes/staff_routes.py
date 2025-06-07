from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import pymysql
import traceback

# Blueprint definition
staff_bp = Blueprint('staff', __name__)

# Store MySQL connection
mysql = None

# Initialize MySQL
def init_mysql(mysql_connection):
    global mysql
    mysql = mysql_connection

# Staff login required decorator
def staff_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('user_type') != 'staff':
            flash('Please login as staff to access this page', 'danger')
            return redirect(url_for('staff.login'))
        return f(*args, **kwargs)
    return decorated_function

# Get database connection
def get_db_connection():
    try:
        return pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        print(traceback.format_exc())
        return None

# Staff login route
@staff_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Get form data
            staff_id = request.form['staff_id']
            password = request.form['password']
            
            # Validate
            if not staff_id or not password:
                flash('Please enter both Staff ID and Password', 'danger')
                return render_template('staff_login.html')
            
            # Check if the staff exists and password matches
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return render_template('staff_login.html')
                
            cur = conn.cursor()
            cur.execute("""
                SELECT s.*, sl.Passcode 
                FROM Staff s
                JOIN Staff_Login sl ON s.Staff_ID = sl.Staff_ID
                WHERE s.Staff_ID = %s
            """, [staff_id])
            staff = cur.fetchone()
            cur.close()
            conn.close()
            
            if staff and str(staff['Passcode']) == password:
                # Login successful, set session variables
                session['logged_in'] = True
                session['user_id'] = staff['Staff_ID']
                session['user_name'] = staff['Name']
                session['user_type'] = 'staff'
                session['role'] = staff['Staff_Role']
                
                flash(f'Welcome {staff["Name"]}!', 'success')
                return redirect(url_for('staff.dashboard'))
            else:
                flash('Invalid Staff ID or Password', 'danger')
                return render_template('staff_login.html')
                
        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return render_template('staff_login.html')
    
    # GET request - render the login form
    return render_template('staff_login.html')

# Staff dashboard route
@staff_bp.route('/dashboard')
@staff_login_required
def dashboard():
    try:
        # Get all staff members for the manager to view
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('index'))
            
        cur = conn.cursor()
        
        # Get staff list
        cur.execute("""
            SELECT * FROM Staff
            ORDER BY Staff_ID
        """)
        staff_list = cur.fetchall()
        
        # Get doctor count
        doctor_count = 0
        try:
            cur.execute("SELECT COUNT(*) as count FROM Doctor")
            result = cur.fetchone()
            if result:
                doctor_count = result['count']
        except:
            pass
        
        # Get patient count
        patient_count = 0
        try:
            cur.execute("SELECT COUNT(*) as count FROM Patient")
            result = cur.fetchone()
            if result:
                patient_count = result['count']
        except:
            pass
        
        cur.close()
        conn.close()
        
        return render_template('staff_dashboard.html', 
                              staff_list=staff_list,
                              doctor_count=doctor_count,
                              patient_count=patient_count)
        
    except Exception as e:
        error_msg = f"Dashboard error: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('index'))

# Add new staff route
@staff_bp.route('/add', methods=['GET', 'POST'])
@staff_login_required
def add_staff():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form['dob']
            age = request.form['age']
            contact = request.form['contact']
            address = request.form['address']
            email = request.form['email']
            role = request.form['role']
            shift = request.form['shift']
            
            # Insert into database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('staff.add_staff'))
                
            cur = conn.cursor()
            
            # Insert staff data
            cur.execute("""
                INSERT INTO Staff (Name, Gender, Date_of_Birth, Age, Contact_Number, Address, Email, Staff_Role, Shift_Timing)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [name, gender, dob, age, contact, address, email, role, shift])
            
            # Get the last inserted ID
            staff_id = cur.lastrowid
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash(f'Staff member added successfully with ID: {staff_id}', 'success')
            return redirect(url_for('staff.dashboard'))
            
        except Exception as e:
            error_msg = f"Error adding staff: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return redirect(url_for('staff.add_staff'))
    
    # GET request - render add staff form
    return render_template('staff_add.html')

# Update staff route
@staff_bp.route('/edit/<int:staff_id>', methods=['GET', 'POST'])
@staff_login_required
def edit_staff_form(staff_id):
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form['dob']
            age = request.form['age']
            contact = request.form['contact']
            address = request.form['address']
            email = request.form['email']
            role = request.form['role']
            shift = request.form['shift']
            
            # Update database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('staff.dashboard'))
                
            cur = conn.cursor()
            
            # Update staff data
            cur.execute("""
                UPDATE Staff 
                SET Name = %s, Gender = %s, Date_of_Birth = %s, Age = %s, 
                    Contact_Number = %s, Address = %s, Email = %s, 
                    Staff_Role = %s, Shift_Timing = %s
                WHERE Staff_ID = %s
            """, [name, gender, dob, age, contact, address, email, role, shift, staff_id])
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Staff member updated successfully', 'success')
            return redirect(url_for('staff.dashboard'))
            
        except Exception as e:
            error_msg = f"Error updating staff: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return redirect(url_for('staff.edit_staff_form', staff_id=staff_id))
    
    # GET request - fetch staff data and render edit form
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))
            
        cur = conn.cursor()
        cur.execute("SELECT * FROM Staff WHERE Staff_ID = %s", [staff_id])
        staff = cur.fetchone()
        cur.close()
        conn.close()
        
        if not staff:
            flash('Staff member not found', 'danger')
            return redirect(url_for('staff.dashboard'))
            
        return render_template('staff_edit.html', staff=staff)
        
    except Exception as e:
        error_msg = f"Error fetching staff data: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.dashboard'))

# Delete staff route
@staff_bp.route('/delete/<int:staff_id>', methods=['POST'])
@staff_login_required
def delete_staff(staff_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))
            
        cur = conn.cursor()
        
        # Get staff details before deletion for archiving
        cur.execute("SELECT * FROM Staff WHERE Staff_ID = %s", [staff_id])
        staff = cur.fetchone()
        
        if staff:
            # Archive the deleted staff member
            cur.execute("""
                INSERT INTO Deleted_Staff (
                    Staff_ID, Name, Gender, Date_of_Birth, Age, 
                    Contact_Number, Address, Email, Staff_Role, Shift_Timing
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                staff['Staff_ID'], staff['Name'], staff['Gender'], 
                staff['Date_of_Birth'], staff['Age'], staff['Contact_Number'],
                staff['Address'], staff['Email'], staff['Staff_Role'], 
                staff['Shift_Timing']
            ])
            
            # Delete from Staff_Login first (due to foreign key constraint)
            cur.execute("DELETE FROM Staff_Login WHERE Staff_ID = %s", [staff_id])
            
            # Then delete from Staff
            cur.execute("DELETE FROM Staff WHERE Staff_ID = %s", [staff_id])
            
            conn.commit()
            flash('Staff member deleted successfully', 'success')
        else:
            flash('Staff member not found', 'danger')
            
        cur.close()
        conn.close()
        
    except Exception as e:
        error_msg = f"Error deleting staff: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        
    return redirect(url_for('staff.dashboard'))

# Staff list route
@staff_bp.route('/staff/list')
@staff_login_required
def staff_list():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))

        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM Staff
            ORDER BY Staff_ID
        """)
        staff_list = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('staff_list.html', staff_list=staff_list, active_page="staff")
    except Exception as e:
        error_msg = f"Error retrieving staff list: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.dashboard'))

# Doctors list route
@staff_bp.route('/doctors/list')
@staff_login_required
def doctors_list():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))

        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM Doctor
            ORDER BY Doctor_ID
        """)
        doctors_list = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('doctors_list.html', doctors_list=doctors_list, active_page="doctors")
    except Exception as e:
        error_msg = f"Error retrieving doctors list: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.dashboard'))

# Patients list route
@staff_bp.route('/patients/list')
@staff_login_required
def patients_list():
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))
        
        cur = conn.cursor()
        
        # Get all patients
        cur.execute("""
            SELECT * FROM Patient
            ORDER BY Patient_ID
        """)
        patients_list = cur.fetchall()
        
        cur.close()
        
        return render_template('patients_list.html', patients_list=patients_list, active_page="patients")
    except Exception as e:
        error_msg = f"Error retrieving patients list: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.dashboard'))

# Billing list route
@staff_bp.route('/billing/list')
@staff_login_required
def billing_list():
    try:
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.dashboard'))
        
        cur = conn.cursor()
        
        # Check if Billing table exists
        cur.execute("SHOW TABLES LIKE 'Billing'")
        if cur.fetchone() is None:
            flash('Billing table does not exist', 'warning')
            cur.close()
            return render_template('billing_list.html', billing_list=[], active_page="billing")
        
        # Get all billing records with patient names
        cur.execute("""
            SELECT b.*, p.Name as PatientName
            FROM Billing b
            LEFT JOIN Patient p ON b.Patient_ID = p.Patient_ID
            ORDER BY b.Bill_Date DESC
        """)
        billing_list = cur.fetchall()
        
        # Calculate the sum of all completed bills
        total_paid_amount = 0
        for bill in billing_list:
            if bill['Payment_Status'] == 'Paid' or bill['Payment_Status'] == 'Completed':
                total_paid_amount += float(bill['Total_Amount'])
        
        cur.close()
        
        return render_template('billing_list.html', billing_list=billing_list, active_page="billing", total_paid_amount=total_paid_amount)
    except Exception as e:
        error_msg = f"Error retrieving billing list: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.dashboard'))

# Mark bill as completed route
@staff_bp.route('/billing/complete/<int:bill_id>', methods=['POST'])
@staff_login_required
def mark_bill_completed(bill_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.billing_list'))
            
        cur = conn.cursor()
        
        # Update bill status to completed
        cur.execute("""
            UPDATE Billing 
            SET Payment_Status = 'Completed'
            WHERE Bill_ID = %s
        """, [bill_id])
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Bill marked as completed successfully', 'success')
    except Exception as e:
        error_msg = f"Error updating bill status: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
    
    return redirect(url_for('staff.billing_list'))

# Mark bill as pending route
@staff_bp.route('/billing/pending/<int:bill_id>', methods=['POST'])
@staff_login_required
def mark_bill_pending(bill_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.billing_list'))
            
        cur = conn.cursor()
        
        # Update bill status to pending
        cur.execute("""
            UPDATE Billing 
            SET Payment_Status = 'Pending'
            WHERE Bill_ID = %s
        """, [bill_id])
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Bill marked as pending successfully', 'success')
    except Exception as e:
        error_msg = f"Error updating bill status: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
    
    return redirect(url_for('staff.billing_list'))

# Delete bill route
@staff_bp.route('/billing/delete/<int:bill_id>', methods=['POST'])
@staff_login_required
def delete_bill(bill_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.billing_list'))
            
        cur = conn.cursor()
        
        # Delete the bill
        cur.execute("DELETE FROM Billing WHERE Bill_ID = %s", [bill_id])
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Bill deleted successfully', 'success')
    except Exception as e:
        error_msg = f"Error deleting bill: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
    
    return redirect(url_for('staff.billing_list'))

# Add bill route
@staff_bp.route('/billing/add', methods=['GET', 'POST'])
@staff_login_required
def add_bill():
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.form['patient_id']
            amount = request.form['amount']
            purpose = request.form['purpose']
            payment_status = request.form['payment_status']
            
            # Connect to database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('staff.add_bill'))
                
            cur = conn.cursor()
            
            # Insert new bill record
            cur.execute("""
                INSERT INTO Billing (Patient_ID, Bill_Date, Total_Amount, Purpose, Payment_Status)
                VALUES (%s, CURDATE(), %s, %s, %s)
            """, [patient_id, amount, purpose, payment_status])
            
            conn.commit()
            
            # Get the newly inserted bill ID
            bill_id = cur.lastrowid
            
            cur.close()
            conn.close()
            
            flash(f'Bill added successfully with ID: {bill_id}', 'success')
            return redirect(url_for('staff.billing_list'))
            
        except Exception as e:
            error_msg = f"Error adding bill: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return redirect(url_for('staff.add_bill'))
    
    # GET request - fetch patient list and render add bill form
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.billing_list'))
            
        cur = conn.cursor()
        
        # Fetch all patients for the dropdown
        cur.execute("SELECT Patient_ID, Name FROM Patient ORDER BY Name")
        patients = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('billing_add.html', patients=patients, active_page="billing")
        
    except Exception as e:
        error_msg = f"Error loading add bill form: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, 'danger')
        return redirect(url_for('staff.billing_list'))

@staff_bp.route('/quick-edit/<int:staff_id>', methods=['POST'])
@staff_login_required
def update_staff_details(staff_id):
    try:
        if request.method == 'POST':
            # Get form data
            staff_role = request.form['staff_role']
            shift_timing = request.form['shift_timing']
            
            # Update the database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('staff.staff_list'))
                
            cur = conn.cursor()
            cur.execute("""
                UPDATE Staff 
                SET Staff_Role = %s, Shift_Timing = %s 
                WHERE Staff_ID = %s
            """, (staff_role, shift_timing, staff_id))
            conn.commit()
            cur.close()
            conn.close()
            
            flash("Staff information updated successfully", "success")
        return redirect(url_for('staff.staff_list'))
    except Exception as e:
        error_msg = f"Error updating staff: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, "danger")
        return redirect(url_for('staff.staff_list'))

@staff_bp.route('/quick-delete/<int:staff_id>', methods=['POST'])
@staff_login_required
def quick_delete_staff(staff_id):
    try:
        # Delete the staff record
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.staff_list'))
            
        cur = conn.cursor()
        cur.execute("DELETE FROM Staff WHERE Staff_ID = %s", (staff_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Staff deleted successfully", "success")
        return redirect(url_for('staff.staff_list'))
    except Exception as e:
        error_msg = f"Error deleting staff: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, "danger")
        return redirect(url_for('staff.staff_list'))

# Add doctor form route for staff
@staff_bp.route('/add-doctor', methods=['GET', 'POST'])
@staff_login_required
def add_doctor_form():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form.get('dob', '')
            contact = request.form.get('contact', '')
            email = request.form.get('email', '')
            address = request.form.get('address', '')
            specialization = request.form['specialization']
            qualifications = request.form.get('qualifications', '')
            experience = request.form.get('experience', 0)
            charges = request.form.get('charges', 500)
            passcode = request.form.get('passcode', '1234')  # Default passcode
            
            # Connect to database
            conn = get_db_connection()
            if not conn:
                flash('Database connection error', 'danger')
                return redirect(url_for('staff.doctors_list'))
                
            cur = conn.cursor()
            
            # Insert doctor
            cur.execute("""
                INSERT INTO Doctor (
                    Name, Gender, Date_of_Birth, Contact_Number, Email, Address,
                    Specialization, Qualifications, Experience, Charges, Passcode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name, gender, dob, contact, email, address,
                specialization, qualifications, experience, charges, passcode
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Doctor added successfully', 'success')
            return redirect(url_for('staff.doctors_list'))
            
        except Exception as e:
            error_msg = f"Error adding doctor: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            flash(error_msg, 'danger')
            return redirect(url_for('staff.doctors_list'))
    
    # GET request - show form
    return render_template('doctor_add.html', active_page="doctors")

# Delete doctor route for staff
@staff_bp.route('/delete-doctor/<int:doctor_id>', methods=['POST'])
@staff_login_required
def delete_doctor(doctor_id):
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return redirect(url_for('staff.doctors_list'))
            
        cur = conn.cursor()
        
        # Delete the doctor
        cur.execute("DELETE FROM Doctor WHERE Doctor_ID = %s", (doctor_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Doctor deleted successfully", "success")
        return redirect(url_for('staff.doctors_list'))
    except Exception as e:
        error_msg = f"Error deleting doctor: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        flash(error_msg, "danger")
        return redirect(url_for('staff.doctors_list')) 