from flask import request, render_template, redirect, url_for, Blueprint, flash
from vendora_app.blueprints.vendor.models import Vendor
from vendora_app.blueprints.customer.models import Customer
from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.app import db, bcrypt

customer = Blueprint('customer', __name__, template_folder = 'templates')

@customer.route('/')
def index():
    return render_template('customer/index.html')

@customer.route('/homepage')
def vendors():
    vendors = Vendor.query.all()
    return render_template('customer/vendors.html',vendors = vendors)

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
    return render_template('customer/dashboard.html')
    
@customer.route('/vendor/<int:vendor_id>')
def vendor_details(vendor_id):
    v = Vendor.query.get_or_404(vendor_id)
    return render_template("customer/vendor_detail.html", vendor=v)
