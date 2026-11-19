import uuid
import random
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import or_
from models import db, Payment, Membership, Trainer, Member

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    method_filter = request.args.get('method', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    query = Payment.query

    if search_query:
        if search_query.isdigit():
            query = query.filter(
                or_(
                    Payment.Payment_ID == int(search_query),
                    Payment.Invoice_Number.ilike(f'%{search_query}%'),
                    Payment.Transaction_ID.ilike(f'%{search_query}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    Payment.Invoice_Number.ilike(f'%{search_query}%'),
                    Payment.Transaction_ID.ilike(f'%{search_query}%')
                )
            )

    if status_filter in ['Success', 'Pending', 'Failed']:
        query = query.filter(Payment.Status == status_filter)

    if method_filter in ['Cash', 'Card', 'UPI', 'NetBanking']:
        query = query.filter(Payment.Payment_Method == method_filter)

    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Payment.Payment_Date >= d_from)
        except ValueError:
            pass

    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Payment.Payment_Date <= d_to)
        except ValueError:
            pass

    payments = query.order_by(Payment.Payment_Date.desc(), Payment.Payment_ID.desc()).all()

    return render_template(
        'payments/index.html',
        payments=payments,
        search_query=search_query,
        status_filter=status_filter,
        method_filter=method_filter,
        date_from=date_from,
        date_to=date_to
    )


@payments_bp.route('/add', methods=['GET', 'POST'])
def add():
    memberships = Membership.query.join(Member).order_by(Membership.Membership_ID.desc()).all()
    trainers = Trainer.query.order_by(Trainer.Name.asc()).all()

    preselected_membership_id = request.args.get('membership_id', type=int)
    member_id = request.args.get('member_id', type=int)
    suggested_amount = None

    if not preselected_membership_id and member_id:
        # Find latest membership for this member
        member_ms = Membership.query.filter_by(Member_ID=member_id).order_by(Membership.Membership_ID.desc()).first()
        if member_ms:
            preselected_membership_id = member_ms.Membership_ID

    if preselected_membership_id:
        target_ms = Membership.query.get(preselected_membership_id)
        if target_ms:
            suggested_amount = target_ms.balance_due if target_ms.balance_due > 0 else float(target_ms.Amount)

    if request.method == 'POST':
        membership_id_str = request.form.get('membership_id', '').strip()
        trainer_id_str = request.form.get('trainer_id', '').strip()
        amount_str = request.form.get('amount', '').strip()
        method = request.form.get('payment_method', 'Cash').strip()
        payment_date_str = request.form.get('payment_date', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        status = request.form.get('status', 'Success').strip()
        txn_id = request.form.get('transaction_id', '').strip()
        invoice_no = request.form.get('invoice_number', '').strip()

        errors = []
        if not amount_str:
            errors.append("Payment Amount is required.")
        if not payment_date_str:
            errors.append("Payment Date is required.")
        if not method:
            errors.append("Payment Method is required.")

        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Payment amount must be greater than zero.")
        except (ValueError, TypeError):
            errors.append("Invalid amount.")
            amount = 0.0

        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid payment date format.")
            payment_date = None

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid due date format.")

        membership_id = int(membership_id_str) if (membership_id_str and membership_id_str.isdigit()) else None
        trainer_id = int(trainer_id_str) if (trainer_id_str and trainer_id_str.isdigit()) else None

        # Auto-generate Invoice Number if empty
        if not invoice_no:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            invoice_no = f"INV-{datetime.now().year}-{timestamp[-6:]}{uuid.uuid4().hex[:2].upper()}"

        # Auto-generate Transaction ID / Offline Receipt ID if empty
        if not txn_id:
            if method == 'Cash':
                txn_id = f"CASH-REC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            else:
                txn_id = f"TXN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Check duplicate invoice
        if Payment.query.filter_by(Invoice_Number=invoice_no).first():
            errors.append(f"Invoice number '{invoice_no}' already exists.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'payments/add.html',
                memberships=memberships,
                trainers=trainers,
                form_data=request.form,
                preselected_membership_id=preselected_membership_id,
                suggested_amount=suggested_amount
            )

        try:
            new_payment = Payment(
                Membership_ID=membership_id,
                Trainer_ID=trainer_id,
                Amount=amount,
                Payment_Method=method,
                Payment_Date=payment_date,
                Due_Date=due_date,
                Status=status,
                Transaction_ID=txn_id if txn_id else None,
                Invoice_Number=invoice_no
            )
            db.session.add(new_payment)
            db.session.commit()
            flash(f"Offline payment recorded successfully! Invoice: {new_payment.Invoice_Number}", 'success')
            return redirect(url_for('payments.invoice', id=new_payment.Payment_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error recording payment: {str(e)}", 'danger')
            return render_template(
                'payments/add.html',
                memberships=memberships,
                trainers=trainers,
                form_data=request.form,
                preselected_membership_id=preselected_membership_id,
                suggested_amount=suggested_amount
            )

    default_date = date.today().strftime('%Y-%m-%d')
    suggested_inv = f"INV-{date.today().year}-{datetime.now().strftime('%H%M%S')}{uuid.uuid4().hex[:2].upper()}"
    return render_template(
        'payments/add.html',
        memberships=memberships,
        trainers=trainers,
        default_date=default_date,
        suggested_inv=suggested_inv,
        preselected_membership_id=preselected_membership_id,
        suggested_amount=suggested_amount
    )


@payments_bp.route('/<int:id>')
def show(id):
    payment = Payment.query.get_or_404(id)
    return render_template('payments/show.html', payment=payment)


@payments_bp.route('/<int:id>/invoice')
def invoice(id):
    payment = Payment.query.get_or_404(id)
    return render_template('payments/invoice.html', payment=payment)


@payments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    payment = Payment.query.get_or_404(id)
    memberships = Membership.query.join(Member).order_by(Membership.Membership_ID.desc()).all()
    trainers = Trainer.query.order_by(Trainer.Name.asc()).all()

    if request.method == 'POST':
        membership_id_str = request.form.get('membership_id', '').strip()
        trainer_id_str = request.form.get('trainer_id', '').strip()
        amount_str = request.form.get('amount', '').strip()
        method = request.form.get('payment_method', 'UPI').strip()
        payment_date_str = request.form.get('payment_date', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        status = request.form.get('status', 'Success').strip()
        txn_id = request.form.get('transaction_id', '').strip()
        invoice_no = request.form.get('invoice_number', '').strip()

        errors = []
        if not amount_str:
            errors.append("Amount is required.")
        if not invoice_no:
            errors.append("Invoice Number is required.")

        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Amount must be positive.")
        except (ValueError, TypeError):
            errors.append("Invalid amount.")

        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid payment date format.")
            payment_date = None

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid due date format.")

        existing = Payment.query.filter(Payment.Invoice_Number == invoice_no, Payment.Payment_ID != id).first()
        if existing:
            errors.append(f"Another payment uses invoice number '{invoice_no}'.")

        membership_id = int(membership_id_str) if (membership_id_str and membership_id_str.isdigit()) else None
        trainer_id = int(trainer_id_str) if (trainer_id_str and trainer_id_str.isdigit()) else None

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('payments/edit.html', payment=payment, memberships=memberships, trainers=trainers)

        try:
            payment.Membership_ID = membership_id
            payment.Trainer_ID = trainer_id
            payment.Amount = amount
            payment.Payment_Method = method
            payment.Payment_Date = payment_date
            payment.Due_Date = due_date
            payment.Status = status
            payment.Transaction_ID = txn_id if txn_id else None
            payment.Invoice_Number = invoice_no

            db.session.commit()
            flash("Payment updated successfully!", 'success')
            return redirect(url_for('payments.show', id=payment.Payment_ID))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating payment: {str(e)}", 'danger')

    return render_template('payments/edit.html', payment=payment, memberships=memberships, trainers=trainers)


@payments_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    payment = Payment.query.get_or_404(id)
    try:
        inv = payment.Invoice_Number
        db.session.delete(payment)
        db.session.commit()
        flash(f"Payment '{inv}' deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting payment: {str(e)}", 'danger')
    return redirect(url_for('payments.index'))


@payments_bp.route('/pay-online', methods=['GET', 'POST'])
def pay_online():
    """
    Online payment gateway has been removed in favor of manual offline payments.
    Redirects to manual offline payment entry.
    """
    membership_id = request.args.get('membership_id')
    flash("Online payment gateway has been disabled. Please record manual offline payment.", "info")
    if membership_id:
        return redirect(url_for('payments.add', membership_id=membership_id))
    return redirect(url_for('payments.add'))


@payments_bp.route('/api/membership/<int:id>')
def api_membership(id):
    ms = Membership.query.get_or_404(id)
    return jsonify({
        'membership_id': ms.Membership_ID,
        'member_id': ms.member.Member_ID,
        'member_name': ms.member.Name,
        'member_phone': ms.member.Phone,
        'member_email': ms.member.Email,
        'plan_name': ms.Plan_Name,
        'start_date': ms.Start_Date.strftime('%Y-%m-%d'),
        'end_date': ms.End_Date.strftime('%Y-%m-%d'),
        'amount': float(ms.Amount),
        'total_paid': ms.total_paid,
        'balance_due': ms.balance_due,
        'is_fully_paid': ms.is_fully_paid,
        'status': ms.Status
    })
