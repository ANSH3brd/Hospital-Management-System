import pymysql

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
    print("Database connection successful")
    
    # Create a test patient with ID 110
    with connection.cursor() as cursor:
        # Check if Patient table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'Patient'")
        if cursor.fetchone() is None:
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
            print("Created Patient table")
            connection.commit()
        
        # Check if patient with ID 110 exists
        cursor.execute("SELECT * FROM Patient WHERE Patient_ID = 110")
        existing_patient = cursor.fetchone()
        
        if existing_patient:
            # Update existing patient
            cursor.execute("""
                UPDATE Patient SET
                    Name = 'Priyanshu Kumar Singh',
                    Gender = 'Male',
                    Date_of_Birth = '2000-01-01',
                    Age = 23,
                    Contact_Number = '9876543210',
                    Address = 'Varanasi, Uttar Pradesh',
                    Email = 'priyanshu@example.com',
                    Blood_Group = 'O+',
                    Medical_History = 'No significant medical history. Patient is in good health.',
                    Insurance_Details = 'Insurance ID: 12345'
                WHERE Patient_ID = 110
            """)
            print("Updated patient with ID 110")
        else:
            # Insert new patient
            cursor.execute("""
                INSERT INTO Patient (
                    Patient_ID, Name, Gender, Date_of_Birth, Age, 
                    Contact_Number, Address, Email, Blood_Group, 
                    Medical_History, Insurance_Details
                ) VALUES (
                    110, 'Priyanshu Kumar Singh', 'Male', '2000-01-01', 23,
                    '9876543210', 'Varanasi, Uttar Pradesh', 'priyanshu@example.com', 'O+',
                    'No significant medical history. Patient is in good health.', 'Insurance ID: 12345'
                )
            """)
            print("Inserted new patient with ID 110")
        
        # Commit changes
        connection.commit()
        
        # Verify patient data
        cursor.execute("SELECT * FROM Patient WHERE Patient_ID = 110")
        patient = cursor.fetchone()
        if patient:
            print("\nPatient data for ID 110:")
            for key, value in patient.items():
                print(f"  {key}: {value}")
        else:
            print("\nFailed to retrieve patient with ID 110")
    
    # Close connection
    connection.close()
    print("\nDatabase connection closed")
    
except Exception as e:
    print(f"Error: {str(e)}") 