from flask import *
import datetime
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
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=json_data)
        
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return 'error'
    
def generatehash(json):
    date = str(datetime.date.today())
    hashtext = date + unitsecret + str(json)
    verihash = hashlib.sha256(hashtext.encode('utf-8')).hexdigest()

    return verihash

unitsecret = read_file_to_string(unitsecretpath)

@app.route('/')
def noresponse():
    return render_template('keyshare.html')

@app.route('/keypad')
def keypadrender():
    return render_template('keypad.html')

@app.route('/authid', methods=['POST'])
def authid():
    authmethod = request.json.get('authmethod')

    if authmethod == "pin":

        pin = request.json.get('pin')

        sendjson = {
            "pin": pin
        }

        date = str(datetime.date.today())
        hashtext = date + unitsecret + str(sendjson)
        verihash = hashlib.sha256(hashtext.encode('utf-8')).hexdigest()

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)

        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

            username = response["username"]
            userid = response["userid"]
            borrowinfo = response["borrowinfo"]
            retinfo["userid"] = userid
            retinfo["user"] = username
            retinfo["borrowinfo"] = borrowinfo

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)

    elif authmethod == "card":

        cardid = request.json.get('cardid')

        sendjson = {
            "cardid": cardid
        }

        date = str(datetime.date.today())
        hashtext = date + unitsecret + str(sendjson)
        verihash = hashlib.sha256(hashtext.encode('utf-8')).hexdigest()

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)

        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

            username = response["username"]
            userid = response["userid"]
            borrowinfo = response["borrowinfo"]
            retinfo["userid"] = userid
            retinfo["user"] = username
            retinfo["borrowinfo"] = borrowinfo

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)

@app.route('/checkadminpin', methods=['POST'])
def checkadminpin():
    pin = request.json.get('pin')

    sendjson = {
        "pin": pin
    }

    verihash = generatehash(sendjson)

    sendjson["hash"] = verihash

    response = post_json_request(pincheckurl, sendjson)

    if response == "error":
        retinfo = {
            "status": "transmiterr"
        }
        print("Transmit error")
        return jsonify(retinfo)
    
    response_status = response["status"]
    retinfo = {}

    if response_status == "ok":

        retinfo["status"] = "ok"
    
    elif response_status == "hasherr":

        print("Hash error")
        retinfo["status"] = "hasherr"
    
    elif response_status == "err":

        retinfo["status"] = "err"

        errinfo = response["errinfo"]
        retinfo["errinfo"] = errinfo
    
    else:

        retinfo["status"] = "unknownerr"

    return jsonify(retinfo)

@app.route('/cardregister', methods=['POST'])
def cardregister():
    operation = request.json.get("operation")

    sendjson = {
        "operation": operation
    }

    if operation == "checkpin":
        registerpin = request.json.get('pin')

        sendjson["pin"] = registerpin

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"
            username = response["username"]
            userid = response["userid"]
            retinfo["userid"] = userid
            retinfo["user"] = username

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)

    elif operation == "registercard":
        cardid = request.json.get('cardid')

        sendjson["cardid"] = registerpin

        sendjson["userid"] = cardid

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)
    
    else:
        retinfo = {}

        retinfo["status"] = "operror"

        return jsonify(retinfo)
    
@app.route('/updateitemstatus', methods=['POST'])
def updateitemstatus():
    operation = request.json.get("operation")

    sendjson = {
        "operation": operation
    }

    if operation == "borrow":
        itemtype = request.json.get('itemtype')

        userid = request.json.get('userid')

        sendjson["itemtype"] = itemtype

        sendjson["userid"] = userid

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"
            retinfo["storageid"] = response["storageid"]

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)

    elif operation == "returnverify":
        itemid = request.json.get('itemid')

        sendjson["itemid"] = itemid

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            print("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

        elif response_status == "hasherr":

            print("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)
    
    elif operation == "return":
        itemid = request.json.get('itemid')

        sendjson["itemid"] = itemid

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

    else:
        retinfo = {}

        retinfo["status"] = "operror"

        return jsonify(retinfo)

@app.route('/borrowchoice')
def borrowchoice():
    return render_template('borrowchoice.html')

if __name__ == '__main__':
    app.run(host='localhost')