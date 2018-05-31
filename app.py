
from flask import Flask, session, redirect, url_for, escape, request # Flask
import json, requests, urllib # Parse Server

app = Flask(__name__)

API_ROOT = 'https://nathantannar.me/api/dev'
APP_ID = '5++ejBLY/kzVaVibHAIIQZvbawrEywUCNqpD+FVpHgU='
APP_KEY = 'oR3Jp5YMyxSBu6r6nh9xuYQD5AcsdubQmvATY1OEtXo='
API_HEADERS = {
    "X-Parse-Application-ID": APP_ID,
    "X-Parse-Master-Key": APP_KEY,
    "Content-Type": "application/json"
}

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        params = urllib.parse.urlencode({"username": username, "password": password})
        url = API_ROOT + ('/login?%s' % params)
        headers = {
            "X-Parse-Application-Id": APP_ID,
            "X-Parse-Master-Key": APP_KEY,
            "X-Parse-Revocable-Session": "1"
        }
        response = requests.get(url, headers=headers, verify=False)
        json_data = json.loads(response.text)
        print(json_data)
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
    return redirect(url_for('index'))

# Config
# http://flask.pocoo.org/docs/0.11/config/
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
