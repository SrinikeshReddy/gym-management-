from datetime import date
from flask import Blueprint, render_template
from sqlalchemy import func
from models import db, Member, Membership, Payment, Trainer, Workout, Attendance

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
def index():
    """
    Admin Dashboard: Calculates live metrics and recent activities from the database.
    """
    today = date.today()

    # Core Metric Counters
    total_members = Member.query.count()
    active_members = Member.query.filter_by(Status='Active').count()
    active_memberships = Membership.query.filter_by(Status='Active').count()
    total_payments_revenue = float(
        db.session.query(func.coalesce(func.sum(Payment.Amount), 0))
        .filter(Payment.Status == 'Success')
        .scalar() or 0.0
    )
    today_attendance_count = Attendance.query.filter_by(Date=today).count()
    total_trainers = Trainer.query.count()
    total_workouts = Workout.query.count()

    # Recent Activity Records
    recent_members = Member.query.order_by(Member.Member_ID.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.Payment_Date.desc(), Payment.Payment_ID.desc()).limit(5).all()

    today_attendance = Attendance.query.filter_by(Date=today).order_by(Attendance.Check_In_Time.desc()).limit(5).all()
    if today_attendance:
        recent_attendance = today_attendance
        is_today_attendance = True
    else:
        recent_attendance = Attendance.query.order_by(Attendance.Date.desc(), Attendance.Check_In_Time.desc()).limit(5).all()
        is_today_attendance = False

    return render_template(
        'dashboard.html',
        total_members=total_members,
        active_members=active_members,
        active_memberships=active_memberships,
        total_payments_revenue=total_payments_revenue,
        today_attendance_count=today_attendance_count,
        total_trainers=total_trainers,
        total_workouts=total_workouts,
        recent_members=recent_members,
        recent_payments=recent_payments,
        recent_attendance=recent_attendance,
        is_today_attendance=is_today_attendance
    )
