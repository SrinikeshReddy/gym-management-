import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_database_uri():
    """
    Dynamically determine database URI.
    Tries MySQL connection first. If MySQL is not configured or credentials
    in .env have not been entered yet, falls back to SQLite so the application
    runs seamlessly without crashing.
    """
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
        
    if os.getenv('USE_SQLITE', 'false').lower() in ('1', 'true', 'yes'):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        return f"sqlite:///{os.path.join(base_dir, 'gym_management.db')}"
        
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 3306))
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'gym_management')
    
    # Check if MySQL is accessible with provided credentials
    try:
        import pymysql
        conn = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            connect_timeout=2
        )
        conn.close()
        # MySQL is reachable and database exists!
        encoded_password = quote_plus(db_password) if db_password else ''
        if encoded_password:
            return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        else:
            return f"mysql+pymysql://{db_user}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    except Exception:
        # If MySQL is not yet configured or password in .env is default, fallback to SQLite
        base_dir = os.path.abspath(os.path.dirname(__file__))
        return f"sqlite:///{os.path.join(base_dir, 'gym_management.db')}"

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'gym_management_super_secret_key_2025')
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'gym_management')

    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
