from flask import Flask
from flask import request
import requests
import os
# from db_struct import locker
app = Flask(__name__)


path = r"/home/pondnarawich/Documents/GitHub/keptlock/app/init.py"
assert os.path.isfile(path)
with open(path, "r") as f:
    pass


@app.route('/keptlock/user/register', methods=['POST'])
def register_api():
    r = request.json
    return r


@app.route('/keptlock/user/login', methods=['POST'])
def login_api():
    r = request.json
    print(r)
    return r


@app.route('/keptlock/user/logout/<uid>', methods=['POST'])
def logout_api(uid):
    print(uid)
    return uid


@app.route('/keptlock/user/<uid>', methods=['PUT', 'GET', 'DELETE'])
def crud_api(uid):
    print(uid)
    if request.method == 'PUT':
        print('post',uid)
    elif request.method == 'GET':
        print('get', uid)
    elif request.method == 'DELETE':
        print('delete', uid)
    return uid


if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host='127.0.0.1', port=8000)
