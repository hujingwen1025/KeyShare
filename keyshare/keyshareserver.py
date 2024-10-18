from flask import *
import tkinter as tk
from flask_socketio import SocketIO, emit
import datetime
import requests
import hashlib
import threading
import openpyxl
import time

app = Flask(__name__)

socketio = SocketIO(app)

pincheckurl = "https://example.org"
unitsecretpath = "./unitsecret.txt"
eotablepath = "./eo.xlsx"
debug = True

def dprint(text):
    if debug:
        print(text)

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
        dprint(f"An error occurred: {e}")
        return 'error'
    
def generatehash(json):
    date = str(datetime.date.today())
    hashtext = date + unitsecret + str(json)
    verihash = hashlib.sha256(hashtext.encode('utf-8')).hexdigest()

    return verihash

def nfcInput():
    def clear_textbox():
        content = text_area.get('1.0', tk.END)
        content = content.replace('\n', '')
        nfccontent = content
        dprint('nfccontent is now: ' + nfccontent)
        socketio.emit('contentupdate', nfccontent)
        text_area.delete('1.0', tk.END)

    root = tk.Tk()
    root.title("KEYSHARE NFC INPUT")
    root.geometry("250x50")

    text_area = tk.Text(root, height=10, width=40)
    text_area.pack(padx=10, pady=10)

    def on_enter_press(event):
        clear_textbox()

    text_area.bind("<Return>", on_enter_press)

    root.mainloop()

def searchEO():
    for i in range(eoindex):
        if eocell(row = (i+1), column = 3) == 'e':
            return eocell(row = (i+1), column=1)
    return None

def registerreturn(returnslot, itemid, disabled):
    sendjson = {
        "storageid": returnslot,
        "itemid": itemid,
        "disabled": disabled
    }

    verihash = generatehash(sendjson)

    sendjson["hash"] = verihash

    response = post_json_request(pincheckurl, sendjson)

    response_status = response["status"]

    if response_status == "ok":
        return True
    else:
        return False
    
def openslot(storageid):
    pass

def runMainApp():
    socketio.run(app, port=5000)

unitsecret = read_file_to_string(unitsecretpath)

eoworkbook = openpyxl.load_workbook(eotablepath)
eosheet = eoworkbook.active
eocell = eosheet.cell
eoindex = eocell(row=1, column=1)

@app.route('/')
def keyshare():
    return render_template('keyshare.html')

@app.route('/keypad')
def keypadrender():
    return render_template('keypad.html')

@app.route('/auth', methods=['POST'])
def auth():
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
            dprint("Transmit error")
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

            dprint("Hash error")
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
            dprint("Transmit error")
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

            dprint("Hash error")
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
        dprint("Transmit error")
        return jsonify(retinfo)
    
    response_status = response["status"]
    retinfo = {}

    if response_status == "ok":

        retinfo["status"] = "ok"
    
    elif response_status == "hasherr":

        dprint("Hash error")
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
            dprint("Transmit error")
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

            dprint("Hash error")
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
            dprint("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

        elif response_status == "hasherr":

            dprint("Hash error")
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
            dprint("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"
            retinfo["storageid"] = response["storageid"]

        elif response_status == "hasherr":

            dprint("Hash error")
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
            dprint("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

        elif response_status == "hasherr":

            dprint("Hash error")
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

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            dprint("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

            returnslot = searchEO()

            if returnslot == None:
                retinfo["status"] = "full"
            else:
                returned = registerreturn(returnslot, itemid, "false")
                if returned:
                    openslot(returnslot)
                else:
                    retinfo["status"] = "notapproved"

        elif response_status == "hasherr":

            dprint("Hash error")
            retinfo["status"] = "hasherr"

        elif response_status == "err":

            retinfo["status"] = "err"

            errinfo = response["errinfo"]
            retinfo["errinfo"] = errinfo

        else:

            retinfo["status"] = "unknownerr"

        return jsonify(retinfo)

    elif operation == "report":
        itemid = request.json.get('itemid')

        sendjson["itemid"] = itemid

        verihash = generatehash(sendjson)

        sendjson["hash"] = verihash

        response = post_json_request(pincheckurl, sendjson)

        if response == "error":
            retinfo = {
                "status": "transmiterr"
            }
            dprint("Transmit error")
            return jsonify(retinfo)
        
        response_status = response["status"]
        retinfo = {}

        if response_status == "ok":

            retinfo["status"] = "ok"

            returnslot = searchEO()

            if returnslot == None:
                retinfo["status"] = "full"
            else:
                returned = registerreturn(returnslot, itemid, 'true')
                if returned:
                    openslot(returnslot)
                else:
                    retinfo["status"] = "notapproved"

        elif response_status == "hasherr":

            dprint("Hash error")
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
    
@app.route('/checkitem', methods=['POST'])
def checkItem():
    itemid = request.json.get('itemid')

    sendjson = {
        "itemid": itemid
    }

    verihash = generatehash(sendjson)

    sendjson["hash"] = verihash

    response = post_json_request(pincheckurl, sendjson)

    if response == "error":
        retinfo = {
            "status": "transmiterr"
        }
        dprint("Transmit error")
        return jsonify(retinfo)
    
    response_status = response["status"]
    retinfo = {}

    if response_status == "ok":

        retinfo["status"] = "ok"
    
    elif response_status == "hasherr":

        dprint("Hash error")
        retinfo["status"] = "hasherr"
    
    elif response_status == "err":

        retinfo["status"] = "err"

        errinfo = response["errinfo"]
        retinfo["errinfo"] = errinfo
    
    else:

        retinfo["status"] = "unknownerr"

    return jsonify(retinfo) 

@app.route('/borrowchoice')
def borrowchoice():
    return render_template('borrowchoice.html')

@socketio.on('connect')
def socketconnect():
    emit('connection', {'data': 'ok'})

if __name__ == '__main__':
    appThread = threading.Thread(target=runMainApp)

    appThread.start()
    nfcInput()