"""
Centralized database module for the Face Recognition System.
Uses config.py for database connection instead of hardcoded credentials.
"""
from config import get_db_connection


def load_attendance_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Student_id, Student_name, Roll, Dep, Date, Status FROM attendance")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No attendance data found."
        
        records = []
        for row in rows:
            records.append(
                f"ID {row[0]}, Name {row[1]}, Roll {row[2]}, "
                f"Dept {row[3]}, Date {row[4]}, Status {row[5]}"
            )
        
        return "\n".join(records)
        
    except Exception as e:
        return f"Error loading attendance data: {str(e)}"
