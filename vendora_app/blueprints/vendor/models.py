
from vendora_app.app import db
from flask_login import UserMixin
from datetime import datetime


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120))
    
    business_name = db.Column(db.String(100))
    business_address = db.Column(db.String(200))
    
    phone_number = db.Column(db.String(20), nullable=False)
    whatsapp_number = db.Column(db.String(20))
    
    open_duration = db.Column(db.String(100))
    payment_type = db.Column(db.String(50))
    
    year_of_establishment = db.Column(db.Integer)
    
    rating = db.Column(db.Float)
    rater_no = db.Column(db.Integer)
    services = db.relationship('Service', backref='vendor', lazy=True)
    # add other vendor-specific fields
    # --- Relationships ---
    # Example relationship for Addresses (assuming an 'Addresses' model exists)
    # addresses = db.relationship('Address', backref='vendor', lazy='dynamic')
    
class Service(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"))
    service_name = db.Column(db.String(150), nullable=False)
    service_type = db.Column(db.String(150), nullable=False)
    duration_minutes = db.Column(db.Integer)
    service_cost = db.Column(db.Integer)
    
    
