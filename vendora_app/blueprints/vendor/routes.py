from flask import request, render_template, redirect, url_for, Blueprint, flash
from vendora_app.blueprints.vendor.models import Vendor
from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.app import db
from cloudinary.uploader import upload
vendor = Blueprint('vendor', __name__, template_folder = 'templates')

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
def appointments():
    return render_template('vendor/appointments.html')

@vendor.route('/analytics')
def analytics():
    return render_template('vendor/dashboard.html')

@vendor.route('/reviews')
def reviews():
    return render_template('vendor/dashboard.html')

@vendor.route('/support')
def support():
    return render_template('vendor/dashboard.html')