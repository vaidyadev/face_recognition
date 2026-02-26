import mysql.connector
import os
from dotenv import load_dotenv
from config import DB_CONFIG
from utils import get_executable_dir

# Load environment variables
env_path = os.path.join(get_executable_dir(), '.env')
load_dotenv(dotenv_path=env_path)

def setup_database():
    print("Starting database setup...")
    
    # 1. Connect to MySQL Server (without database)
    try:
        # Create a copy of config without the database name to connect effectively to the server
        server_config = DB_CONFIG.copy()
        db_name = server_config.pop('database')
        
        print(f"Connecting to MySQL server at {server_config['host']}:{server_config['port']}...")
        conn = mysql.connector.connect(**server_config)
        cursor = conn.cursor()
        
        # 2. Create Database
        print(f"Creating database '{db_name}' if it does not exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # 3. Create Tables
        
        # Table: register
        print("Creating table 'register'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS register (
                firstname VARCHAR(45) DEFAULT NULL,
                lastname VARCHAR(45) DEFAULT NULL,
                contact VARCHAR(45) DEFAULT NULL,
                email VARCHAR(45) NOT NULL,
                securityq VARCHAR(45) DEFAULT NULL,
                securitya VARCHAR(45) DEFAULT NULL,
                password VARCHAR(45) DEFAULT NULL,
                PRIMARY KEY (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Table: student
        # Note: Updated to include TelegramID based on application requirements
        print("Creating table 'student'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                Dep VARCHAR(45) DEFAULT NULL,
                Course VARCHAR(45) DEFAULT NULL,
                Year VARCHAR(45) DEFAULT NULL,
                Semester VARCHAR(45) DEFAULT NULL,
                Student_id VARCHAR(45) NOT NULL,
                Student_name VARCHAR(45) DEFAULT NULL,
                Division VARCHAR(45) DEFAULT NULL,
                Roll VARCHAR(45) DEFAULT NULL,
                Gender VARCHAR(45) DEFAULT NULL,
                Dob VARCHAR(45) DEFAULT NULL,
                Email VARCHAR(45) DEFAULT NULL,
                Phone VARCHAR(45) DEFAULT NULL,
                Address VARCHAR(45) DEFAULT NULL,
                Teacher VARCHAR(45) DEFAULT NULL,
                PhotoSample VARCHAR(45) DEFAULT NULL,
                TelegramID VARCHAR(45) DEFAULT NULL,
                PRIMARY KEY (Student_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Table: attendance
        print("Creating table 'attendance'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Student_id VARCHAR(50),
                Student_name VARCHAR(100),
                Roll VARCHAR(50),
                Dep VARCHAR(100),
                Time VARCHAR(50),
                Date VARCHAR(50),
                Status VARCHAR(50)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        conn.commit()
        print("Database setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    setup_database()
