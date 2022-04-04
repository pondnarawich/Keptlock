from flask import Flask, request, render_template, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from werkzeug.security import (generate_password_hash, check_password_hash)
from sqlalchemy.orm import validates
from datetime import datetime
import re
import os
import babel

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


# CREATE CLASSS FOR DATABASE
class User(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(12), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_authenticated = False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pin(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    code = db.Column(db.String(10))
    oid = db.Column(db.String(30))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.String(12))
    status = db.Column(db.String(15))


class Owner(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    uid = db.Column(db.String(10))
    lid = db.Column(db.String(30))


class Locker(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(20))
    serial = db.Column(db.String(30))
    size = db.Column(db.Integer)
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)


class History(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    oid = db.Column(db.String(20))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.Integer)
    vid1 = db.Column(db.String(20))
    vid2 = db.Column(db.String(20))


@login_manager.user_loader
def load_user(user_id):
    # TODO Chane to query data base kong mng either sql or no sql, this to store user info when already login
    User.query.filter_by(id=user_id).all()
    print(User)

    user_info = User
    print(User.username)
    print(User.mobile)

    # user_info.id = User.id
    # user_info.name = User.fname
    # user_info.username = User.username
    # user_info.email = user.emai
    # user_info.password = "gnnchya"

    return user_info
    # mock up variable, need to be from checking with db
    # from db_struct.user import User
    # user_info = User
    # user_info.id = 12345678
    # user_info.name = "gunn"
    # user_info.username = "gnnchya"
    # user_info.email = "62011118@kmitl.ac.th"
    # user_info.password = "gnnchya"

    # return user_info


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect('http://127.0.0.1:8000/keptlock/locker')
    return render_template('index.html')


@app.route('/keptlock/user/register')
def register_page():
    if current_user.is_authenticated:
        return redirect('http://127.0.0.1:8000/keptlock/locker')
    return render_template('signup.html')


@app.route('/keptlock/user/register', methods=['POST'])
def register_api():
    if current_user.is_authenticated:
        return redirect('http://127.0.0.1:8000/keptlock/locker')

    fname = request.form['fname_reg']
    lname = request.form['lname_reg']
    mobile = request.form['mobile_reg']
    email = request.form['email_reg']
    username = request.form['username_reg']
    password = request.form['password_reg']

    # TODO validate username email mobile. Are they unique? if ok then add to db
    user = User(id='147111', fname=fname, lname=lname, mobile=mobile,
                email=email, username=username, password=password)
    user.set_password(password)
    # user.validate_username(username)
    # user.validate_email(email)

    c_username = User.query.filter(User.username == username).first()
    if c_username:
        flash("This username has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')

    if User.query.filter(User.email == email).first():
        flash("This email has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')

    if User.query.filter(User.mobile == mobile).first():
        flash("This mobile number has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')

    try:
        User.is_authenticated = True
        db.session.add(user)
        db.session.commit()
        print("successfully added user")
        return redirect("http://127.0.0.1:8000/keptlock/user/login")
    except AssertionError as exception_message:
        return render_template('error.html'), 400


@app.route('/keptlock/user/login')
def login_page():
    if current_user.is_authenticated:
        return redirect('http://127.0.0.1:8000/keptlock/locker')
    return render_template('login.html')


@app.route('/keptlock/user/login', methods=['POST'])
def login_api():
    if current_user.is_authenticated:
        return redirect('http://127.0.0.1:8000/keptlock/locker')
    username = request.form['username']
    password = request.form['password']

    from db_struct.user import User
    user_info_login = User(12345, "gunn", "chai", "62011118@kmitl.ac.th",
                           "0970047016", "gnnchya", "gnnchya", None, None, None)

    # TODO Check the user and password in the database
    # mock up variable, need to be from checking with db
    user = True
    checked_pass = True

    # No username in the database
    if not user:
        flash('This username is not registered')
        return redirect('http://127.0.0.1:8000/keptlock/user/login')
    # wrong password
    elif user and not checked_pass:
        flash('Password is incorrect, Try again')
        return redirect('http://127.0.0.1:8000/keptlock/user/login')
    # login success
    else:
        login_user(user_info_login, remember=True)
        return redirect('http://127.0.0.1:8000/keptlock/locker')


@app.route('/keptlock/user/logout')
@login_required
def logout_api():
    logout_user()
    return redirect('http://127.0.0.1:8000')


@app.route('/keptlock/user/<uid>', methods=['PUT', 'GET', 'DELETE'])
@login_required
def crud_api(uid):
    print(uid)
    if request.method == 'PUT':
        print('post', uid)
    elif request.method == 'GET':
        print('get', uid)
    elif request.method == 'DELETE':
        print('delete', uid)
    return uid


# locker api
@app.route('/keptlock/locker')
@login_required
def lockers_page():
    uid = current_user.id
    # TODO: query all the device based on user id

    from db_struct.locker import Locker
    # mock up variable, need to be query from db
    locker1 = Locker(1234, "Pitsinee", "ABCDEFG", 3, 3, 1)
    locker2 = Locker(1235, "Mind", "AB12345", 3, 3, 1)
    locker3 = Locker(1236, "Mickey's owner", "1234EFG", 3, 3, 1)
    locker4 = Locker(1246, "Minnie's owner", "1245nFG", 3, 3, 1)

    lockers = [locker1, locker2, locker3, locker4]

    return render_template('device.html', username=current_user.username, lockers=lockers)


@app.route('/keptlock/locker', methods=['POST'])
@login_required
def add_locker_api():
    serial = request.form['serial']
    # TODO: query the device according to the serial to check if the serial exists

    serial_exist = True

    if not serial_exist:
        flash("The serial does not exist, please contact admin for further help")
    else:
        flash("New device added!")
    return redirect("http://127.0.0.1:8000/keptlock/locker#")


@app.route('/keptlock/locker', methods=['POST'])
@login_required
def create_locker_api():
    r = request.json
    return r


@app.route('/keptlock/locker/<lid>', methods=['PUT', 'GET', 'DELETE'])
def rud_locker_api(lid):
    print(lid)
    if request.method == 'PUT':
        print('put', lid)
    elif request.method == 'GET':
        # TODO: query history and active pin of the locker from locker id

        # mock up data
        from db_struct.pin import Pin
        import datetime
        pin1 = Pin(1234, 121212, 1324234, datetime.datetime.now(), 2, "valid")
        pin2 = Pin(3243, 454545, 1324234, datetime.datetime.now(), 1, "valid")
        pin3 = Pin(2342, 676767, 1324234, datetime.datetime.now(), 2, "valid")
        pin4 = Pin(5676, 787878, 1324234, datetime.datetime.now(), 3, "valid")

        pin = [pin1, pin2, pin3, pin4]

        from db_struct.history import History
        his1 = History(1432, 1324234, datetime.datetime.now(), 1,
                       "static/vid.pune.mov", "static/vid.pond.mov")
        his2 = History(3546, 1324234, datetime.datetime.now(), 2,
                       "static/vid.pune.mov", "static/vid.pond.mov")
        his3 = History(2343, 1324234, datetime.datetime.now(), 3,
                       "static/vid.pune.mov", "static/vid.pond.mov")
        his4 = History(1643, 1324234, datetime.datetime.now(), 2,
                       "static/vid.pune.mov", "static/vid.pond.mov")

        history = [his1, his2, his3, his4]

        return render_template("locker.html", pin=pin, history=history)

    elif request.method == 'DELETE':
        print('delete', lid)
    return lid


# hading cache and error

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.errorhandler(404)
def not_found(e):
    flash("Page not found")
    return render_template('error.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return redirect('http://127.0.0.1:8000/keptlock/user/login')


@app.errorhandler(400)
def signUp_error(e):
    flash("Unable to Sign Up")
    return render_template('error.html'), 400


@app.template_filter()
def format_datetime(value, form='date'):
    if form == 'time':
        form = "HH:mm"
    elif form == 'date':
        form = "dd.MM.yy"
    return babel.dates.format_datetime(value, form)


if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run(host='127.0.0.1', port=8000)
