
from flask import Flask, session, redirect, url_for, escape, request
import json, requests

PARSE_HOSTNAME = 'http://localhost:1337/parse'
PARSE_APP_ID = 'myAppId'
PARSE_REST_API_KEY = 'myMasterKey'


endpoint = '/functions/userData/'
headers = {"X-Parse-Application-Id": PARSE_APP_ID,"X-Parse-REST-API-Key": "PARSE_REST_API_KEY","Content-Type": "application/json"}
payload = {'userID': '1234'}

r = requests.post(PARSE_HOSTNAME + endpoint, data=json.dumps(payload), headers=headers)

print(r.json)

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=email name=username placeholder=Email>
            <p><input type=password name=password placeholder=Password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=email name=username placeholder=Email>
            <p><input type=password name=password placeholder=Password>
            <p><input type=submit value=Signup>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))

# Config
# http://flask.pocoo.org/docs/0.11/config/
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True