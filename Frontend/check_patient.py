import pymysql
import json

# Connect to the database
try:
    # Connect to the database
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='iAf_49512',
        database='hospital_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Database connection successful")
    
    # Execute queries
    with connection.cursor() as cursor:
        # Check if Patient table exists
        cursor.execute("SHOW TABLES LIKE 'Patient'")
        if cursor.fetchone():
            print("Patient table exists")
            
            # Get table structure
            cursor.execute("DESCRIBE Patient")
            columns = cursor.fetchall()
            print("\nPatient table structure:")
            for col in columns:
                print(f"- {col['Field']} ({col['Type']})")
            
            # Check for patient with ID 110
            cursor.execute("SELECT * FROM Patient WHERE Patient_ID = 110")
            patient = cursor.fetchone()
            
            if patient:
                print("\nPatient data for ID 110:")
                print(json.dumps(patient, indent=2, default=str))
            else:
                print("\nNo patient found with ID 110")
                
            # Get all patient IDs
            cursor.execute("SELECT Patient_ID FROM Patient")
            patients = cursor.fetchall()
            print("\nAll Patient IDs:")
            for p in patients:
                print(f"- {p['Patient_ID']}")
        else:
            print("Patient table does not exist")
    
    # Close connection
    connection.close()
    print("\nDatabase connection closed")
    
except Exception as e:
    print(f"Error: {str(e)}") 