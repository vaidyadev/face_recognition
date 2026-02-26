"""
Centralized configuration module for the Face Recognition System.
Loads credentials from environment variables (.env file) for security.
"""
import os
from dotenv import load_dotenv
from utils import get_executable_dir

# Load environment variables from .env file
env_path = os.path.join(get_executable_dir(), '.env')
load_dotenv(dotenv_path=env_path)

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'face_recognizer')
}

# Email Configuration
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'user': os.getenv('SMTP_USER', ''),
    'password': os.getenv('SMTP_PASSWORD', '')
}


def get_db_connection():
    """
    Create and return a new database connection using centralized config.
    
    Returns:
        mysql.connector.connection: Active database connection
    
    Raises:
        mysql.connector.Error: If connection fails
    """
    import mysql.connector
    return mysql.connector.connect(**DB_CONFIG)


def get_db_config():
    """
    Returns the database configuration dictionary.
    Useful for modules that need direct access to config values.
    """
    return DB_CONFIG.copy()
