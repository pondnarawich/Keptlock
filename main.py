from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
import os
# from babel.dates import format_datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import (generate_password_hash, check_password_hash)
import uuid
import random
import string

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
cur_pin = set()


# CREATE CLASS FOR DATABASE
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(12), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    is_authenticated = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=None)
    deleted_at = db.Column(db.DateTime, default=None)

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.id


class Pin(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    code = db.Column(db.String(10))
    uid = db.Column(db.String(50))
    lid = db.Column(db.String(50), nullable=False)
    date_start = db.Column(db.DateTime, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.String(12))
    status = db.Column(db.String(15), default='unused')

    def __repr__(self):
        return '<Pin %r>' % self.id


class Owner(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    uid = db.Column(db.String(50))
    lid = db.Column(db.String(50))

    def __repr__(self):
        return '<Owner %r>' % self.id


class Locker(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(20), default="My locker")
    serial = db.Column(db.String(50))
    size = db.Column(db.Integer)
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)

    def __repr__(self):
        return '<Locker %r>' % self.id


class History(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    uid = db.Column(db.String(50))
    lid = db.Column(db.String(50))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot_id = db.Column(db.Integer)
    vid_id = db.Column(db.String(50))

    def __repr__(self):
        return '<History %r>' % self.id


class Slot(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    lid = db.Column(db.String(30), nullable=False)
    opened = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Slot %r>' % self.id


class Video(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    uid = db.Column(db.String(50))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot_id = db.Column(db.String(50))
    vid1 = db.Column(db.String(50))
    vid2 = db.Column(db.String(50))

    def __repr__(self):
        return '<Video %r>' % self.id


def set_password(password):
    return generate_password_hash(password)


def check_password(hashed, password):
    return check_password_hash(hashed, password)


def id_generator(size=6, chars=string.digits):
    while True:
        pin = ''.join(random.choice(chars) for x in range(size))
        if pin not in cur_pin:
            cur_pin.add(pin)
            return pin


def create_locker(size=3):
    locker_id = str(uuid.uuid4())
    serial = str(uuid.uuid4())
    print(serial)
    new_locker = Locker(id=locker_id, serial=serial, size=size, row=size, col=1)
    db.session.add(new_locker)
    for i in range(size):
        slot = Slot(id=str(uuid.uuid4()), lid=locker_id)
        db.session.add(slot)
    db.session.commit()


# create_locker()

@login_manager.user_loader
def load_user(user_id):
    user_info = User.query.filter_by(id=user_id).first()
    return user_info


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

    uname_unique = True
    email_unique = True
    mobile_unique = True

    non_unique = User.query.filter_by(username=username, email=email, mobile=mobile).all()
    if non_unique is not None:
        for user in non_unique:
            if user.username == username:
                uname_unique = False
            elif user.email == email:
                email_unique = False
            elif user.mobile == mobile:
                mobile_unique = False

    if uname_unique and email_unique and mobile_unique:
        hashed = set_password(password)
        uid = uuid.uuid4()
        new_user = User(id=str(uid), fname=fname, lname=lname, email=email, mobile=mobile, username=username, password=hashed)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("http://127.0.0.1:8000/keptlock/user/login")
        except:
            flash("Something went wrong, please try again")
            return redirect('http://127.0.0.1:8000/keptlock/user/register')

    elif uname_unique and email_unique and not mobile_unique:
        flash("This mobile number has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')
    elif uname_unique and not email_unique and mobile_unique:
        flash("This email has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')
    elif not uname_unique and email_unique and mobile_unique:
        flash("This username has been used, try again")
        return redirect('http://127.0.0.1:8000/keptlock/user/register')


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

    user = False
    checked_pass = False

    check = User.query.filter_by(username=username).first()
    if check is not None:
        user = True
        if check_password(check.password, password):
            checked_pass = True

    if not user:
        flash('This username is not registered')
        return redirect('http://127.0.0.1:8000/keptlock/user/login')
    elif user and not checked_pass:
        flash('Password is incorrect, Try again')
        return redirect('http://127.0.0.1:8000/keptlock/user/login')
    else:
        login_user(check, remember=True)
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
    own_ids = Owner.query.filter_by(uid=uid).all()
    lockers = None
    if own_ids:
        lids = []
        for own in own_ids:
            lids.append(own.lid)
        lockers = db.session.query(Locker).filter(Locker.id.in_(lids)).all()

    return render_template('device.html', username=current_user.username, lockers=lockers)


@app.route('/keptlock/locker', methods=['POST'])
@login_required
def add_locker_api():
    serial = request.form['serial']

    serial_exist = False

    check = Locker.query.filter_by(serial=serial).first()
    if check is not None:
        serial_exist = True
        new_owner = Owner(id=str(uuid.uuid4()), uid=current_user.id, lid=check.id)
        try:
            db.session.add(new_owner)
            db.session.commit()
        except:
            flash("Something went wrong, please try again")
            return redirect("http://127.0.0.1:8000/keptlock/locker#")

    if not serial_exist:
        flash("The serial does not exist, please contact admin for further help")
    else:
        flash("New device added!")
    return redirect("http://127.0.0.1:8000/keptlock/locker#")


@app.route('/keptlock/locker', methods=['POST'])
@login_required
def create_locker_api():
    return create_locker()


@app.route('/keptlock/locker/<lid>', methods=['POST', 'PUT', 'GET', 'DELETE'])
def rud_locker_api(lid):
    check_own = Owner.query.filter_by(lid=lid).all()
    authorized = False
    for user in check_own:
        if user.uid == current_user.id:
            authorized = True

    if not authorized:
        flash("You trying to access other's locker!")
        return redirect("http://127.0.0.1:8000/keptlock/locker#")

    if request.method == 'POST':
        session['uid'] = current_user.id
        for key in request.form:
            if key.startswith('open.'):
                slot = key.partition('.')[-1]
                # TODO do something with the locker
                print("turn on slot no.", slot)
                return redirect("http://127.0.0.1:8000/keptlock/locker/"+lid+"#")
            if key.startswith('del_pin.'):
                pin = key.partition('.')[-1]
                session['lid'] = lid
                return redirect("http://127.0.0.1:8000/keptlock/locker/unlock/"+pin)
            if key.startswith('change.'):
                name = request.form['name']
                locker_info = Locker.query.filter_by(id=lid).first()
                locker_info.name = name
                try:
                    db.session.commit()
                except:
                    flash("Something went wrong, please try again")
                return redirect("http://127.0.0.1:8000/keptlock/locker/"+lid+"#")

    if request.method == 'PUT':
        print('put', lid)
    elif request.method == 'GET':
        # current_time = datetime.utcnow()

        locker = Locker.query.filter_by(id=lid).first()
        slots = Slot.query.filter_by(lid=lid).all()
        pin = Pin.query.filter_by(lid=lid, uid=current_user.id, status='unused').all()
        history = History.query.filter_by(lid=lid, uid=current_user.id).all()

        if not pin:
            pin = None
        if not history:
            history = None

        session["lid"] = lid
        return render_template("locker.html", pins=pin, histories=history, locker=locker, slots=slots, username=current_user.username, lid=lid)

    elif request.method == 'DELETE':
        print('delete', lid)


# pin

@app.route('/keptlock/locker/unlock/pin/<lid>')
def generate_pin_page(lid):
    return render_template("pin.html", username=current_user.username)


@app.route('/keptlock/locker/unlock/pin/<lid>', methods=['POST'])
def generate_pin_api(lid):
    slot = request.form['open']
    code = id_generator()
    if request.form['time'] == "time_range":
        start = request.form['start_time']
        end = request.form['end_time']
        print(start)
        print(end)

        new_pin = User(id=str(uuid.uuid4()), code=code, uid=current_user.id, slot=slot, date_start=start, date_end=end)
        try:
            db.session.add(new_pin)
            db.session.commit()
        except:
            flash("Something went wrong, please try again")

    elif request.form['time'] == "time_countdown":
        countdown = request.form['countdown']

        current_time = datetime.utcnow()
        expired_date = current_time + datetime.timedelta(minutes=countdown)

        new_pin = User(id=uuid.uuid4(), code=code, uid=current_user.id, slot=slot, date_end=expired_date)
        try:
            db.session.add(new_pin)
            db.session.commit()
        except:
            flash("Something went wrong, please try again")

    return redirect("http://127.0.0.1:8000/keptlock/locker/"+lid+"#")


@app.route('/keptlock/locker/unlock/<pid>', methods=['PUT', 'GET', 'DELETE'])
def rud_pin_api(pid):
    lid = session['lid']
    check_own = Owner.query.filter_by(lid=lid).all()
    authorized = False
    for user in check_own:
        if user.uid == current_user.id:
            authorized = True

    if not authorized:
        flash("You trying to access other's locker!")
        return redirect("http://127.0.0.1:8000/keptlock/locker#")

    if request.method == 'PUT':
        print('put', pid)
    elif request.method == 'GET':
        print('get', pid)
        pin_to_delete = Pin.query.get_or_404(pid)
        db.session.delete(pin_to_delete)
    elif request.method == 'DELETE':
        print('delete', pid)
    return redirect("http://127.0.0.1:8000/keptlock/locker/" + lid + "#")


@app.route('/keptlock/locker/unlock/<pid>', methods=['POST'])
def unlock_api(pid):
    print(pid)
    return pid

# video


@app.route('/keptlock/locker/video', methods=['POST'])
def add_video_api():
    r = request.json
    return r


@app.route('/keptlock/locker/video/<vid>', methods=['PUT', 'GET', 'DELETE'])
def rud_video_api(vid):
    lid = session["lid"]
    check_own = Owner.query.filter_by(lid=lid).all()
    authorized = False
    for user in check_own:
        if user.uid == current_user.id:
            authorized = True

    if not authorized:
        flash("You trying to access other's locker!")
        return redirect("http://127.0.0.1:8000/keptlock/locker#")

    if request.method == 'PUT':
        print('put', vid)
    elif request.method == 'GET':
        # TODO get all the info from the db from vid
        video = Video.query.filter_by(id=vid).first()

        # # mock up data
        # from db_struct.video import Video
        # import datetime
        # vid = Video(3456, 1324234, datetime.datetime.now(), 1, "pond2.mp4", "pune2.mp4")

        return render_template("video.html", username=current_user.username, vid=video, lid=lid)
    elif request.method == 'DELETE':
        print('delete', vid)
        return


@app.route('/display/<filename>')
def display_video(filename):
    # print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='vid/' + filename), code=301)


@app.route('/keptlock/locker/video', methods=['GET'])
def readall_locker_api():
    r = request.json
    return r


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


# @app.template_filter()
# def format_datetime(value, form='date'):
#     if form == 'time':
#         form = "HH:mm"
#     elif form == 'date':
#         form = "dd.MM.yy"
#     return format_datetime(value, form)


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