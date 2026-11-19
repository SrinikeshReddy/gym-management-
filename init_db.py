"""
Database Setup and Initialization Utility
Gym Management System
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def init_mysql():
    import pymysql

    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    dbname = os.getenv('DB_NAME', 'gym_management')

    print(f"[*] Connecting to MySQL Server at {host}:{port} as user '{user}'...")

    try:
        # Step 1: Connect to server without selecting database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("[+] Connected to MySQL Server successfully!")

        with conn.cursor() as cursor:
            print(f"[*] Ensuring database '{dbname}' exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            cursor.execute(f"USE `{dbname}`;")
            conn.commit()
        conn.close()

        # Step 2: Connect to specific database to run schema and sample data
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            charset='utf8mb4',
            autocommit=True
        )

        base_dir = os.path.abspath(os.path.dirname(__file__))
        schema_path = os.path.join(base_dir, 'schema.sql')
        sample_path = os.path.join(base_dir, 'sample_data.sql')

        print("[*] Executing schema.sql to create 10 tables...")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute statements
        with conn.cursor() as cursor:
            for statement in schema_sql.split(';'):
                stmt = statement.strip()
                if stmt and not stmt.lower().startswith('create database') and not stmt.lower().startswith('use '):
                    cursor.execute(stmt)

        print("[+] All 10 tables created successfully in MySQL!")

        print("[*] Executing sample_data.sql to insert sample records...")
        with open(sample_path, 'r', encoding='utf-8') as f:
            sample_sql = f.read()

        with conn.cursor() as cursor:
            for statement in sample_sql.split(';'):
                stmt = statement.strip()
                if stmt and not stmt.lower().startswith('use '):
                    cursor.execute(stmt)

        print("[+] Sample data inserted successfully!")

        # Verify table counts
        tables = [
            'MEMBER', 'MEMBER_ADDRESS', 'TRAINER', 'TRAINER_CERTIFICATION',
            'WORKOUT', 'MEMBERSHIP', 'PAYMENT', 'ATTENDANCE',
            'ATTENDANCE_REMARKS', 'PARTICIPATES_IN'
        ]
        print("\n================ VERIFICATION SUMMARY ================")
        with conn.cursor() as cursor:
            for tbl in tables:
                cursor.execute(f"SELECT COUNT(*) AS c FROM `{tbl}`")
                count = cursor.fetchone()[0]
                print(f" - {tbl.ljust(25)} : {count} rows")
        print("=======================================================\n")
        print("[SUCCESS] MySQL database initialized and ready!")
        conn.close()
        return True

    except pymysql.err.OperationalError as e:
        print(f"\n[!] MySQL Connection Failed: {e}")
        print("    Please verify your MySQL Server is running and DB_PASSWORD is correct in .env")
        return False
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        return False

def init_sqlite():
    """Fallback initialization for SQLite when MySQL server is not locally configured."""
    print("\n[*] Initializing SQLite database (gym_management.db)...")
    from app import create_app
    from models import db
    
    os.environ['USE_SQLITE'] = 'true'
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Load sample data if empty
        from models import Member
        if Member.query.count() == 0:
            print("[*] Populating SQLite with sample data...")
            import sqlite3
            conn = sqlite3.connect('gym_management.db')
            with open('sample_data.sql', 'r', encoding='utf-8') as f:
                content = f.read()
            # Clean MySQL-specific commands
            lines = []
            for line in content.splitlines():
                if any(line.strip().upper().startswith(x) for x in ['USE ', 'SET FOREIGN_KEY_CHECKS', 'TRUNCATE TABLE']):
                    continue
                lines.append(line)
            clean_sql = '\n'.join(lines)
            
            cursor = conn.cursor()
            for stmt in clean_sql.split(';'):
                s = stmt.strip()
                if s:
                    try:
                        cursor.execute(s)
                    except Exception:
                        pass
            conn.commit()
            conn.close()
            print("[+] SQLite database initialized with sample data!")
        else:
            print("[+] SQLite database already contains data.")

if __name__ == '__main__':
    if '--sqlite' in sys.argv:
        init_sqlite()
    else:
        success = init_mysql()
        if not success:
            print("\n[NOTE] If you want to use SQLite fallback temporarily, run: python init_db.py --sqlite")
            print("       Or set DB_PASSWORD in .env and run: python init_db.py")
