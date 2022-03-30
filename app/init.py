from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def send():
    response = requests.get('http://127.0.0.1:5000')
    r = response.json()
    print(r)


if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()