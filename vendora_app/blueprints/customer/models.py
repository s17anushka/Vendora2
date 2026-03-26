from vendora_app.app import db
from flask_login import UserMixin

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    # add other customer-specific fields
    
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    city = db.Column(db.String(100))