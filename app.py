
from flask import Flask, session, redirect, url_for, escape, request # Flask
import subprocess
import json, requests, urllib, urllib3 # Parse Server
from threading import Timer

API_ROOT = 'https://nathantannar.me/api/prod'
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

def getBusinessId():
    with open("businessId.txt", "r") as f:
        f.seek(0) #ensure you're at the start of the file..
        first_char = f.read(1) #get the first character
        if not first_char:
            # File empty
            return None
        else:
            f.seek(0) #first character wasn't empty, return to start of file
            businessId = f.read()
            f.close()
            return businessId
    return None
        

def popBusinessId():
    session.pop('businessId', None)
    f = open("businessId.txt", "w")
    f.write('')
    f.close()

def recoverSession():
    # Recover Session
    businessId = getBusinessId()
    if businessId is None:
        session.pop('businessId', None)
    else:
        session['businessId'] = businessId
    return

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.before_first_request
def startup():
    urllib3.disable_warnings()
    recoverSession()
    startNFC()

@app.route('/')
def index():
    businessId = getBusinessId()
    if businessId is None:
        return redirect(url_for('login'))
    else:
        return 'Logged in with businessId: %s' % escape(businessId)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        params = urllib.parse.urlencode({'username': username, 'password': password})
        url = API_ROOT + ('/login?%s' % params)
        response = requests.get(url, headers=API_HEADERS, verify=False)
        
        if response.ok:
            json_data = json.loads(response.text)
            if 'business' in json_data:
                id = json_data['business']['objectId']
                setBusinessId(id)
                return redirect(url_for('index'))
            else:
                return response.text
        else:
            return response.text
        
    elif request.method == 'GET':
        return '''
            <form method="post">
                <h1>Login</h1>
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

@app.route('/openTransaction', methods=['GET', 'POST'])
def openTransaction():

    businessId = getBusinessId()

    if businessId is None:
        return {'error':'No business logged in'}

    if request.method == 'POST':

        if 'amount' in request.form:
            if not ('itemCount' in request.form):
                return {'error':'"itemCount" Not specified'}
            data = {'amount': float(request.form['amount']), 'itemCount': int(request.form['itemCount']), 'businessId': businessId}

        else:
            post_json = request.get_json(force=True)
            if not ('amount' in post_json):
                return {'error':'"amount" Not specified'}
            if not ('itemCount' in post_json):
                return {'error':'"itemCount" Not specified'}
            data = {'amount': post_json['amount'], 'itemCount': post_json['itemCount'], 'businessId': businessId}
            if 'items' in post_json:
                data['items'] = post_json['items']
        
        
        url = API_ROOT + '/functions/openTransaction'
        response = requests.post(url,data=json.dumps(data), headers=API_HEADERS, verify=False)
        
        if response.ok:
            json_data = json.loads(response.text)

            if 'result' in json_data:
                if 'objectId' in json_data['result']:
                    transactionId = json_data['result']['objectId']
                    writeToNFC(transactionId)
                    return response.text
                    
            return response.text
        else:
            return response.text

    elif request.method == 'GET':  

        return '''
            <form method="post">
                <h1>Open Transaction</h1>
                <p><input type=number step=0.01 name=amount placeholder=Amount>
                <p><input type=number name=itemCount placeholder=Count>
                <p><input type=submit value=Open>
            </form>
        '''

@app.route('/openRedeemTransaction', methods=['GET', 'POST'])
def openRedeemTransaction():

    businessId = getBusinessId()

    if businessId is None:
        return {'error':'No business logged in'}

    if request.method == 'POST':

        if 'points' in request.form:
          data = {'points': float(request.form['points']), 'businessId': businessId}
        else:
            post_json = request.get_json(force=True)
            if not ('points' in post_json):
                return {'error':'"points" Not specified'}
            data = {'points': post_json['points'], 'businessId': businessId}
        
        url = API_ROOT + '/functions/openRedeemTransaction'
        response = requests.post(url,data=json.dumps(data), headers=API_HEADERS, verify=False)
        
        if response.ok:
            json_data = json.loads(response.text)

            if 'result' in json_data:
                if 'objectId' in json_data['result']:
                    transactionId = json_data['result']['objectId']
                    writeToNFC(transactionId)
                    return response.text
                    
            return response.text
        else:
            return response.text

    elif request.method == 'GET':
    
        return '''
            <form method="post">
                <h1>Open Redeem Transaction</h1>
                <p><input type=number step=0.01 name=points placeholder=Points>
                <p><input type=submit value=Open>
            </form>
        '''
    

if __name__ == "__main__":
    app.run()
