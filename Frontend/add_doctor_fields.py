import pymysql
import traceback

def add_fields_to_doctor_table():
    try:
        # Connect to the database
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db'
        )
        
        cursor = conn.cursor()
        
        # Check if fields already exist to avoid errors
        cursor.execute("SHOW COLUMNS FROM Doctor LIKE 'Charges'")
        if not cursor.fetchone():
            print("Adding Charges field to Doctor table...")
            cursor.execute("ALTER TABLE Doctor ADD COLUMN Charges DECIMAL(10,2) DEFAULT 500.00")
        
        cursor.execute("SHOW COLUMNS FROM Doctor LIKE 'Pass_Code'")
        if not cursor.fetchone():
            print("Adding Pass_Code field to Doctor table...")
            cursor.execute("ALTER TABLE Doctor ADD COLUMN Pass_Code VARCHAR(50)")
        
        # Commit changes
        conn.commit()
        print("Database updated successfully!")
        
        # Show the updated schema
        cursor.execute("DESCRIBE Doctor")
        print("\nDoctor table schema:")
        for row in cursor.fetchall():
            print(row)
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    add_fields_to_doctor_table() 