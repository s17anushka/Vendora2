from flask import request, render_template, redirect, url_for, Blueprint, session, flash
from vendora_app.app import db

from flask_login import login_user, current_user, login_required
from vendora_app.blueprints.vendor.models import Vendor

appointment = Blueprint('appointment', __name__, template_folder = 'templates')

@appointment.route('/')
def index():
    return render_template('appointment/index.html')
