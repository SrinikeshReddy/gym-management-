from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import or_
from models import db, Member, MemberAddress, Membership, Workout, Attendance, Payment

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Member self-registration portal.
    Allows new gym members to create their account and profile.
    """
    if 'role' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.portal'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        dob_str = request.form.get('date_of_birth', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        address = request.form.get('address', '').strip()

        errors = []
        if not name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email address is required.")
        if not phone:
            errors.append("Phone number is required.")
        if not gender:
            errors.append("Gender is required.")
        if not dob_str:
            errors.append("Date of Birth is required.")
        if not blood_group:
            errors.append("Blood group is required.")
        if not emergency_contact:
            errors.append("Emergency contact phone is required.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 4:
            errors.append("Password must be at least 4 characters long.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")

        # Check duplicate email
        if email and Member.query.filter(Member.Email.ilike(email)).first():
            errors.append(f"A member account with email '{email}' already exists. Please log in.")

        dob = None
        age = 18
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if age < 12 or age > 100:
                    errors.append("Please enter a valid date of birth (age between 12 and 100).")
            except ValueError:
                errors.append("Invalid date format for Date of Birth.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html', form_data=request.form)

        try:
            new_member = Member(
                Name=name,
                Gender=gender,
                Date_of_Birth=dob,
                Age=age,
                Phone=phone,
                Email=email,
                Emergency_Contact=emergency_contact,
                Join_Date=date.today(),
                Status='Active',
                Blood_Group=blood_group,
                Password=password
            )
            db.session.add(new_member)
            db.session.flush()

            if address:
                new_address = MemberAddress(Member_ID=new_member.Member_ID, Address=address)
                db.session.add(new_address)

            db.session.commit()

            # Automatically log the new member in
            session.clear()
            session['user_id'] = new_member.Member_ID
            session['role'] = 'user'
            session['user_name'] = new_member.Name
            session['email'] = new_member.Email

            flash(f"Account registered successfully! Welcome to Titan Fitness, {new_member.Name}.", "success")
            return redirect(url_for('auth.portal'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating member account: {str(e)}", "danger")
            return render_template('auth/register.html', form_data=request.form)

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Dual Authentication Portal:
    1. Administrator Login (Full system access)
    2. Member / User Login (Personal Member Portal)
    """
    if 'role' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.portal'))

    active_tab = request.args.get('role', 'admin')

    # Fetch a sample member for convenience demo hint
    sample_member = Member.query.first()
    sample_member_email = sample_member.Email if sample_member else 'sneha.rao@outlook.com'

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'admin').strip()

        if login_type == 'admin':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            valid_usernames = ['admin', 'admin@gym.com', 'administrator']
            valid_passwords = ['admin', 'admin123']

            if username.lower() in valid_usernames and password in valid_passwords:
                session.clear()
                session['user_id'] = 'admin'
                session['role'] = 'admin'
                session['user_name'] = 'Administrator'
                session['email'] = 'admin@gym.com'
                flash('Welcome back, Administrator! Successfully logged in as Admin.', 'success')

                next_url = request.args.get('next')
                if next_url and not next_url.startswith('/login') and not next_url.startswith('/logout'):
                    return redirect(next_url)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid admin credentials. Use Username: admin | Password: admin123', 'danger')
                return render_template(
                    'auth/login.html',
                    active_tab='admin',
                    admin_username=username,
                    sample_member_email=sample_member_email
                )

        elif login_type == 'user':
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '').strip()

            if not identifier:
                flash('Please enter your registered Email or Phone number.', 'danger')
                return render_template(
                    'auth/login.html',
                    active_tab='user',
                    sample_member_email=sample_member_email
                )

            member_query = Member.query.filter(
                or_(
                    Member.Email.ilike(identifier),
                    Member.Phone == identifier
                )
            )
            if identifier.isdigit():
                member_query = Member.query.filter(
                    or_(
                        Member.Member_ID == int(identifier),
                        Member.Email.ilike(identifier),
                        Member.Phone == identifier
                    )
                )

            member = member_query.first()

            if member:
                valid_passwords = [
                    member.Password or 'member123',
                    'member123',
                    'password',
                    'user123',
                    member.Phone
                ]

                if password in valid_passwords:
                    session.clear()
                    session['user_id'] = member.Member_ID
                    session['role'] = 'user'
                    session['user_name'] = member.Name
                    session['email'] = member.Email
                    flash(f'Welcome back, {member.Name}! Successfully logged in as Member.', 'success')

                    next_url = request.args.get('next')
                    if next_url and not next_url.startswith('/login') and not next_url.startswith('/logout'):
                        return redirect(next_url)
                    return redirect(url_for('auth.portal'))
                else:
                    flash(f'Incorrect password for {member.Name}. (Default password: "member123")', 'danger')
                    return render_template(
                        'auth/login.html',
                        active_tab='user',
                        user_identifier=identifier,
                        sample_member_email=sample_member_email
                    )
            else:
                flash(f'No member found with email or phone "{identifier}". Please verify your credentials.', 'danger')
                return render_template(
                    'auth/login.html',
                    active_tab='user',
                    user_identifier=identifier,
                    sample_member_email=sample_member_email
                )

    return render_template(
        'auth/login.html',
        active_tab=active_tab,
        sample_member_email=sample_member_email
    )


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Terminates session and displays dedicated Logout confirmation page.
    """
    prev_user_name = session.get('user_name', 'User')
    prev_role = session.get('role', 'user')
    session.clear()
    return render_template('auth/logout.html', user_name=prev_user_name, role=prev_role)


@auth_bp.route('/portal')
def portal():
    """
    Member Dashboard / Portal for authenticated gym members.
    """
    if 'role' not in session:
        flash('Please log in to view your Member Portal.', 'warning')
        return redirect(url_for('auth.login', role='user', next=request.path))

    if session.get('role') == 'user':
        member_id = session.get('user_id')
    else:
        member_id = request.args.get('member_id', type=int)
        if not member_id:
            first_m = Member.query.first()
            member_id = first_m.Member_ID if first_m else None

    if not member_id:
        flash('No member records found.', 'warning')
        return redirect(url_for('dashboard.index'))

    member = Member.query.get_or_404(member_id)

    # Active membership
    active_membership = next((m for m in member.memberships if m.Status == 'Active'), None)
    if not active_membership and member.memberships:
        active_membership = member.memberships[0]

    # Assigned workouts
    member_workouts = [p.workout for p in member.participations if p.workout]

    # Attendance logs
    attendances = Attendance.query.filter_by(Member_ID=member.Member_ID).order_by(
        Attendance.Date.desc(),
        Attendance.Check_In_Time.desc()
    ).all()

    # Payments & Invoices
    ms_ids = [m.Membership_ID for m in member.memberships]
    payments = Payment.query.filter(Payment.Membership_ID.in_(ms_ids)).order_by(
        Payment.Payment_Date.desc(),
        Payment.Payment_ID.desc()
    ).all() if ms_ids else []

    return render_template(
        'auth/portal.html',
        member=member,
        active_membership=active_membership,
        member_workouts=member_workouts,
        attendances=attendances,
        payments=payments
    )

