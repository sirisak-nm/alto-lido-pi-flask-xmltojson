from flask import Flask, request
import requests
import xmltodict, json

app = Flask(__name__)

@app.route('/axis2/services/FIAPStorage', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        a =  request.content_type
        b = request.data
        obj = xmltodict.parse(b)
        objson = json.dumps(obj)
        print(a)
        print("\n")
        print(objson)
        print("\n")
        print(request.headers)
        return objson
    else:
        # for test request external api
        r = requests.get('http://www.google.com')
        return r.text

if __name__ == '__main__':
   app.run(debug=True, port=5000)