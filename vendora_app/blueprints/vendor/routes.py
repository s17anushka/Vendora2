from flask import request, render_template, redirect, url_for, Blueprint, flash
from vendora_app.blueprints.vendor.models import Vendor, Service
from vendora_app.blueprints.appointment.models import Appointment
from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.app import db
from cloudinary.uploader import upload
vendor = Blueprint('vendor', __name__, template_folder = 'templates')

SERVICE_TYPES = {
    1: "Haircuts & Styling",
    2: "Facial & Clean-ups",
    3: "Hair Spa & Deep Conditioning",
    4: "Hair Coloring",
    5: "Manicures & Pedicures",
    6: "Head & Body Massage",
    7: "Bleach & De-Tan",
    8: "Waxing / Threading"
}


@vendor.route('/')
def index():
    return render_template('vendor/index.html')

@vendor.route('/profile_setup', methods = ['GET','POST'])
@login_required
def profile_setup():
    if request.method == 'GET':
        return render_template('vendor/profile_setup.html')
    
    name = request.form.get('name')
    email = request.form.get('email')
    
    business_name = request.form.get('business_name')
    business_address = request.form.get('business_address')
    
    phone_number = request.form.get('phone_number')
    whatsapp_number = request.form.get('whatsapp_number')
    
    open_duration = request.form.get('open_duration')
    payment_type = request.form.get('payment_type')
    
    year_of_establishment = request.form.get('year_of_establishment')
    
    
    # uploading business image
    files = request.files.getlist("image")
    uploaded_urls = []
    index_start = len(current_user.business_imgs)+1
    print(current_user.uid)
    for i, file in enumerate(files, start=index_start):
        result = upload(
            file,
            folder=f"vendora/{current_user.uid}/business_img/",
            public_id=f"img_{str(i)}",
            overwrite=True
        )
        url = result["secure_url"]
        current_user.business_imgs.append(url)
        uploaded_urls.append(url)
    
    db.session.commit()
    
    if current_user.vendor_profile:
        flash('Profile already exists','info')
        return redirect(url_for('vendor.dashboard'))
    
    new_profile = Vendor(
        user_id = current_user.uid,
        name = name,
        email = email,
        business_name = business_name,
        business_address = business_address,
        phone_number = phone_number,
        whatsapp_number = whatsapp_number,
        open_duration = open_duration,
        payment_type = payment_type,
        year_of_establishment = year_of_establishment,
        rating = 0,
        rater_no = 0
    )
    
    db.session.add(new_profile)
    db.session.commit()
    
    flash('Vendor Profile completed successfully!', 'Success')
    return redirect(url_for('vendor.dashboard'))

@vendor.route('/profile_update', methods=['GET', 'POST'])
@login_required
def profile_update():
    vendor_profile = current_user.vendor_profile

    if not vendor_profile:
        flash("You don't have a vendor profile yet. Complete setup first.", "warning")
        return redirect(url_for('vendor.profile_setup'))

    # ==========================
    # GET → show update form
    # ==========================
    if request.method == 'GET':
        return render_template(
            'vendor/profile_update.html',
            profile=vendor_profile
        )

    # ==========================
    # POST → update values
    # ==========================
    vendor_profile.name = request.form.get('name', vendor_profile.name)
    vendor_profile.email = request.form.get('email', vendor_profile.email)
    vendor_profile.business_name = request.form.get('business_name', vendor_profile.business_name)
    vendor_profile.business_address = request.form.get('business_address', vendor_profile.business_address)
    vendor_profile.phone_number = request.form.get('phone_number', vendor_profile.phone_number)
    vendor_profile.whatsapp_number = request.form.get('whatsapp_number', vendor_profile.whatsapp_number)
    vendor_profile.open_duration = request.form.get('open_duration', vendor_profile.open_duration)
    vendor_profile.payment_type = request.form.get('payment_type', vendor_profile.payment_type)
    vendor_profile.year_of_establishment = request.form.get('year_of_establishment', vendor_profile.year_of_establishment)
     
    # uploading business image
    files = request.files.getlist("image")
    uploaded_urls = []
    index_start = len(current_user.business_imgs)+1
    print(current_user.uid)
    for i, file in enumerate(files, start=index_start):
        result = upload(
            file,
            folder=f"vendora/{current_user.uid}/business_img/",
            public_id=f"img_{str(i)}",
            overwrite=True
        )
        url = result["secure_url"]
        current_user.business_imgs.append(url)
        uploaded_urls.append(url)
    db.session.commit()

    flash('Vendor Profile updated successfully!', 'success')
    return redirect(url_for('vendor.dashboard'))


@vendor.route('/services', methods=['GET', 'POST'])
def services():   
      
    if request.method == 'POST':
        # Get form data
        service_name = request.form.get('service_name')
        service_type = request.form.get('service_type')
        duration_minutes = request.form.get('duration_minutes')
        service_cost = request.form.get('service_cost')
        vendor_id = current_user.vendor_profile.id

        # Convert numeric fields safely
        duration_minutes = int(duration_minutes) if duration_minutes else None
        service_cost = int(service_cost) if service_cost else None
        
        if not vendor_id:
            return "Vendor not logged in", 400

        # Create new Service object
        new_service = Service(
            vendor_id=vendor_id,
            service_name=service_name,
            service_type=service_type,
            duration_minutes=duration_minutes,
            service_cost=service_cost
        )

        # Save to database
        db.session.add(new_service)
        db.session.commit()

        # Optional: redirect after success (important to prevent resubmission)
        return redirect(url_for('vendor.services'))

    # GET request
    services_data = Service.query.filter_by(vendor_id=current_user.vendor_profile.id).all()
    return render_template('vendor/services.html',vendor=vendor, services = services_data,service_types=SERVICE_TYPES )
 
@vendor.route('/add-service', methods=['POST'])
def add_service():
    vendor_id = current_user.vendor_profile.id

    new_service = Service(
        vendor_id=vendor_id,
        service_name=request.form.get('service_name'),
        service_type=int(request.form.get('service_type')),
        duration_minutes=int(request.form.get('duration_minutes')) if request.form.get('duration_minutes') else None,
        service_cost=int(request.form.get('service_cost')) if request.form.get('service_cost') else None
    )

    db.session.add(new_service)
    db.session.commit()

    return redirect(url_for('vendor.services'))
 
@vendor.route('/edit-service/<int:id>', methods=['POST'])
def edit_service(id):
    service = Service.query.get_or_404(id)

    service.service_name = request.form.get('service_name')
    service_type = int(request.form.get('service_type'))
    service.duration_minutes = int(request.form.get('duration_minutes')) if request.form.get('duration_minutes') else None
    service.service_cost = int(request.form.get('service_cost')) if request.form.get('service_cost') else None

    db.session.commit()

    return redirect(url_for('vendor.services'))
 
@vendor.route('/delete-service/<int:id>', methods=['POST'])
def delete_service(id):
    service = Service.query.get_or_404(id)

    db.session.delete(service)
    db.session.commit()

    return redirect(url_for('vendor.services'))  
    

@vendor.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_vendor != True:
        return "Access denied", 403
    
    """if current_user.last_role == 'customer':
        return "Access denied", 403"""
    
    vendor = current_user.vendor_profile
    return render_template('vendor/dashboard.html',vendor=vendor)

    """
    Can Access the information using
    <h2>{{ vendor.shop_name }}</h2>
    <p>Business type: {{ vendor.business_type }}</p>
    """

@vendor.route('/delete_profile')
@login_required
def delete_vendor_profile():
    vendor_profile = current_user.vendor_profile
    logout_user()
    db.session.delete(vendor_profile)
    current_user.is_vendor = 0
    db.session.commit()
    flash('Vendor Profile have me Deleted','Success')
    return redirect(url_for('auth.login'))

"""
@vendor.route('/dashboard1')
def dashboard():
    return render_template('vendor/dashboard.html')
"""
  
@vendor.route('/edit_business')
def edit_business():
    return render_template('vendor/dashboard.html')

@vendor.route('/appointments')
@login_required

def appointments():
    if current_user.is_vendor != True:
        return "Access denied", 403
        flash('login as Customer','danger')
    vendor_id = current_user.vendor_profile.id

    appointments = Appointment.query.filter_by(
        vendor_id=vendor_id
    ).order_by(Appointment.start_time).all()

    return render_template(
        'vendor/appointments.html',
        appointments=appointments
    )
    
@vendor.route('/confirm-appointment/<int:id>', methods=['POST'])
@login_required
def confirm_appointment(id):
    appt = Appointment.query.get_or_404(id)

    appt.status = 'confirmed'
    db.session.commit()

    return redirect(url_for('vendor.appointments'))

@vendor.route('/cancel-appointment/<int:id>', methods=['POST'])
@login_required
def cancel_appointment(id):
    appt = Appointment.query.get_or_404(id)

    appt.status = 'cancelled'
    db.session.commit()

    return redirect(url_for('vendor.appointments'))

@vendor.route('/analytics')
def analytics():
    return render_template('vendor/analytics.html')

@vendor.route('/reviews')
def reviews():
    return render_template('vendor/reviews.html')

@vendor.route('/support')
def support():
    return render_template('vendor/support.html')

@vendor.route('/complete_appointment/<int:id>', methods=['POST'])
@login_required
def complete_appointment(id):
    appointment = Appointment.query.get_or_404(id)

    # Optional: ensure correct vendor
    if appointment.vendor_id != current_user.vendor_profile.id:
        flash("Unauthorized action", "danger")
        return redirect(url_for('vendor.appointments'))

    # Only confirmed can be completed
    if appointment.status != "confirmed":
        flash("Only confirmed appointments can be completed", "warning")
        return redirect(url_for('vendor.appointments'))

    # ✅ Mark as completed
    appointment.status = "completed"
    db.session.commit()

    flash("Appointment marked as completed ✅", "success")
    return redirect(url_for('vendor.appointments'))

