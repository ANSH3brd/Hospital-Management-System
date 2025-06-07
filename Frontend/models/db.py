from flask_mysqldb import MySQL
from flask import current_app, Flask
import time
import pymysql
import traceback

mysql = None

def init_app(app):
    global mysql
    try:
        # Configure MySQL directly on the app object
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'iAf_49512'
        app.config['MYSQL_DB'] = 'hospital_db'
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        
        mysql = MySQL(app)
        
        # Test connection
        with app.app_context():
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
        print("Database connection successfully initialized")
        return mysql
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return None

def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='iAf_49512',
            database='hospital_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        print(traceback.format_exc())
        return None

def get_db():
    try:
        class MySQLWrapper:
            def __init__(self, connection):
                self.connection = connection
                
        connection = get_db_connection()
        if connection is None:
            return None
            
        return MySQLWrapper(connection)
    except Exception as e:
        print(f"Error in get_db: {str(e)}")
        print(traceback.format_exc())
        return None 