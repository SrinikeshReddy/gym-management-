from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Membership, Member, Payment

memberships_bp = Blueprint('memberships', __name__)

@memberships_bp.route('/')
def index():
    plan_filter = request.args.get('plan', '').strip()
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()

    query = db.session.query(Membership).join(Member)

    if search_query:
        query = query.filter(
            or_(
                Member.Name.ilike(f'%{search_query}%'),
                Member.Phone.ilike(f'%{search_query}%')
            )
        )

    if plan_filter in ['Monthly', 'Quarterly', 'Half-Yearly', 'Yearly']:
        query = query.filter(Membership.Plan_Name == plan_filter)

    if status_filter in ['Active', 'Expired']:
        query = query.filter(Membership.Status == status_filter)

    memberships = query.order_by(Membership.Membership_ID.desc()).all()

    return render_template(
        'memberships/index.html',
        memberships=memberships,
        plan_filter=plan_filter,
        status_filter=status_filter,
        search_query=search_query
    )


@memberships_bp.route('/add', methods=['GET', 'POST'])
def add():
    members = Member.query.order_by(Member.Name.asc()).all()

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        plan_name = request.form.get('plan_name', '').strip()
        plan_desc = request.form.get('plan_description', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        amount_str = request.form.get('amount', '0').strip()
        status = request.form.get('status', 'Active').strip()

        errors = []
        if not member_id_str:
            errors.append("Member selection is required.")
        if not plan_name:
            errors.append("Plan Name is required.")
        if not start_date_str:
            errors.append("Start Date is required.")
        if not end_date_str:
            errors.append("End Date is required.")

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date < start_date:
                errors.append("End Date cannot be earlier than Start Date.")
            # Automatically calculate Duration_Days
            duration_days = (end_date - start_date).days
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD.")
            start_date, end_date = None, None
            duration_days = 0

        try:
            amount = float(amount_str)
            if amount < 0:
                errors.append("Amount cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Amount must be a valid number.")
            amount = 0.0

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('memberships/add.html', members=members, form_data=request.form)

        try:
            new_membership = Membership(
                Member_ID=int(member_id_str),
                Plan_Name=plan_name,
                Plan_Description=plan_desc,
                Start_Date=start_date,
                End_Date=end_date,
                Amount=amount,
                Status=status,
                Duration_Days=duration_days
            )
            db.session.add(new_membership)
            db.session.commit()
            flash(f"Membership plan '{new_membership.Plan_Name}' created successfully!", 'success')
            return redirect(url_for('memberships.show', id=new_membership.Membership_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating membership: {str(e)}", 'danger')
            return render_template('memberships/add.html', members=members, form_data=request.form)

    return render_template('memberships/add.html', members=members)


@memberships_bp.route('/<int:id>')
def show(id):
    membership = Membership.query.get_or_404(id)
    return render_template('memberships/show.html', membership=membership)


@memberships_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    membership = Membership.query.get_or_404(id)
    members = Member.query.order_by(Member.Name.asc()).all()

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        plan_name = request.form.get('plan_name', '').strip()
        plan_desc = request.form.get('plan_description', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        amount_str = request.form.get('amount', '0').strip()
        status = request.form.get('status', 'Active').strip()

        errors = []
        if not member_id_str:
            errors.append("Member selection is required.")
        if not plan_name:
            errors.append("Plan Name is required.")

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date < start_date:
                errors.append("End Date cannot be earlier than Start Date.")
            duration_days = (end_date - start_date).days
        except ValueError:
            errors.append("Invalid date format.")
            start_date, end_date = None, None
            duration_days = 0

        try:
            amount = float(amount_str)
            if amount < 0:
                errors.append("Amount cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Amount must be a valid number.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('memberships/edit.html', membership=membership, members=members)

        try:
            membership.Member_ID = int(member_id_str)
            membership.Plan_Name = plan_name
            membership.Plan_Description = plan_desc
            membership.Start_Date = start_date
            membership.End_Date = end_date
            membership.Amount = amount
            membership.Status = status
            membership.Duration_Days = duration_days

            db.session.commit()
            flash("Membership updated successfully!", 'success')
            return redirect(url_for('memberships.show', id=membership.Membership_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating membership: {str(e)}", 'danger')

    return render_template('memberships/edit.html', membership=membership, members=members)


@memberships_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    membership = Membership.query.get_or_404(id)
    try:
        db.session.delete(membership)
        db.session.commit()
        flash(f"Membership ID {id} deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting membership: {str(e)}", 'danger')
    return redirect(url_for('memberships.index'))
