from flask import request, render_template, redirect, url_for, Blueprint, flash, abort
from vendora_app.blueprints.vendor.models import Vendor, Service
from vendora_app.blueprints.customer.models import Customer
from vendora_app.blueprints.appointment.models import Appointment
from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.app import db
from cloudinary.uploader import upload,  destroy
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json



vendor = Blueprint('vendor', __name__, template_folder = 'templates')
from sqlalchemy import func
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
    vendor_profile.year_of_establishment = request.form.get(
        'year_of_establishment', vendor_profile.year_of_establishment
    )

    # ==========================
    # Image Handling (Replace)
    # ==========================
    files = request.files.getlist("image")

    # ✅ Only proceed if user uploaded new images
    if files and files[0].filename != "":

        # 🔴 Step 1: Delete old images from Cloudinary
        for url in current_user.business_imgs:
            try:
                public_id = url.split("/")[-1].split(".")[0]
                folder_path = f"vendora/{current_user.uid}/business_img/"
                destroy(folder_path + public_id)
            except Exception as e:
                print("Error deleting image:", e)

        # 🔴 Step 2: Clear DB list
        current_user.business_imgs = []

        # 🔴 Step 3: Upload new images
        uploaded_urls = []
        for i, file in enumerate(files, start=1):
            result = upload(
                file,
                folder=f"vendora/{current_user.uid}/business_img/",
                public_id=f"img_{str(i)}",
                overwrite=True
            )
            uploaded_urls.append(result["secure_url"])

        # 🔴 Step 4: Save new images
        current_user.business_imgs = uploaded_urls

    # ==========================
    # Commit Changes
    # ==========================
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
    if not current_user.is_vendor:
        abort(403)
    
    vendor = current_user.vendor_profile
    v_id = vendor.id

    # Calculate Average Rating from the Appointment table
    # We round it to 1 decimal place for a clean UI
    avg_rating_query = db.session.query(func.avg(Appointment.rating))\
        .filter(Appointment.vendor_id == v_id, Appointment.rating.isnot(None))\
        .scalar()
    
    avg_rating = round(float(avg_rating_query), 1) if avg_rating_query else 0.0

    # Quick Stats
    total_revenue = db.session.query(func.sum(Appointment.service_cost))\
        .filter(Appointment.vendor_id == v_id, Appointment.status == 'completed').scalar() or 0
    
    pending_bookings = Appointment.query.filter_by(vendor_id=v_id, status='pending').count()
    
    customer_count = db.session.query(func.count(func.distinct(Appointment.customer_id)))\
        .filter(Appointment.vendor_id == v_id).scalar() or 0

    return render_template(
        'vendor/dashboard.html',
        vendor=vendor,
        total_revenue=total_revenue,
        pending_bookings=pending_bookings,
        customer_count=customer_count,
        avg_rating=avg_rating
    )
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
    # 1. Vendor ID from relationship
    v_id = current_user.vendor_profile.id
    
    # 2. Total Revenue (Directly from Appointment)
    # This is now a very fast, single-table query
    total_revenue = db.session.query(func.sum(Appointment.service_cost))\
        .filter(Appointment.vendor_id == v_id, Appointment.status == 'completed')\
        .scalar() or 0

    # 3. Total Unique Customers
    total_customers = db.session.query(func.count(func.distinct(Appointment.customer_id)))\
        .filter(Appointment.vendor_id == v_id).scalar() or 0

    # 4. Average Rating
    # float() ensures compatibility with Jinja and JavaScript
    avg_rating = db.session.query(func.avg(Appointment.rating))\
        .filter(Appointment.vendor_id == v_id, Appointment.rating.isnot(None))\
        .scalar() or 0

    # 5. Most Used Services (Pie Chart)
    # We still join Service here just to get the 'service_name' for the labels
    service_stats = db.session.query(
        Service.service_name, 
        func.count(Appointment.id).label('count')
    ).join(Appointment, Appointment.service_id == Service.id)\
     .filter(Appointment.vendor_id == v_id)\
     .group_by(Service.service_name)\
     .order_by(desc('count')).all()
    
    service_labels = [s[0] for s in service_stats]
    service_counts = [s[1] for s in service_stats]

    # 6. Demand Trend (Line Chart)
    trend_query = db.session.query(
        func.date_format(Appointment.start_time, '%b').label('month_name'), 
        func.count(Appointment.id).label('app_count')
    ).filter(Appointment.vendor_id == v_id)\
     .group_by(func.date_format(Appointment.start_time, '%Y-%m'), 'month_name')\
     .order_by(func.min(Appointment.start_time))\
     .all()

    trend_labels = [t[0] for t in trend_query]
    trend_counts = [t[1] for t in trend_query]

    return render_template(
        'vendor/analytics.html', 
        total_customers=total_customers,
        total_revenue=total_revenue,
        avg_rating=round(float(avg_rating), 1),
        service_labels=json.dumps(service_labels),
        service_counts=json.dumps(service_counts),
        trend_labels=json.dumps(trend_labels),
        trend_counts=json.dumps(trend_counts)
    )

@vendor.route('/reviews')
@login_required
def reviews():
    # 1. Access the vendor ID from the users -> vendor relationship
    # Based on your table desc, current_user is from 'users', 
    # which connects to 'vendor' via user_id.
    vendor_id = current_user.vendor_profile.id 

    # 2. Query appointments for this vendor that have reviews
    # We join with Customer to get 'full_name' and Service for 'service_name'
    vendor_reviews = db.session.query(Appointment, Customer, Service).\
        join(Customer, Appointment.customer_id == Customer.id).\
        join(Service, Appointment.service_id == Service.id).\
        filter(Appointment.vendor_id == vendor_id).\
        filter(Appointment.rating.isnot(None)).\
        order_by(Appointment.id.desc()).all()

    # 3. Calculate Summary Statistics
    total_reviews = len(vendor_reviews)
    
    if total_reviews > 0:
        avg_rating = db.session.query(func.avg(Appointment.rating)).\
            filter(Appointment.vendor_id == vendor_id).\
            filter(Appointment.rating.isnot(None)).scalar()
        
        pos_count = Appointment.query.filter_by(vendor_id=vendor_id, sentiment='positive').count()
        neu_count = Appointment.query.filter_by(vendor_id=vendor_id, sentiment='neutral').count()
        neg_count = Appointment.query.filter_by(vendor_id=vendor_id, sentiment='negative').count()

        stats = {
            "avg": round(avg_rating, 1),
            "total": total_reviews,
            "pos": round((pos_count / total_reviews) * 100),
            "neu": round((neu_count / total_reviews) * 100),
            "neg": round((neg_count / total_reviews) * 100)
        }
    else:
        stats = {"avg": 0, "total": 0, "pos": 0, "neu": 0, "neg": 0}

    return render_template('vendor/reviews.html', reviews_data=vendor_reviews, stats=stats)

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

