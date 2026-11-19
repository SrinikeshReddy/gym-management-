from flask import Blueprint

# Blueprints
from .auth import auth_bp
from .dashboard import dashboard_bp
from .members import members_bp
from .trainers import trainers_bp
from .workouts import workouts_bp
from .memberships import memberships_bp
from .payments import payments_bp
from .attendance import attendance_bp
from .reports import reports_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp, url_prefix='/members')
    app.register_blueprint(trainers_bp, url_prefix='/trainers')
    app.register_blueprint(workouts_bp, url_prefix='/workouts')
    app.register_blueprint(memberships_bp, url_prefix='/memberships')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(reports_bp, url_prefix='/reports')
