from flask import request, render_template, redirect, url_for, Blueprint, flash
from vendora_app.blueprints.vendor.models import Vendor,Service
from vendora_app.blueprints.customer.models import Customer
from vendora_app.blueprints.appointment.models import Appointment
from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.app import db, bcrypt
from datetime import datetime

customer = Blueprint('customer', __name__, template_folder = 'templates')

@customer.route('/')
def index():
    return render_template('customer/index.html')

@customer.route('/homepage')
def vendors():
    search_query = request.args.get('q', '').strip()  # Get the search input
    if search_query:
        # Filter vendors whose business_name contains the search query (case-insensitive)
        vendors = Vendor.query.filter(Vendor.business_name.ilike(f"%{search_query}%")).all()
    else:
        vendors = Vendor.query.all()
    
    return render_template('customer/vendors.html', vendors=vendors)

@customer.route('/profile_setup',methods=['GET','POST'])
@login_required
def profile_setup():
    if request.method=='GET':
        return render_template('customer/profile_setup.html')
    
    # Save Customer Info
    full_name = request.form.get('full_name')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    # Check if already exists
    if current_user.customer_profile:
        flash('Profile already exist','info')
        return redirect(url_for('customer.dashboard'))
    
    new_profile = Customer(user_id=current_user.uid, full_name=full_name,address=address,phone=phone)
    db.session.add(new_profile)
    db.session.commit()

    flash('Customer profile completed successfully!', 'success')
    return redirect(url_for('customer.dashboard'))


@customer.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_customer != True:
        return "Access denied", 403
    customer_id = current_user.customer_profile.id

    appointments = Appointment.query.filter_by(
        customer_id= current_user.customer_profile.id
    ).order_by(Appointment.start_time.desc()).all()

    vendors = Vendor.query.all()  # keep your existing logic

    return render_template(
        "customer/dashboard.html",
        appointments=appointments,
        vendors=vendors
    )    
    

@customer.route('/cancel-appointment/<int:id>', methods=['POST'])
@login_required
def cancel_appointment(id):
    appt = Appointment.query.get_or_404(id)

    # security check
    if appt.customer_id != current_user.customer_profile.id:
        return "Unauthorized", 403

    appt.status = 'cancelled'
    db.session.commit()

    return redirect(url_for('customer.dashboard'))

@customer.route('/update-appointment/<int:id>', methods=['GET', 'POST'])
@login_required
def update_appointment(id):
    appt = Appointment.query.get_or_404(id)

    if appt.customer_id != current_user.customer_profile.id:
        return "Unauthorized", 403

    service = appt.service

    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')

        start_time = datetime.strptime(
            f"{date} {time}",
            "%Y-%m-%d %H:%M"
        )

        end_time = start_time + timedelta(
            minutes=service.duration_minutes
        )

        # overlap check (ignore current appointment)
        conflict = Appointment.query.filter(
            Appointment.vendor_id == appt.vendor_id,
            Appointment.id != appt.id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        ).first()

        if conflict:
            return "Time slot not available"

        appt.start_time = start_time
        appt.end_time = end_time
        appt.status = "pending"  # reset after change

        db.session.commit()

        return redirect(url_for('customer.dashboard'))

    return render_template(
        "customer/update_appointment.html",
        appt=appt
    )

@customer.route('/vendor/<int:vendor_id>')

def vendor_details(vendor_id):
    v = Vendor.query.get_or_404(vendor_id)

    services = Service.query.filter_by(
        vendor_id=vendor_id
    ).all()

    return render_template(
        "customer/vendor_detail.html",
        vendor=v,
        services=services
    )

@customer.route('/rate/<int:appointment_id>', methods=['POST'])
@login_required
def rate_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # ✅ Security checks
    if appointment.customer_id != current_user.customer_profile.id:
        flash("Unauthorized action", "danger")
        return redirect(url_for('customer.dashboard'))
    """
    if appointment.status != "completed":
        flash("You can only review completed appointments", "warning")
        return redirect(url_for('customer.dashboard'))
    """
    if appointment.rating is not None:
        flash("You have already reviewed this appointment", "info")
        return redirect(url_for('customer.dashboard'))

    # ✅ Get data
    rating = int(request.form.get('rating'))
    review = request.form.get('review')

    # ✅ Save
    appointment.rating = rating
    appointment.review = review

    db.session.commit()

    flash(" Thank you for your feedback!", "success")
    return redirect(url_for('customer.dashboard'))