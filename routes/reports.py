from datetime import datetime, date
from flask import Blueprint, render_template, request
from sqlalchemy import func, desc
from models import (
    db, Member, Membership, Payment, Trainer, Workout, Attendance, ParticipatesIn
)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def index():
    report_type = request.args.get('type', 'active_members')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    data = {}

    # 1. Active Members Report
    if report_type == 'active_members':
        data['members'] = Member.query.filter_by(Status='Active')\
                                      .order_by(Member.Join_Date.desc()).all()

    # 2. Expired Memberships Report
    elif report_type == 'expired_memberships':
        data['memberships'] = Membership.query.filter(
            (Membership.Status == 'Expired') | (Membership.End_Date < date.today())
        ).order_by(Membership.End_Date.desc()).all()

    # 3. Membership Revenue Report (GROUP BY Plan_Name)
    elif report_type == 'membership_revenue':
        plan_revenue = db.session.query(
            Membership.Plan_Name,
            func.count(Membership.Membership_ID).label('subscribers'),
            func.coalesce(func.sum(Membership.Amount), 0).label('total_revenue'),
            func.coalesce(func.avg(Membership.Amount), 0).label('avg_revenue'),
            func.coalesce(func.min(Membership.Amount), 0).label('min_revenue'),
            func.coalesce(func.max(Membership.Amount), 0).label('max_revenue')
        ).group_by(Membership.Plan_Name).all()

        total_rev = db.session.query(func.coalesce(func.sum(Membership.Amount), 0)).scalar() or 0
        total_subs = db.session.query(func.count(Membership.Membership_ID)).scalar() or 0

        data['plan_revenue'] = plan_revenue
        data['grand_total'] = float(total_rev)
        data['total_subscribers'] = total_subs

    # 4. Payment Status Report (GROUP BY Status and Payment_Method)
    elif report_type == 'payment_status':
        status_breakdown = db.session.query(
            Payment.Status,
            func.count(Payment.Payment_ID).label('count'),
            func.coalesce(func.sum(Payment.Amount), 0).label('total_amount')
        ).group_by(Payment.Status).all()

        method_breakdown = db.session.query(
            Payment.Payment_Method,
            func.count(Payment.Payment_ID).label('count'),
            func.coalesce(func.sum(Payment.Amount), 0).label('total_amount')
        ).filter(Payment.Status == 'Success')\
         .group_by(Payment.Payment_Method).all()

        data['status_breakdown'] = status_breakdown
        data['method_breakdown'] = method_breakdown

    # 5. Trainer Workload Report (JOIN and GROUP BY)
    elif report_type == 'trainer_workload':
        workload = db.session.query(
            Trainer.Trainer_ID,
            Trainer.Name,
            Trainer.Specialization,
            Trainer.Experience_Years,
            Trainer.Salary,
            func.count(func.distinct(Workout.Workout_ID)).label('workouts_count'),
            func.count(func.distinct(ParticipatesIn.Member_ID)).label('trainees_count')
        ).outerjoin(Workout, Trainer.Trainer_ID == Workout.Trainer_ID)\
         .outerjoin(ParticipatesIn, Workout.Workout_ID == ParticipatesIn.Workout_ID)\
         .group_by(Trainer.Trainer_ID, Trainer.Name, Trainer.Specialization, Trainer.Experience_Years, Trainer.Salary)\
         .order_by(desc('trainees_count')).all()

        data['workload'] = workload

    # 6. Workout Participation Report (N:M Aggregations)
    elif report_type == 'workout_participation':
        participation = db.session.query(
            Workout.Workout_ID,
            Workout.Workout_Name,
            Workout.Difficulty_Level,
            Workout.Calories_Burn,
            Trainer.Name.label('trainer_name'),
            func.count(func.distinct(ParticipatesIn.Member_ID)).label('enrolled_members'),
            func.count(func.distinct(Attendance.Attendance_ID)).label('attendance_sessions')
        ).outerjoin(Trainer, Workout.Trainer_ID == Trainer.Trainer_ID)\
         .outerjoin(ParticipatesIn, Workout.Workout_ID == ParticipatesIn.Workout_ID)\
         .outerjoin(Attendance, Workout.Workout_ID == Attendance.Workout_ID)\
         .group_by(Workout.Workout_ID, Workout.Workout_Name, Workout.Difficulty_Level, Workout.Calories_Burn, Trainer.Name)\
         .order_by(desc('enrolled_members')).all()

        data['participation'] = participation

    # 7. Daily Attendance Report (with date range filters)
    elif report_type == 'daily_attendance':
        query = db.session.query(
            Attendance.Date,
            func.count(Attendance.Attendance_ID).label('total_checkins'),
            func.avg(Attendance.Workout_Duration).label('avg_duration')
        )
        if date_from:
            try:
                df = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Attendance.Date >= df)
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Attendance.Date <= dt)
            except ValueError:
                pass

        daily = query.group_by(Attendance.Date).order_by(Attendance.Date.desc()).all()
        data['daily'] = daily

    # 8. Monthly Attendance Report
    elif report_type == 'monthly_attendance':
        # Use strftime formatted query for SQLite/MySQL compatibility
        records = db.session.query(
            Attendance.Date,
            Attendance.Workout_Duration
        ).all()
        
        # Group by YYYY-MM in Python for 100% cross-database compatibility (MySQL & SQLite)
        month_summary = {}
        for r in records:
            m_key = r.Date.strftime('%Y-%m')
            if m_key not in month_summary:
                month_summary[m_key] = {'count': 0, 'duration': 0}
            month_summary[m_key]['count'] += 1
            month_summary[m_key]['duration'] += (r.Workout_Duration or 0)

        data['monthly'] = sorted(
            [{'month': k, 'count': v['count'], 'duration': v['duration']} for k, v in month_summary.items()],
            key=lambda x: x['month'],
            reverse=True
        )

    # 9. Member Attendance History Report
    elif report_type == 'member_history':
        member_stats = db.session.query(
            Member.Member_ID,
            Member.Name,
            Member.Phone,
            Member.Status,
            func.count(Attendance.Attendance_ID).label('visit_count'),
            func.coalesce(func.sum(Attendance.Workout_Duration), 0).label('total_minutes'),
            func.max(Attendance.Date).label('last_visit')
        ).outerjoin(Attendance, Member.Member_ID == Attendance.Member_ID)\
         .group_by(Member.Member_ID, Member.Name, Member.Phone, Member.Status)\
         .order_by(desc('visit_count')).all()

        data['member_stats'] = member_stats

    return render_template(
        'reports.html',
        report_type=report_type,
        data=data,
        date_from=date_from,
        date_to=date_to
    )
