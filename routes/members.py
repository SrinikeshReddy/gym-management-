from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Member, MemberAddress, Membership, Attendance, Workout, ParticipatesIn

members_bp = Blueprint('members', __name__)

@members_bp.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Member.query

    # Apply database search filter on ID, Name, Phone, Email
    if search_query:
        if search_query.isdigit():
            query = query.filter(
                or_(
                    Member.Member_ID == int(search_query),
                    Member.Name.ilike(f'%{search_query}%'),
                    Member.Phone.ilike(f'%{search_query}%'),
                    Member.Email.ilike(f'%{search_query}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    Member.Name.ilike(f'%{search_query}%'),
                    Member.Phone.ilike(f'%{search_query}%'),
                    Member.Email.ilike(f'%{search_query}%')
                )
            )

    if status_filter in ['Active', 'Inactive']:
        query = query.filter(Member.Status == status_filter)

    members = query.order_by(Member.Member_ID.asc()).all()
    return render_template('members/index.html', members=members, search_query=search_query, status_filter=status_filter)


@members_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        dob_str = request.form.get('date_of_birth', '').strip()
        age_str = request.form.get('age', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        join_date_str = request.form.get('join_date', '').strip()
        status = request.form.get('status', 'Active').strip()
        blood_group = request.form.get('blood_group', '').strip()
        
        # Addresses list (supports multiple addresses submitted from dynamic inputs)
        addresses = request.form.getlist('addresses[]')
        single_address = request.form.get('address', '').strip()
        if single_address and single_address not in addresses:
            addresses.append(single_address)

        # Validation
        errors = []
        if not name:
            errors.append("Name is required.")
        if not phone or len(phone) < 7:
            errors.append("A valid phone number is required.")
        if not email or '@' not in email:
            errors.append("A valid email address is required.")
        if not dob_str:
            errors.append("Date of Birth is required.")
        if not join_date_str:
            errors.append("Join Date is required.")
        if not emergency_contact:
            errors.append("Emergency Contact number is required.")
        if not blood_group:
            errors.append("Blood Group is required.")

        # Check duplicate email
        if email and Member.query.filter_by(Email=email).first():
            errors.append(f"Member with email '{email}' already exists.")

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD.")
            dob, join_date = None, None

        try:
            age = int(age_str)
            if age <= 0:
                errors.append("Age must be a positive integer.")
        except (ValueError, TypeError):
            # Calculate from DOB if age not provided
            if dob:
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                errors.append("Valid Age is required.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('members/add.html', form_data=request.form)

        # Create new Member
        try:
            new_member = Member(
                Name=name,
                Gender=gender,
                Date_of_Birth=dob,
                Age=age,
                Phone=phone,
                Email=email,
                Emergency_Contact=emergency_contact,
                Join_Date=join_date,
                Status=status,
                Blood_Group=blood_group
            )
            db.session.add(new_member)
            db.session.flush()  # Generate Member_ID

            # Add member addresses
            for addr in addresses:
                clean_addr = addr.strip()
                if clean_addr:
                    db.session.add(MemberAddress(Member_ID=new_member.Member_ID, Address=clean_addr))

            db.session.commit()
            flash(f"Member '{new_member.Name}' (ID: {new_member.Member_ID}) added successfully!", 'success')
            return redirect(url_for('members.show', id=new_member.Member_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Database error while adding member: {str(e)}", 'danger')
            return render_template('members/add.html', form_data=request.form)

    # GET request
    default_join_date = date.today().strftime('%Y-%m-%d')
    return render_template('members/add.html', default_join_date=default_join_date)


@members_bp.route('/<int:id>')
def show(id):
    member = Member.query.get_or_404(id)
    all_workouts = Workout.query.order_by(Workout.Workout_Name.asc()).all()
    
    # Get enrolled workout IDs for this member
    enrolled_workout_ids = [p.Workout_ID for p in member.participations]
    
    return render_template(
        'members/show.html',
        member=member,
        all_workouts=all_workouts,
        enrolled_workout_ids=enrolled_workout_ids
    )


@members_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    member = Member.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        dob_str = request.form.get('date_of_birth', '').strip()
        age_str = request.form.get('age', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        join_date_str = request.form.get('join_date', '').strip()
        status = request.form.get('status', 'Active').strip()
        blood_group = request.form.get('blood_group', '').strip()

        errors = []
        if not name:
            errors.append("Name is required.")
        if not phone:
            errors.append("Phone is required.")
        if not email or '@' not in email:
            errors.append("Valid Email is required.")
        if not emergency_contact:
            errors.append("Emergency contact is required.")
        
        # Check duplicate email on other members
        existing = Member.query.filter(Member.Email == email, Member.Member_ID != id).first()
        if existing:
            errors.append(f"Another member already uses email '{email}'.")

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid date format.")
            dob, join_date = None, None

        try:
            age = int(age_str)
            if age <= 0:
                errors.append("Age must be a positive integer.")
        except (ValueError, TypeError):
            if dob:
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                errors.append("Valid Age is required.")
                age = member.Age

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('members/edit.html', member=member)

        try:
            member.Name = name
            member.Gender = gender
            member.Date_of_Birth = dob
            member.Age = age
            member.Phone = phone
            member.Email = email
            member.Emergency_Contact = emergency_contact
            member.Join_Date = join_date
            member.Status = status
            member.Blood_Group = blood_group

            db.session.commit()
            flash(f"Member details for '{member.Name}' updated successfully!", 'success')
            return redirect(url_for('members.show', id=member.Member_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating member: {str(e)}", 'danger')

    return render_template('members/edit.html', member=member)


@members_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    member = Member.query.get_or_404(id)
    try:
        member_name = member.Name
        db.session.delete(member)
        db.session.commit()
        flash(f"Member '{member_name}' (ID: {id}) and all associated records deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete member: {str(e)}", 'danger')
    return redirect(url_for('members.index'))


@members_bp.route('/<int:id>/add_address', methods=['POST'])
def add_address(id):
    member = Member.query.get_or_404(id)
    address_text = request.form.get('address', '').strip()

    if not address_text:
        flash("Address cannot be empty.", 'danger')
        return redirect(url_for('members.show', id=id))

    # Check if address already exists for this member
    existing = MemberAddress.query.filter_by(Member_ID=id, Address=address_text).first()
    if existing:
        flash("This address is already registered for this member.", 'warning')
        return redirect(url_for('members.show', id=id))

    try:
        new_addr = MemberAddress(Member_ID=id, Address=address_text)
        db.session.add(new_addr)
        db.session.commit()
        flash("Address added successfully!", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding address: {str(e)}", 'danger')

    return redirect(url_for('members.show', id=id))


@members_bp.route('/<int:id>/delete_address', methods=['POST'])
def delete_address(id):
    address_text = request.form.get('address', '').strip()
    addr = MemberAddress.query.filter_by(Member_ID=id, Address=address_text).first()
    if addr:
        try:
            db.session.delete(addr)
            db.session.commit()
            flash("Address removed.", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting address: {str(e)}", 'danger')
    return redirect(url_for('members.show', id=id))
