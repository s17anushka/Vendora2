from flask import request, render_template, redirect, url_for, Blueprint,flash
from vendora_app.app import db
from datetime import datetime, timedelta, date
from flask_login import current_user, login_required
from vendora_app.blueprints.vendor.models import Service
from vendora_app.blueprints.appointment.models import Appointment

appointment = Blueprint('appointment', __name__, template_folder='templates')


# ✅ SLOT GENERATION FUNCTION
def generate_slots(selected_date):
    slots = []

    start = datetime.strptime(f"{selected_date} 10:00", "%Y-%m-%d %H:%M")
    end = datetime.strptime(f"{selected_date} 19:00", "%Y-%m-%d %H:%M")

    while start < end:
        slots.append(start)
        start += timedelta(minutes=30)

    return slots


@appointment.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_id):
    if current_user.is_customer != True:
        return "Access denied", 403
        flash('login as Customer','danger')
    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        if not date_str or not time_str:
            flash('Please Choose Date and Time.','info')
        # ✅ Create start_time
        start_time = datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )

        # ✅ Calculate end_time
        end_time = start_time + timedelta(
            minutes=service.duration_minutes
        )

        # 🚨 Overlap Check
        conflict = Appointment.query.filter(
            Appointment.vendor_id == service.vendor_id,
            Appointment.status != 'cancelled',
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        ).first()

        if conflict:
            flash('❌ This time slot is already booked. Please choose another.','danger')
            return redirect(url_for('appointment.book_service', service_id = service_id))


        # ✅ Save Appointment
        new_appointment = Appointment(
            customer_id=current_user.customer_profile.id,
            vendor_id=service.vendor_id,
            service_id=service.id,
            start_time=start_time,
            end_time=end_time,
            service_type = service.service_type,
            service_cost=service.service_cost,
            status="pending"
        )

        db.session.add(new_appointment)
        db.session.commit()
        flash('Your Slot is Booked','Success')
        return redirect(
            url_for('customer.vendor_details', vendor_id=service.vendor_id)
        )

    # ✅ GET request → generate slots
    selected_date = date.today().strftime("%Y-%m-%d")
    slots = generate_slots(selected_date)
    
    return render_template(
        "appointment/book.html",
        service=service,
        slots=slots   # ❗ VERY IMPORTANT
    )