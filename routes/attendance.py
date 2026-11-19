from datetime import datetime, date, time
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Attendance, AttendanceRemarks, Member, Workout

attendance_bp = Blueprint('attendance', __name__)

def compute_duration(check_in_str, check_out_str):
    """Calculates duration in minutes between check-in and check-out time strings."""
    if not check_in_str or not check_out_str:
        return 0
    try:
        t_in = datetime.strptime(check_in_str, '%H:%M' if len(check_in_str) == 5 else '%H:%M:%S')
        t_out = datetime.strptime(check_out_str, '%H:%M' if len(check_out_str) == 5 else '%H:%M:%S')
        diff_seconds = (t_out - t_in).total_seconds()
        if diff_seconds < 0:
            return -1  # error code
        return int(diff_seconds // 60)
    except Exception:
        return 0

@attendance_bp.route('/')
def index():
    date_filter = request.args.get('date', '').strip()
    member_filter = request.args.get('member_id', '').strip()
    workout_filter = request.args.get('workout_id', '').strip()

    query = Attendance.query

    if date_filter:
        try:
            d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Attendance.Date == d)
        except ValueError:
            pass

    if member_filter and member_filter.isdigit():
        query = query.filter(Attendance.Member_ID == int(member_filter))

    if workout_filter and workout_filter.isdigit():
        query = query.filter(Attendance.Workout_ID == int(workout_filter))

    attendances = query.order_by(Attendance.Date.desc(), Attendance.Check_In_Time.desc()).all()
    members = Member.query.order_by(Member.Name.asc()).all()
    workouts = Workout.query.order_by(Workout.Workout_Name.asc()).all()

    return render_template(
        'attendance/index.html',
        attendances=attendances,
        members=members,
        workouts=workouts,
        date_filter=date_filter,
        member_filter=member_filter,
        workout_filter=workout_filter
    )


@attendance_bp.route('/add', methods=['GET', 'POST'])
def add():
    members = Member.query.filter_by(Status='Active').order_by(Member.Name.asc()).all()
    workouts = Workout.query.order_by(Workout.Workout_Name.asc()).all()
    default_date = date.today().strftime('%Y-%m-%d')
    default_time = datetime.now().strftime('%H:%M')

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        workout_id_str = request.form.get('workout_id', '').strip()
        date_str = request.form.get('date', '').strip()
        check_in_str = request.form.get('check_in_time', '').strip()
        check_out_str = request.form.get('check_out_time', '').strip()
        remark_text = request.form.get('remarks', '').strip()

        errors = []
        if not member_id_str:
            errors.append("Member is required.")
        if not workout_id_str:
            errors.append("Workout routine is required.")
        if not date_str:
            errors.append("Date is required.")
        if not check_in_str:
            errors.append("Check-in time is required.")

        try:
            att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid date format.")
            att_date = None

        try:
            t_in = datetime.strptime(check_in_str, '%H:%M' if len(check_in_str) == 5 else '%H:%M:%S').time()
        except ValueError:
            errors.append("Invalid Check-In time.")
            t_in = None

        t_out = None
        duration_minutes = 0
        if check_out_str:
            try:
                t_out = datetime.strptime(check_out_str, '%H:%M' if len(check_out_str) == 5 else '%H:%M:%S').time()
                duration_minutes = compute_duration(check_in_str, check_out_str)
                if duration_minutes < 0:
                    errors.append("Check-out time cannot be earlier than Check-in time.")
                    duration_minutes = 0
            except ValueError:
                errors.append("Invalid Check-Out time.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'attendance/add.html',
                members=members,
                workouts=workouts,
                form_data=request.form,
                default_date=default_date,
                default_time=default_time
            )

        try:
            new_attendance = Attendance(
                Member_ID=int(member_id_str),
                Workout_ID=int(workout_id_str),
                Date=att_date,
                Check_In_Time=t_in,
                Check_Out_Time=t_out,
                Workout_Duration=duration_minutes
            )
            db.session.add(new_attendance)
            db.session.flush()

            # Add remark if provided
            if remark_text:
                db.session.add(AttendanceRemarks(Attendance_ID=new_attendance.Attendance_ID, Remarks=remark_text))

            db.session.commit()
            flash("Attendance logged successfully!", 'success')
            return redirect(url_for('attendance.show', id=new_attendance.Attendance_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error logging attendance: {str(e)}", 'danger')
            return render_template(
                'attendance/add.html',
                members=members,
                workouts=workouts,
                form_data=request.form,
                default_date=default_date,
                default_time=default_time
            )

    return render_template(
        'attendance/add.html',
        members=members,
        workouts=workouts,
        default_date=default_date,
        default_time=default_time
    )


@attendance_bp.route('/<int:id>')
def show(id):
    attendance = Attendance.query.get_or_404(id)
    return render_template('attendance/show.html', attendance=attendance)


@attendance_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    attendance = Attendance.query.get_or_404(id)
    members = Member.query.order_by(Member.Name.asc()).all()
    workouts = Workout.query.order_by(Workout.Workout_Name.asc()).all()

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        workout_id_str = request.form.get('workout_id', '').strip()
        date_str = request.form.get('date', '').strip()
        check_in_str = request.form.get('check_in_time', '').strip()
        check_out_str = request.form.get('check_out_time', '').strip()

        errors = []
        if not member_id_str or not workout_id_str or not date_str or not check_in_str:
            errors.append("All basic attendance fields are required.")

        try:
            att_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            t_in = datetime.strptime(check_in_str, '%H:%M' if len(check_in_str) == 5 else '%H:%M:%S').time()
        except ValueError:
            errors.append("Invalid date or check-in time format.")
            att_date, t_in = None, None

        t_out = None
        duration_minutes = 0
        if check_out_str:
            try:
                t_out = datetime.strptime(check_out_str, '%H:%M' if len(check_out_str) == 5 else '%H:%M:%S').time()
                duration_minutes = compute_duration(check_in_str, check_out_str)
                if duration_minutes < 0:
                    errors.append("Check-out time cannot be earlier than Check-in time.")
                    duration_minutes = 0
            except ValueError:
                errors.append("Invalid check-out time format.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('attendance/edit.html', attendance=attendance, members=members, workouts=workouts)

        try:
            attendance.Member_ID = int(member_id_str)
            attendance.Workout_ID = int(workout_id_str)
            attendance.Date = att_date
            attendance.Check_In_Time = t_in
            attendance.Check_Out_Time = t_out
            attendance.Workout_Duration = duration_minutes

            db.session.commit()
            flash("Attendance record updated successfully!", 'success')
            return redirect(url_for('attendance.show', id=attendance.Attendance_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating attendance: {str(e)}", 'danger')

    return render_template('attendance/edit.html', attendance=attendance, members=members, workouts=workouts)


@attendance_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    attendance = Attendance.query.get_or_404(id)
    try:
        db.session.delete(attendance)
        db.session.commit()
        flash("Attendance record deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting attendance: {str(e)}", 'danger')
    return redirect(url_for('attendance.index'))


@attendance_bp.route('/<int:id>/add_remark', methods=['POST'])
def add_remark(id):
    attendance = Attendance.query.get_or_404(id)
    remark_text = request.form.get('remark', '').strip()

    if not remark_text:
        flash("Remark text cannot be empty.", 'danger')
        return redirect(url_for('attendance.show', id=id))

    existing = AttendanceRemarks.query.filter_by(Attendance_ID=id, Remarks=remark_text).first()
    if existing:
        flash("This remark is already recorded for this attendance session.", 'warning')
        return redirect(url_for('attendance.show', id=id))

    try:
        new_remark = AttendanceRemarks(Attendance_ID=id, Remarks=remark_text)
        db.session.add(new_remark)
        db.session.commit()
        flash("Remark added successfully!", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding remark: {str(e)}", 'danger')

    return redirect(url_for('attendance.show', id=id))


@attendance_bp.route('/<int:id>/delete_remark', methods=['POST'])
def delete_remark(id):
    remark_text = request.form.get('remark', '').strip()
    remark = AttendanceRemarks.query.filter_by(Attendance_ID=id, Remarks=remark_text).first()
    if remark:
        try:
            db.session.delete(remark)
            db.session.commit()
            flash("Remark removed.", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting remark: {str(e)}", 'danger')
    return redirect(url_for('attendance.show', id=id))
