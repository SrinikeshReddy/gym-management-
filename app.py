import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config, get_database_uri
from models import db
from routes import register_blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Ensure fresh evaluated URI
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()

    # Initialize extensions
    db.init_app(app)

    # Enable SQLite foreign key cascades
    with app.app_context():
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # Enforce foreign key constraints and cascade deletes in SQLite
            if type(dbapi_connection).__name__ == "Connection":
                try:
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON;")
                    cursor.close()
                except Exception:
                    pass

    # Register all application blueprints
    register_blueprints(app)

    # Ensure MEMBER table has Password column
    with app.app_context():
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("SELECT Password FROM MEMBER LIMIT 1"))
                except Exception:
                    conn.execute(text("ALTER TABLE MEMBER ADD COLUMN Password VARCHAR(255) DEFAULT 'member123'"))
                    conn.commit()
        except Exception:
            pass

    # Authentication and Role-based Access Middleware
    @app.before_request
    def check_auth():
        if request.path.startswith('/static') or request.path == '/favicon.ico':
            return None

        endpoint = request.endpoint
        if endpoint in ('auth.login', 'auth.logout', 'auth.register', None):
            return None

        if 'role' not in session:
            flash("Please log in to access the Gym Management System.", "warning")
            return redirect(url_for('auth.login', next=request.path))

        if session.get('role') == 'user':
            allowed_member_endpoints = {
                'auth.portal',
                'auth.logout',
                'payments.invoice',
                'members.show',
                'favicon'
            }
            if endpoint == 'dashboard.index':
                return redirect(url_for('auth.portal'))

            if endpoint not in allowed_member_endpoints:
                flash("Access restricted to Member Portal. Administrator role required for administrative functions.", "warning")
                return redirect(url_for('auth.portal'))

    # Favicon route to prevent 404 console errors
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.svg')

    # Context processors for templates
    @app.context_processor
    def inject_global_vars():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        engine_name = 'MySQL 8.x' if 'mysql' in uri else 'SQLite'
        return {
            'current_year': datetime.now().year,
            'app_title': 'Gym Management System',
            'db_engine': engine_name,
            'is_logged_in': 'role' in session,
            'is_admin': session.get('role') == 'admin',
            'is_user': session.get('role') == 'user',
            'current_user_name': session.get('user_name', ''),
            'current_role': session.get('role', '')
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Not Found", error_message="The requested resource or page was not found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Server Error", error_message="An internal database or application error occurred."), 500

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[Notice] Database check: {e}")

    port = int(os.getenv('PORT', 5000))
    print(f"\n=======================================================")
    print(f" GYM MANAGEMENT SYSTEM")
    print(f" Web Application Server running at: http://127.0.0.1:{port}/")
    print(f" Active Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"=======================================================\n")
    app.run(host='127.0.0.1', port=port, debug=True)


    
