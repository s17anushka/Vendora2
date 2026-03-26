from vendora_app.app import db
from flask_login import UserMixin


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    rating = db.Column(db.Integer, nullable=True)   # 1 to 5
    review = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(50), default="pending")
    vendor = db.relationship('Vendor')
    service = db.relationship('Service')
    
    # ✅ NEW: Sentiment column
    sentiment = db.Column(db.String(20), nullable=True)  
    # values: "positive", "negative", "neutral"