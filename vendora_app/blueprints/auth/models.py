from vendora_app.app import db
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.mutable import MutableList
class  User(db.Model, UserMixin):
      __tablename__   = 'users'
      uid = db.Column(db.Integer, primary_key = True)
      username = db.Column(db.String(100), nullable=False,unique=True)
      password = db.Column(db.String(200), nullable=False)
      
      is_customer = db.Column(db.Boolean, default=False)
      is_vendor = db.Column(db.Boolean, default=False)   
      
      last_role = db.Column(db.String(20))
      
      name = db.Column(db.String(50))
      customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade="all, delete-orphan")
      vendor_profile = db.relationship('Vendor', backref='user', uselist=False,  cascade="all, delete-orphan")
      
      # FOR images
      profile_img = db.Column(db.String(500))
      business_imgs = db.Column(
        MutableList.as_mutable(JSON), 
        default=lambda: []
    )
      
      
      def __repr__ (self):
          return f'<User: {self.username}, Role: {self.role}>'
       
      # to return self uid 
      def get_id(self):
          return self.uid

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Foreign key links note to its user
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
