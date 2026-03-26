from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()
cloudinary.config(
    cloud_name = os.getenv('c_cloud_name'),
    api_key    = os.getenv('c_api_key'),
    api_secret = os.getenv('c_api_secret')
)


db = SQLAlchemy()
login_manager = LoginManager() 
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://avnadmin:{os.getenv("DB_PASSWORD")}@mysql-3b0838a6-priyamjainsocial-b642.i.aivencloud.com:27509/defaultdb'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./blueprints.db'
    app.config['SECRET_KEY'] = 'some-secret-key'
    
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # ✅ LOGIN CONFIG (IMPORTANT)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login to continue"
    login_manager.login_message_category = "warning"
    
    
    #import and register all blueprints
    from vendora_app.blueprints.core.routes import core
    from vendora_app.blueprints.auth.routes import auth
    #from vendora_app.blueprints.user.routes import user
    from vendora_app.blueprints.vendor.routes import vendor
    from vendora_app.blueprints.customer.routes import customer
    from vendora_app.blueprints.appointment.routes import appointment
    
    from vendora_app.blueprints.auth.models import User
    from vendora_app.blueprints.vendor.models import Vendor
    from vendora_app.blueprints.vendor.models import Service
    from vendora_app.blueprints.customer.models import Customer
    from vendora_app.blueprints.appointment.models import Appointment
    
    
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    app.register_blueprint(core, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
   # app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(vendor, url_prefix='/vendor')
    app.register_blueprint(customer, url_prefix='/customer')
    app.register_blueprint(appointment, url_prefix='/appointment')
    
    migrate = Migrate(app,db)
    
    return app
    