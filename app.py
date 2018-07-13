
from flask import Flask, session, redirect, url_for, escape, request # Flask
import subprocess
import json, requests, urllib, urllib3 # Parse Server
from threading import Timer

API_ROOT = 'http://nathantannar.me/api/prod'
APP_ID = '5ejBLYkzVaVibHAIIQZvbawrEywUCNqpDFVpHgU'
APP_KEY = 'oR3Jp5YMyxSBu6r6nh9xuYQD5AcsdubQmvATY1OEtXo'
API_HEADERS = {
    "X-Parse-Application-ID": APP_ID,
    "X-Parse-Master-Key": APP_KEY,
    "Content-Type": "application/json"
}

def startNFC():
    return

def clearNFC():
    subprocess.call(['./SharedMemory/build/SharedMemory', 'XXXXXXXXXX'])

def writeToNFC(transactionID):
    subprocess.call(['./SharedMemory/build/SharedMemory', transactionID])
    timeout = Timer(30.0, clearNFC)
    timeout.start()

def setBusinessId(id):
    session['businessId'] = id
    f = open("businessId.txt", "w")
    f.write(id)
    f.close()

def popBusinessId():
    session.pop('businessId', None)
    f = open("businessId.txt", "w")
    f.write('')
    f.close()

def recoverSession():
    # Recover Session
    with open("businessId.txt", "r") as f:
        f.seek(0) #ensure you're at the start of the file..
        first_char = f.read(1) #get the first character
        if not first_char:
            # File empty
            session.pop('businessId', None)
            return
        else:
            f.seek(0) #first character wasn't empty, return to start of file
            session['businessId'] = f.read()
        f.close() 

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.before_first_request
def startup():
    urllib3.disable_warnings()
    recoverSession()
    startNFC()

@app.route('/')
def index():
    if 'businessId' in session:
        return 'Logged in as business %s' % escape(session['businessId'])
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        params = urllib.parse.urlencode({'username': username, 'password': password})
        url = API_ROOT + ('/login?%s' % params)
        response = requests.get(url, headers=API_HEADERS, verify=False)
        json_data = json.loads(response.text)
        print(json_data)
        if 'business' in json_data:
            id = json_data['business']['objectId']
            setBusinessId(id)
            return redirect(url_for('index'))
        if 'error' in json_data:
            return json_data['error']
        return 'No business connected to your account'
        
    elif request.method == 'GET':
        return '''
            <form method="post">
                <p><input type=email name=username placeholder=Email>
                <p><input type=password name=password placeholder=Password>
                <p><input type=submit value=Login>
            </form>
        '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    if 'businessId' in session:
        popBusinessId()
        return 'Logged Out'
    else:
        return redirect(url_for('index'))

@app.route('/openTransaction', methods=['POST'])
def openTransaction():
    if not ('businessId' in session):
        return {'error':'No business logged in'}

    json_data = request.get_json(silent=True)
    data = {}
    if 'items' in json_data:
        # inventory based
        data['items'] = json_data['items']
    elif ('amount' in json_data) and ('itemCount' in json_data):
        # purchase based
        data['amount'] = json_data['amount']
        data['itemCount'] = json_data['itemCount']
    else:
        return {'error':'Undefined parameters'}

    data['businessId'] = session['businessId']
    response = requests.post(API_ROOT + 'functions/openTransaction', data=json.dumps(data), headers=API_HEADERS, verify=False)

    json_data = json.loads(response.text)
    if ('result' in json_data) and ('objectId' in json_data['result']):
        transactionId = json_data['result']['objectId']
        writeToNFC(transactionId)
        return {'result':'Success', 'transactionId':transactionId}
    else:
        return json_data


@app.route('/openRedeemTransaction', methods=['POST'])
def openRedeemTransaction():
    if not ('businessId' in session):
        return {'error':'No business logged in'}

    json_data = request.get_json(silent=True)
    data = {}
    if 'points' in json_data:
        # inventory based
        data['points'] = json_data['points']
    else:
        return {'error':'Undefined parameters'}

    data['businessId'] = session['businessId']
    response = requests.post(API_ROOT + 'functions/openRedeemTransaction', data=json.dumps(data), headers=API_HEADERS, verify=False)

    json_data = json.loads(response.text)
    if ('result' in json_data) and ('objectId' in json_data['result']):
        transactionId = json_data['result']['objectId']
        writeToNFC(transactionId)
        return {'result':'Success', 'transactionId':transactionId}
    else:
        return json_data

if __name__ == "__main__":
    app.run()
