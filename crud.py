from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import (generate_password_hash, check_password_hash)
from sqlalchemy.orm import validates

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config["TEMPLATES_AUTO_RELOAD"] = True
db = SQLAlchemy(app)


# CREATE CLASS FOR DATABASE
class User(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(12), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=None)
    deleted_at = db.Column(db.DateTime, default=None)

    is_authenticated = False

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pin(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    code = db.Column(db.String(10))
    uid = db.Column(db.String(30))
    date_start = db.Column(db.DateTime, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.String(12))
    status = db.Column(db.String(15), default='unused')


class Owner(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    uid = db.Column(db.String(10))
    lid = db.Column(db.String(30))


class Locker(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(20), default='My locker')
    serial = db.Column(db.String(30))
    size = db.Column(db.Integer)
    row = db.Column(db.Integer)
    col = db.Column(db.Integer)


class History(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    uid = db.Column(db.String(20))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    slot = db.Column(db.Integer)
    vid1 = db.Column(db.String(20))
    vid2 = db.Column(db.String(20))


class Slot(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    lid = db.Column(db.String(30), nullable=False)
    opened = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Slot %r>' % self.id

# def create(info, table):


# read by id
def read(id, table):
    res = table.query.filter_by(id=id).first()
    return res


def update(id, info, table):
    data = table.query.filter_by(id=id).first()
    if data:
        db.session.delete(data)
        db.session.commit()

    data = table(**data)


def delete(id, table):

    data = table.query.get_or_404(id)

    try:
        db.session.delete(data)
        db.session.commit()
        return True
    except:
        return False

    # user = User(id='147111', fname=fname, lname=lname, mobile=mobile,
    #             email=email, username=username, password=password)
    # user.set_password(password)
    # # user.validate_username(username)
    # # user.validate_email(email)

    # c_username = User.query.filter(User.username == username).first()
    # if c_username:
    #     flash("This username has been used, try again")
    #     return redirect('http://127.0.0.1:8000/keptlock/user/register')

    # if User.query.filter(User.email == email).first():
    #     flash("This email has been used, try again")
    #     return redirect('http://127.0.0.1:8000/keptlock/user/register')

    # if User.query.filter(User.mobile == mobile).first():
    #     flash("This mobile number has been used, try again")
    #     return redirect('http://127.0.0.1:8000/keptlock/user/register')

    # try:
    #     User.is_authenticated = True
    #     db.session.add(user)
    #     db.session.commit()
    #     print("successfully added user")
    #     return redirect("http://127.0.0.1:8000/keptlock/user/login")
    # except AssertionError as exception_message:
    #     return render_template('error.html'), 400