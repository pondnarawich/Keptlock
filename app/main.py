from flask import Flask
import requests
import os
from db_struct import locker
app = Flask(__name__)

path = r"/home/pondnarawich/Documents/GitHub/keptlock/app/init.py"
assert os.path.isfile(path)
with open(path, "r") as f:
    pass

@app.route('/keptlock/usesr/register',method=['POST'])
def register():
    print(b)
    return r

@app.route('/off')
def off():
    response = requests.get('http://127.0.0.1:5000/off')
    r = response.json()
    print(r)
    return r

@app.route('/start')
def start():
    response = requests.get('http://127.0.0.1:5000/start')
    r = response.json()
    print(r)
    return r

@app.route('/stop')
def stop():
    response = requests.get('http://127.0.0.1:5000/stop')
    r = response.json()
    print(r)
    return r

a = locker
a.id = '123'
print(a)

if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(host='127.0.0.1',port=8000)