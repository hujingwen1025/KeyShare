from flask import *
from datetime import date
import requests
import hashlib

app = Flask(__name__)

pincheckurl = "https://example.org"
unitsecretpath = "./unitsecret.txt"

def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def post_json_request(url, json_data=None):
    session = requests.Session()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = session.post(url, headers=headers, json=json_data)
        
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        session.close()

unitsecret = read_file_to_string(unitsecretpath)

@app.route('/')
def noresponse():
    return render_template('keyshare.html')

@app.route('/keypad.html')
def keypadrender():
    return render_template('keypad.html')

@app.route('/checkpin', methods=['POST'])
def apiresponding():
    pin = request.json.get('pin')
    date = str(date.today())
    hashtext = date + unitsecret + pin
    verihash = hashlib.sha256(hashtext.encode('utf-8')).hexdigest()
    sendjson = {
        "hash": verihash,
        "pin": pin
    }
    response = post_json_request(pincheckurl, sendjson)
    #Add response handle
    return 0

if __name__ == '__main__':
    app.run(host='localhost')