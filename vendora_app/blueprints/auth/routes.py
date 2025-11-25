from flask import request, render_template, redirect, url_for, Blueprint, session, flash
from vendora_app.app import db, bcrypt

from flask_login import login_user, logout_user, current_user, login_required
from vendora_app.blueprints.auth.models import User, Note


auth = Blueprint('auth', __name__, template_folder = 'templates')



"""
@auth.route('/')
def index():
    todos = User.query.all()
    return render_template('todos/index.html' , todos = todos)


@auth.route('/create', methods = ['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('todos/create.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        done = True if 'done' in request.form.keys() else False
        
        description = description if description != ''else None
        todo = Todo(title= title, description=description, done = done)
        
        db.session.add(todo)
        db.session.commit()
        
        return redirect(url_for('todos.index'))
"""
    
@auth.route('/')
def index():
    return render_template('auth/index.html')

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        

    user = User.query.filter_by(username=username).first()

    if not user:
        #new user
      hashed_password = bcrypt.generate_password_hash(password)
      new_user = User(username =username, password=hashed_password)
      if role == 'vendor':
          new_user.is_vendor = True
      else:
          new_user.is_customer = True
      db.session.add(new_user)
      db.session.commit()
      flash('Account created successfully! Please login.','Success')
        
    else:
        #Already existing user
        #checking password
        if bcrypt.check_password_hash(user.password,password):
            if role == 'vendor' and not user.is_vendor:
                user.is_vendor = True
                db.session.commit()
                flash('You are now also Registered as a vendor!','success')
            elif role == 'customer' and not user.is_customer:
                user.is_customer = True
                db.session.commit()
                flash('You are now also registered as a Customer!', 'success')
            else:
                flash(f'You are already registered as a {role}','info')
        else:
            flash('Incorrect password for this username.','danger')
        
    return redirect(url_for('auth.login'))
        
        
        
        #return redirect(url_for('auth.login'))

@auth.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        

        # Authentication check
        user = User.query.filter(User.username == username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Invalid username or password','danger')
            return redirect(url_for('auth.login'))
        
        #check if the user has selscted a valid role
        if role == 'vendor' and not user.is_vendor:
            flash('You are not registered as a vendor.','danger')
            return redirect(url_for('auth.signup'))
        elif role =='customer' and not user.is_customer:
            flash('You are not registered as a customer.','danger')
            return redirect(url_for('auth.signup'))
        
        # All good -> Login and Redirect
        login_user(user)
        user.last_role = role
        db.session.commit()
        
        if role == 'customer':
            if not user.customer_profile:
                flash('Please complete your customer profile.','info')
                return redirect(url_for('customer.profile_setup'))
            else:
                return redirect(url_for('customer.dashboard'))
        
        elif role =='vendor':
            if not user.vendor_profile:
                flash('Please complete your vendor profile.','info')
                return redirect(url_for('vendor.profile_setup'))
            else:
                return redirect(url_for('vendor.dashboard'))
        
            

@auth.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('customer.vendors'))

@auth.route('/new_note',methods = ['GET','POST'])
@login_required
def new_note():
    if request.method == 'GET':
        return render_template('auth/note.html')
    elif request.method == 'POST':
        print("got request")
        note = request.form.get('note')
        new_note = Note(content=note, user_id=current_user.uid)
        db.session.add(new_note)
        db.session.commit()
        #flash('Note added successfully!', 'success')
        return redirect(url_for('auth.show_notes'))
        
@auth.route("/show_notes")
def show_notes():
        user_notes = Note.query.filter_by(user_id=current_user.uid).all()
        notes_html = "<ul>"
        for n in user_notes:
            notes_html += f"<li>{n.content}</li>"
        notes_html += "</ul>"

        return f"""
            <a href="/">Home</a> 

            <a href="/logout">logout</a>
            <p>Note added successfully!</p>
            {notes_html}
            <a href="/new_note">Add another note</a> <br>
                                   
        """
@auth.route("/upload-profile-image", methods=["GET","POST"])
def upload_profile_image():
    if request.method == "GET":
        return render_template("profile_update.html")