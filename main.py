from flask import Flask, request, render_template, redirect, flash
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
import os

template_dir = os.path.abspath('templates')
static_dir = os.path.abspath('static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
     #TODO Chane to query data base kong mng either sql or no sql, this to store user info when already login
    # return User.query.get(int(user_id))

    from db_struct.user import User
    user_info = User
    user_info.id = 12345678
    user_info.name = "gunn"
    user_info.username = "gnnchya"
    user_info.email = "62011118@kmitl.ac.th"
    user_info.password = "gnnchya"

    return user_info


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/keptlock/user/register')
def register_page():
    return render_template('signup.html')


@app.route('/keptlock/user/register', methods=['POST'])
def register_api():
    fname = request.form['fname_reg']
    lname = request.form['lname_reg']
    mobile = request.form['mobile_reg']
    email = request.form['email_reg']
    username = request.form['username_reg']
    password = request.form['password_reg']

    #TODO validate username email mobile. Are they unique? if ok then add to db

    uname_unique = True
    email_unique = True
    mobile_unique = True

    if uname_unique and email_unique and mobile_unique:
        return redirect("http://127.0.0.1:8000/keptlock/user/login")
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
    return render_template('login.html')


@app.route('/keptlock/user/login', methods=['POST'])
def login_api():
    username = request.form['username']
    password = request.form['password']

    user = True
    checked_pass = True

    from db_struct.user import User
    user_info_login = User(12345, "gunn", "chai", "62011118@kmitl.ac.th", "0970047016", "gnnchya", "gnnchya", None, None, None)

    #TODO Check the user and password in the database

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
        return redirect('http://127.0.0.1:8000/keptlock/device')


@app.route('/keptlock/device')
@login_required
def device():
    return render_template('device.html', username=current_user.username)


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


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.errorhandler(404)
def not_found(e):
    flash("Page not found")
    return render_template('error.html'), 404

@app.errorhandler(401)
def not_found(e):
    flash("You trying to access the service while not logging in")
    return render_template('error.html'), 401


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