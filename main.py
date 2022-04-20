from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
import os
# from babel.dates import format_datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
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

UPLOAD_FOLDER = '/static/vid'

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
    lid = db.Column(db.String(50))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.Integer)
    vid_id = db.Column(db.String(50))

    def __repr__(self):
        return '<History %r>' % self.id


class Slot(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    lid = db.Column(db.String(30), nullable=False)
    slot_no = db.Column(db.Integer, nullable=False)
    opened = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Slot %r>' % self.id


class Video(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.Integer)
    vid1 = db.Column(db.String(50))
    vid2 = db.Column(db.String(50))

    def __repr__(self):
        return '<Video %r>' % self.id


def set_password(password):
    return generate_password_hash(password)


def check_password(hashed, password):
    return check_password_hash(hashed, password)


def code_generator(size=6, chars=string.digits):
    while True:
        pin = ''.join(random.choice(chars) for x in range(size))
        if pin not in cur_pin:
            cur_pin.add(pin)
            return pin


def temp_his(lid):
    print("created")
    vid_id = str(uuid.uuid4())
    new_vid = Video(id=vid_id, date_time=datetime.now(), slot=1, vid1="pond2.mp4", vid2="pune2.mp4")
    db.session.add(new_vid)
    new_his = History(id=str(uuid.uuid4()), lid=lid, date_time=datetime.now(), slot=1, vid_id=vid_id)
    db.session.add(new_his)
    db.session.commit()


# TODO use this when the pin is used
def renew_code(code):
    return cur_pin.remove(code)


# TODO use then when create new locker
def create_locker(size=3):
    locker_id = str(uuid.uuid4())
    serial = str(uuid.uuid4())
    print(serial)
    new_locker = Locker(id=locker_id, serial=serial, size=size, row=size, col=1)
    db.session.add(new_locker)
    for i in range(size):
        slot = Slot(id=str(uuid.uuid4()), lid=locker_id, slot_no=i)
        db.session.add(slot)
    db.session.commit()
    return Locker


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


# TODO need testing
@app.route('/keptlock/locker', methods=['POST'])
def create_locker_api():
    slot = request.json['slot']
    return create_locker(int(slot))


@app.route('/keptlock/locker/<lid>', methods=['POST', 'PUT', 'GET', 'DELETE'])
@login_required
def rud_locker_api(lid):
    # temp_his(lid)
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
                try:
                    slot_info = Slot.query.filter_by(lid=lid, slot_no=slot).first()
                    if slot_info.opened:
                        flash("Something went wrong, try again")
                    else:
                        slot_info.opened = True
                        db.session.commit()
                #         sent to pi
                except:
                    flash("Something went wrong, try again")

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
        locker = Locker.query.filter_by(id=lid).first()
        slots = Slot.query.filter_by(lid=lid).all()
        pin = Pin.query.filter_by(lid=lid, uid=current_user.id, status='unused').all()
        # TODO ask pond if want to show only for the action of that user or all user on a single locker
        history = History.query.filter_by(lid=lid).all()

        if not pin:
            pin = None
        if not history:
            history = None

        if pin is not None:
            for p in pin:
                if p.date_end < datetime.now():
                    p.status = 'expired'
                    # renew_code(p.code)

            try:
                db.session.commit()
                pin = Pin.query.filter_by(lid=lid, uid=current_user.id, status='unused').all()
                if not pin:
                    pin = None
            except:
                flash("Something went wrong, please try again")

        session["lid"] = lid
        return render_template("locker.html", pins=pin, histories=history, locker=locker, slots=slots, username=current_user.username, lid=lid)

    elif request.method == 'DELETE':
        print('delete', lid)


# pin

@app.route('/keptlock/locker/unlock/pin/<lid>')
@login_required
def generate_pin_page(lid):
    return render_template("pin.html", username=current_user.username)


@app.route('/keptlock/locker/unlock/pin/<lid>', methods=['POST'])
@login_required
def generate_pin_api(lid):
    slot = request.form['open']
    code = code_generator()
    if request.form['time'] == "time_range":
        start = request.form['start_time']
        end = request.form['end_time']
        if start == "" or end == "":
            flash("Please select the valid time")
            return redirect("http://127.0.0.1:8000/keptlock/locker/unlock/pin/"+lid)

        start = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M')

        if start <= datetime.now():
            flash("The time interval must be in the future")
            return redirect("http://127.0.0.1:8000/keptlock/locker/unlock/pin/" + lid)
        elif start > end:
            flash("End time must be later than the start time")
            return redirect("http://127.0.0.1:8000/keptlock/locker/unlock/pin/" + lid)

        new_pin = Pin(id=str(uuid.uuid4()), code=code, uid=current_user.id, slot=slot, lid=lid, date_start=start, date_end=end)
        try:
            db.session.add(new_pin)
            db.session.commit()
        except:
            flash("Something went wrong, please try again")

    elif request.form['time'] == "time_countdown":
        countdown = request.form['countdown']

        if countdown == "":
            flash("Please select the valid time")
            return redirect("http://127.0.0.1:8000/keptlock/locker/unlock/pin/" + lid)

        current_time = datetime.now()
        expired_date = current_time + timedelta(minutes=int(countdown))

        new_pin = Pin(id=str(uuid.uuid4()), code=code, uid=current_user.id, lid=lid, slot=slot, date_end=expired_date)
        try:
            db.session.add(new_pin)
            db.session.commit()
        except:
            flash("Something went wrong, please try again")

    return redirect("http://127.0.0.1:8000/keptlock/locker/"+lid+"#")


@app.route('/keptlock/locker/unlock/<pid>', methods=['PUT', 'GET', 'DELETE'])
@login_required
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
        try:
            # pin = Pin.query.filter_by(id=pid).first()
            # renew_code(pin.code)
            Pin.query.filter_by(id=pid).delete()
            db.session.commit()
        except:
            flash("Something went wrong, Try again")

    elif request.method == 'DELETE':
        print('delete', pid)
    return redirect("http://127.0.0.1:8000/keptlock/locker/" + lid + "#")


@app.route('/keptlock/locker/unlock/pin/<lid>', methods=['POST'])
def unlock_pin_api(lid):
    pin = Pin.query.filter_by(lid=lid, uid=current_user.id, status='unused').all()

    if pin:
        for p in pin:
            if p.date_end < datetime.now():
                p.status = 'expired'
                # renew_code(p.code)

    print(lid)
    code = request.json['code']
    pin = Pin.query.filter_by(lid=lid, code=str(code), status="unused").first()

    if not pin:
        return "Pin is invalid or expired", 400
    # renew_code(pin.code)
    return pin.slot, 200


@app.route('/keptlock/locker/unlock/<lid>', methods=['POST'])
def slot_update_api(lid):
    slots = request.json['slots']
    try:
        slot_db = Slot.query.filter_by(lid=lid).all()
        for no, slot in enumerate(slot_db):
            slot.status = slots[no]
        db.session.commit()
    except:
        return "something went wrong", 400
    return "ok", 200

# video


# TODO need testing
@app.route('/keptlock/locker/video', methods=['POST'])
def add_video_api():
    if 'vid1' not in request.files:
        return "something went wrong", 400

    vid1 = request.files["vid1"]
    vid2 = request.files["vid2"]
    if vid1 and vid2:
        vid1.save(os.path.join(app.config['UPLOAD_FOLDER'], vid1.filename))
        vid2.save(os.path.join(app.config['UPLOAD_FOLDER'], vid2.filename))

        lid_pi = request.json['lid']
        slot = request.json['slot']
        vid_id = str(uuid.uuid4())
        try:
            new_vid = Video(id=vid_id, date_time=datetime.now(), slot=slot, vid1=vid1.filename, vid2=vid2.filename)
            db.session.add(new_vid)
            new_his = History(id=str(uuid.uuid4()), lid=lid_pi, date_time=datetime.now(), slot=slot, vid_id=vid_id)
            db.session.add(new_his)
            db.session.commit()
            return "ok", 200
        except:
            return "something went wrong", 400


@app.route('/keptlock/locker/video/<vid>', methods=['PUT', 'GET', 'DELETE'])
@login_required
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
@login_required
def display_video(filename):
    # print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='vid/' + filename), code=301)


@app.route('/keptlock/locker/video', methods=['GET'])
@login_required
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


@app.errorhandler(500)
def not_found(e):
    flash("Something went wrong")
    return render_template('error.html'), 500


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
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.debug = True
    app.run(host='127.0.0.1', port=5000)