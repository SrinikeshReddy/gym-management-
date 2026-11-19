from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Trainer, TrainerCertification, Workout, Payment

trainers_bp = Blueprint('trainers', __name__)

@trainers_bp.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    query = Trainer.query

    if search_query:
        if search_query.isdigit():
            query = query.filter(
                or_(
                    Trainer.Trainer_ID == int(search_query),
                    Trainer.Name.ilike(f'%{search_query}%'),
                    Trainer.Specialization.ilike(f'%{search_query}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    Trainer.Name.ilike(f'%{search_query}%'),
                    Trainer.Specialization.ilike(f'%{search_query}%'),
                    Trainer.Email.ilike(f'%{search_query}%')
                )
            )

    trainers = query.order_by(Trainer.Trainer_ID.asc()).all()
    return render_template('trainers/index.html', trainers=trainers, search_query=search_query)


@trainers_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        specialization = request.form.get('specialization', '').strip()
        exp_str = request.form.get('experience_years', '0').strip()
        salary_str = request.form.get('salary', '0').strip()

        # Certifications list
        certifications = request.form.getlist('certifications[]')
        single_cert = request.form.get('certification', '').strip()
        if single_cert and single_cert not in certifications:
            certifications.append(single_cert)

        errors = []
        if not name:
            errors.append("Trainer Name is required.")
        if not phone:
            errors.append("Phone is required.")
        if not email or '@' not in email:
            errors.append("Valid Email is required.")
        if not specialization:
            errors.append("Specialization is required.")

        # Check duplicate email
        if email and Trainer.query.filter_by(Email=email).first():
            errors.append(f"Trainer with email '{email}' already exists.")

        try:
            exp = int(exp_str)
            if exp < 0:
                errors.append("Experience years cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Experience years must be a valid integer.")
            exp = 0

        try:
            salary = float(salary_str)
            if salary < 0:
                errors.append("Salary cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Salary must be a valid number.")
            salary = 0.0

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('trainers/add.html', form_data=request.form)

        try:
            new_trainer = Trainer(
                Name=name,
                Phone=phone,
                Email=email,
                Specialization=specialization,
                Experience_Years=exp,
                Salary=salary
            )
            db.session.add(new_trainer)
            db.session.flush()

            # Add certifications
            for cert in certifications:
                clean_cert = cert.strip()
                if clean_cert:
                    db.session.add(TrainerCertification(Trainer_ID=new_trainer.Trainer_ID, Certification=clean_cert))

            db.session.commit()
            flash(f"Trainer '{new_trainer.Name}' added successfully!", 'success')
            return redirect(url_for('trainers.show', id=new_trainer.Trainer_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding trainer: {str(e)}", 'danger')
            return render_template('trainers/add.html', form_data=request.form)

    return render_template('trainers/add.html')


@trainers_bp.route('/<int:id>')
def show(id):
    trainer = Trainer.query.get_or_404(id)
    return render_template('trainers/show.html', trainer=trainer)


@trainers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    trainer = Trainer.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        specialization = request.form.get('specialization', '').strip()
        exp_str = request.form.get('experience_years', '0').strip()
        salary_str = request.form.get('salary', '0').strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not phone:
            errors.append("Phone is required.")
        if not email or '@' not in email:
            errors.append("Valid Email is required.")
        if not specialization:
            errors.append("Specialization is required.")

        existing = Trainer.query.filter(Trainer.Email == email, Trainer.Trainer_ID != id).first()
        if existing:
            errors.append(f"Another trainer already uses email '{email}'.")

        try:
            exp = int(exp_str)
            if exp < 0:
                errors.append("Experience years cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Experience must be an integer.")

        try:
            salary = float(salary_str)
            if salary < 0:
                errors.append("Salary cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Salary must be a valid number.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('trainers/edit.html', trainer=trainer)

        try:
            trainer.Name = name
            trainer.Phone = phone
            trainer.Email = email
            trainer.Specialization = specialization
            trainer.Experience_Years = exp
            trainer.Salary = salary

            db.session.commit()
            flash(f"Trainer '{trainer.Name}' updated successfully!", 'success')
            return redirect(url_for('trainers.show', id=trainer.Trainer_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating trainer: {str(e)}", 'danger')

    return render_template('trainers/edit.html', trainer=trainer)


@trainers_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    trainer = Trainer.query.get_or_404(id)
    try:
        name = trainer.Name
        db.session.delete(trainer)
        db.session.commit()
        flash(f"Trainer '{name}' deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting trainer: {str(e)}", 'danger')
    return redirect(url_for('trainers.index'))


@trainers_bp.route('/<int:id>/add_cert', methods=['POST'])
def add_cert(id):
    trainer = Trainer.query.get_or_404(id)
    cert_text = request.form.get('certification', '').strip()

    if not cert_text:
        flash("Certification name cannot be empty.", 'danger')
        return redirect(url_for('trainers.show', id=id))

    existing = TrainerCertification.query.filter_by(Trainer_ID=id, Certification=cert_text).first()
    if existing:
        flash("This certification is already listed for this trainer.", 'warning')
        return redirect(url_for('trainers.show', id=id))

    try:
        new_cert = TrainerCertification(Trainer_ID=id, Certification=cert_text)
        db.session.add(new_cert)
        db.session.commit()
        flash("Certification added successfully!", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding certification: {str(e)}", 'danger')

    return redirect(url_for('trainers.show', id=id))


@trainers_bp.route('/<int:id>/delete_cert', methods=['POST'])
def delete_cert(id):
    cert_text = request.form.get('certification', '').strip()
    cert = TrainerCertification.query.filter_by(Trainer_ID=id, Certification=cert_text).first()
    if cert:
        try:
            db.session.delete(cert)
            db.session.commit()
            flash("Certification removed.", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting certification: {str(e)}", 'danger')
    return redirect(url_for('trainers.show', id=id))
