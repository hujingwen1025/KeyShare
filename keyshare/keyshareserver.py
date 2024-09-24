from flask import *

app = Flask(__name__)

@app.route('/')
def noresponse():
    return render_template('keyshare.html')

@app.route('/keypad.html')
def keypadrender():
    return render_template('keypad.html')

if __name__ == '__main__':
    app.run(host='localhost')