from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Workout, Trainer, Member, ParticipatesIn, Attendance

workouts_bp = Blueprint('workouts', __name__)

@workouts_bp.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    difficulty_filter = request.args.get('difficulty', '').strip()
    trainer_filter = request.args.get('trainer', '').strip()

    query = Workout.query

    if search_query:
        query = query.filter(Workout.Workout_Name.ilike(f'%{search_query}%'))

    if difficulty_filter in ['Easy', 'Medium', 'Hard']:
        query = query.filter(Workout.Difficulty_Level == difficulty_filter)

    if trainer_filter and trainer_filter.isdigit():
        query = query.filter(Workout.Trainer_ID == int(trainer_filter))

    workouts = query.order_by(Workout.Workout_ID.asc()).all()
    trainers = Trainer.query.order_by(Trainer.Name.asc()).all()

    return render_template(
        'workouts/index.html',
        workouts=workouts,
        trainers=trainers,
        search_query=search_query,
        difficulty_filter=difficulty_filter,
        trainer_filter=trainer_filter
    )


@workouts_bp.route('/add', methods=['GET', 'POST'])
def add():
    trainers = Trainer.query.order_by(Trainer.Name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('workout_name', '').strip()
        description = request.form.get('description', '').strip()
        calories_str = request.form.get('calories_burn', '0').strip()
        duration_str = request.form.get('duration_minutes', '0').strip()
        difficulty = request.form.get('difficulty_level', 'Medium').strip()
        trainer_id_str = request.form.get('trainer_id', '').strip()

        errors = []
        if not name:
            errors.append("Workout Name is required.")

        try:
            calories = int(calories_str)
            if calories < 0:
                errors.append("Calories burned cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Calories burned must be an integer.")
            calories = 0

        try:
            duration = int(duration_str)
            if duration <= 0:
                errors.append("Duration must be a positive integer.")
        except (ValueError, TypeError):
            errors.append("Duration must be an integer.")
            duration = 0

        trainer_id = int(trainer_id_str) if (trainer_id_str and trainer_id_str.isdigit()) else None

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('workouts/add.html', trainers=trainers, form_data=request.form)

        try:
            new_workout = Workout(
                Workout_Name=name,
                Description=description,
                Calories_Burn=calories,
                Duration_Minutes=duration,
                Difficulty_Level=difficulty,
                Trainer_ID=trainer_id
            )
            db.session.add(new_workout)
            db.session.commit()
            flash(f"Workout '{new_workout.Workout_Name}' created successfully!", 'success')
            return redirect(url_for('workouts.show', id=new_workout.Workout_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating workout: {str(e)}", 'danger')
            return render_template('workouts/add.html', trainers=trainers, form_data=request.form)

    return render_template('workouts/add.html', trainers=trainers)


@workouts_bp.route('/<int:id>')
def show(id):
    workout = Workout.query.get_or_404(id)
    all_members = Member.query.filter_by(Status='Active').order_by(Member.Name.asc()).all()
    enrolled_member_ids = [p.Member_ID for p in workout.participations]
    
    return render_template(
        'workouts/show.html',
        workout=workout,
        all_members=all_members,
        enrolled_member_ids=enrolled_member_ids
    )


@workouts_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    workout = Workout.query.get_or_404(id)
    trainers = Trainer.query.order_by(Trainer.Name.asc()).all()

    if request.method == 'POST':
        name = request.form.get('workout_name', '').strip()
        description = request.form.get('description', '').strip()
        calories_str = request.form.get('calories_burn', '0').strip()
        duration_str = request.form.get('duration_minutes', '0').strip()
        difficulty = request.form.get('difficulty_level', 'Medium').strip()
        trainer_id_str = request.form.get('trainer_id', '').strip()

        errors = []
        if not name:
            errors.append("Workout Name is required.")

        try:
            calories = int(calories_str)
            if calories < 0:
                errors.append("Calories burned cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Calories burned must be an integer.")

        try:
            duration = int(duration_str)
            if duration <= 0:
                errors.append("Duration must be a positive integer.")
        except (ValueError, TypeError):
            errors.append("Duration must be an integer.")

        trainer_id = int(trainer_id_str) if (trainer_id_str and trainer_id_str.isdigit()) else None

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('workouts/edit.html', workout=workout, trainers=trainers)

        try:
            workout.Workout_Name = name
            workout.Description = description
            workout.Calories_Burn = calories
            workout.Duration_Minutes = duration
            workout.Difficulty_Level = difficulty
            workout.Trainer_ID = trainer_id

            db.session.commit()
            flash(f"Workout '{workout.Workout_Name}' updated successfully!", 'success')
            return redirect(url_for('workouts.show', id=workout.Workout_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating workout: {str(e)}", 'danger')

    return render_template('workouts/edit.html', workout=workout, trainers=trainers)


@workouts_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    workout = Workout.query.get_or_404(id)
    try:
        name = workout.Workout_Name
        db.session.delete(workout)
        db.session.commit()
        flash(f"Workout '{name}' deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting workout: {str(e)}", 'danger')
    return redirect(url_for('workouts.index'))


@workouts_bp.route('/assign', methods=['GET', 'POST'])
def assign():
    members = Member.query.order_by(Member.Name.asc()).all()
    workouts = Workout.query.order_by(Workout.Workout_Name.asc()).all()

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        workout_id_str = request.form.get('workout_id', '').strip()
        target = request.form.get('next') or request.referrer or url_for('workouts.assign')

        if not member_id_str or not workout_id_str:
            flash("Please select both a Member and a Workout.", 'danger')
            return redirect(target)

        member_id = int(member_id_str)
        workout_id = int(workout_id_str)

        # Check duplicate composite key (Member_ID, Workout_ID)
        existing = ParticipatesIn.query.filter_by(Member_ID=member_id, Workout_ID=workout_id).first()
        if existing:
            flash("This member is already enrolled in this workout routine (duplicate prevented).", 'warning')
            return redirect(target)

        try:
            new_participation = ParticipatesIn(Member_ID=member_id, Workout_ID=workout_id)
            db.session.add(new_participation)
            db.session.commit()
            flash("Member assigned to workout successfully!", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error assigning workout: {str(e)}", 'danger')

        return redirect(target)

    # List all current assignments
    assignments = db.session.query(ParticipatesIn).all()
    return render_template('workouts/assign.html', members=members, workouts=workouts, assignments=assignments)


@workouts_bp.route('/<int:workout_id>/remove_member/<int:member_id>', methods=['POST'])
def remove_member(workout_id, member_id):
    participation = ParticipatesIn.query.filter_by(Workout_ID=workout_id, Member_ID=member_id).first()
    if participation:
        try:
            db.session.delete(participation)
            db.session.commit()
            flash("Member unassigned from workout.", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error removing member from workout: {str(e)}", 'danger')
    
    redirect_target = request.referrer or url_for('workouts.show', id=workout_id)
    return redirect(redirect_target)
