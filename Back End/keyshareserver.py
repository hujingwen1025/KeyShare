from flask import *
from flask_socketio import SocketIO, emit
import mysql.connector
import datetime

import hashlib
import threading
import time
import json

app = Flask(__name__)

keysharedb = mysql.connector.connect(
    host="localhost",
    user="user",
    password="10252009",
    autocommit = True,
    database="KeyShare"
)

spamwait = 2

dbcursor = keysharedb.cursor()

debug = True

def dprint(text):
    if debug:
        print(text)

def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def antiSpamWait():
    time.sleep(spamwait)

borrowitems = json.loads(read_file_to_string('./borrowitems.txt'))

@app.route('/auth', methods=['POST'])
def auth():
    antiSpamWait()

    authmethod = request.json.get('authmethod')

    retinfo = {}

    if authmethod == "pin":
        pin = request.json.get('pin')
        pin = str(int(pin))
        dbcursor.execute("SELECT userid, username, borrowdisabled FROM users WHERE authpin = " + pin)

        dbcursorfetch = dbcursor.fetchall()

        if len(dbcursorfetch) < 1:
            retinfo['status'] = 'err'
            retinfo['errinfo'] = 'No user associated with entered PIN'
            return jsonify(retinfo)

        userinfo = dbcursorfetch[0]
        retinfo['status'] = 'ok'
        retinfo['userid'] = userinfo[0]
        retinfo['username'] = userinfo[1]
        if userinfo[2] == None:
            retinfo['borrowinfo'] = str(borrowitems)
        else:
            disableditems = userinfo[2].split()
            borrowinfo = borrowitems
            for popitem in disableditems:
                borrowinfo.popitem(popitem)
            retinfo['borrowinfo'] = borrowinfo

        return jsonify(retinfo)
    elif authmethod == "card":
        cardid = request.json.get('cardid')
        cardid = str(int(cardid))
        dbcursor.execute("SELECT userid, username, borrowdisabled FROM users WHERE authcardid = " + cardid)

        dbcursorfetch = dbcursor.fetchall()

        if len(dbcursorfetch) < 1:
            retinfo['status'] = 'err'
            retinfo['errinfo'] = 'No user associated with entered PIN'
            return jsonify(retinfo)

        userinfo = dbcursorfetch[0]
        retinfo['status'] = 'ok'
        retinfo['userid'] = userinfo[0]
        retinfo['username'] = userinfo[1]
        if userinfo[2] == None:
            retinfo['borrowinfo'] = str(borrowitems)
        else:
            disableditems = userinfo[2].split()
            borrowinfo = borrowitems
            for popitem in disableditems:
                borrowinfo.popitem(popitem)
            retinfo['borrowinfo'] = borrowinfo

        return jsonify(retinfo)
    else:
        retinfo['status'] = 'err'
        retinfo["errinfo"] = 'authmethod incorrect'

@app.route('/updateitemstatus', methods=['POST'])
def updateitemstatus():
    antiSpamWait()

    operation = request.json.get("operation")

    retinfo = {}

    dprint(operation)

    if operation == "borrow":
        userid = request.json.get('userid')
        userid = str(int(userid))
        unitid = request.json.get('unitid')
        unitid = str(int(unitid))
        itemtype = request.json.get('itemtype')
        itemtype = str(itemtype)

        dbcursor.execute(f"SELECT itemid FROM items WHERE borrowed = FALSE AND disabled = FALSE AND itemtype = '{itemtype}' AND unitid = '{unitid}'")

        allitemid = dbcursor.fetchall()

        if len(allitemid) < 1:
            retinfo['status'] = 'err'
            retinfo['errinfo'] = 'No requested item at station'
            return jsonify(retinfo)

        selecteditemid = allitemid[0][0]
        selecteditemid = str(selecteditemid)

        dbcursor.execute(f"SELECT storageid FROM items WHERE itemid = {selecteditemid}")

        selectedstorageid = str(dbcursor.fetchall()[0][0])

        dbcursor.execute(f"UPDATE items SET borrowed = TRUE, storageid = NULL, unitid = NULL, borrowedtime = CURRENT_TIMESTAMP, borroweduser = '{userid}' WHERE itemid = {selecteditemid}")

        retinfo['status'] = 'ok'
        retinfo['storageid'] = selectedstorageid

        return jsonify(retinfo)

    elif operation == "returnverify":
        itemnfc = request.json.get("itemnfc")
        itemnfc = str(itemnfc)

        dbcursor.execute(f"SELECT borroweduser, itemid, itemtype FROM items WHERE borrowed = TRUE AND itemnfc = '{itemnfc}'")

        selectediteminfo = dbcursor.fetchall()

        if len(selectediteminfo) < 1:
            retinfo["status"] = 'err'
            retinfo["errinfo"] = "Item or user not registered in borrowed list"

            return jsonify(retinfo)
        
        borroweduserid = selectediteminfo[0][0]
        borroweduserid = str(borroweduserid)

        borroweditemid = selectediteminfo[0][1]
        borroweditemid = str(borroweditemid)

        borroweditemtype = selectediteminfo[0][2]
        borroweditemtype = str(borroweditemtype)

        dbcursor.execute(f"SELECT username FROM users WHERE userid = {borroweduserid}")

        selectedusername = dbcursor.fetchall()

        if len(selectedusername) < 1:
            retinfo["status"] = 'err'
            retinfo["errinfo"] = "Item was found in database but user is invalid"

            return jsonify(retinfo)

        borrowedusername = selectedusername[0][0]
        borrowedusername = str(borrowedusername)

        retinfo["status"] = "ok"
        retinfo["userid"] = borroweduserid
        retinfo["username"] = borrowedusername
        retinfo["itemid"] = borroweditemid
        retinfo["itemtype"] = borroweditemtype

        return jsonify(retinfo)

    elif operation == "return":
        storageid = request.json.get('storageid')
        itemid = request.json.get('itemid')
        disabled = request.json.get('disabled')
        unitid = request.json.get('unitid')
        
        unitid = str(int(unitid))
        storageid = str(storageid)
        itemid = str(int(itemid))

        if disabled == 'true':
            disabled = 'TRUE'
        else:
            disabled = 'FALSE'

        retinfo = {}

        dbcursor.execute(f"UPDATE items SET borroweduser = NULL, borrowedtime = NULL, borrowed = FALSE, unitid = '{unitid}', storageid = '{storageid}', disabled = {disabled} WHERE itemid = {itemid}")
        
        retinfo["status"] = "ok"

        return jsonify(retinfo)

if __name__ == '__main__':
    app.run(host='localhost', port=7000)