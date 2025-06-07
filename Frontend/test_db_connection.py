import pymysql
import traceback

def test_db_connection():
    try:
        print("Attempting to connect to MySQL database...")
        # Direct connection to MySQL
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Execute a test query
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"Test query result: {result}")
            
            # Test if Doctor table exists and has the necessary fields
            cursor.execute("SHOW TABLES LIKE 'Doctor'")
            if cursor.fetchone():
                print("Doctor table exists")
                
                cursor.execute("DESCRIBE Doctor")
                columns = cursor.fetchall()
                column_names = [col['Field'] for col in columns]
                print(f"Doctor table columns: {column_names}")
                
                # Check for all required fields
                required_fields = ['Charges', 'Passcode', 'Role', 'Shift_Timing']
                missing = [field for field in required_fields if field not in column_names]
                
                if not missing:
                    print("All required fields exist in the Doctor table")
                else:
                    print(f"Warning: Missing fields in Doctor table: {missing}")
                    
                    # Add missing fields
                    for field in missing:
                        if field == 'Charges':
                            cursor.execute("ALTER TABLE Doctor ADD COLUMN Charges DECIMAL(10,2) DEFAULT 500.00")
                            print("Added Charges field to Doctor table")
                        elif field == 'Passcode':
                            cursor.execute("ALTER TABLE Doctor ADD COLUMN Passcode VARCHAR(50)")
                            print("Added Passcode field to Doctor table")
                        elif field == 'Role':
                            cursor.execute("ALTER TABLE Doctor ADD COLUMN Role VARCHAR(50) DEFAULT 'Doctor'")
                            print("Added Role field to Doctor table")
                        elif field == 'Shift_Timing':
                            cursor.execute("ALTER TABLE Doctor ADD COLUMN Shift_Timing VARCHAR(50) DEFAULT 'Day Shift'")
                            print("Added Shift_Timing field to Doctor table")
                
                connection.commit()
                
                # Double-check after adding fields
                cursor.execute("DESCRIBE Doctor")
                columns = cursor.fetchall()
                column_names = [col['Field'] for col in columns]
                print(f"Updated Doctor table columns: {column_names}")
                
                # Test inserting a dummy doctor
                try:
                    cursor.execute("""
                        INSERT INTO Doctor (Name, Gender, Date_of_Birth, Age, Contact_Number, Address,
                        Email, Specialization, Qualifications, Experience, Availability_Status, Department_ID, Charges, Passcode, Role, Shift_Timing)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            "Test Doctor", 
                            "Male", 
                            "1990-01-01", 
                            33, 
                            "1234567890", 
                            "Test Address", 
                            "test@example.com", 
                            "General Medicine", 
                            "MBBS", 
                            0,  # Experience
                            "Available",  # Availability_Status
                            0,  # Department_ID
                            "500", 
                            "testpass123",
                            "Doctor",
                            "Day Shift"
                        ))
                    connection.commit()
                    print("Successfully inserted test doctor")
                    
                    # Clean up test data
                    cursor.execute("DELETE FROM Doctor WHERE Name = 'Test Doctor' AND Email = 'test@example.com'")
                    connection.commit()
                    print("Cleaned up test data")
                except Exception as insert_error:
                    print(f"Error inserting test doctor: {str(insert_error)}")
                    traceback.print_exc()
            else:
                print("Doctor table does not exist!")
        
        # Close connection
        connection.close()
        print("Database connection test successful")
        return True
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_db_connection() 