from flask import Flask, request ,jsonify
import requests
import xmltodict
import json
from datetime import datetime
import time
import pytz
from azure.iot.hub import IoTHubRegistryManager

CONNECTION_STRING = "HostName=altoiothubprod.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=QYeYx2dZK4WYhtfBePlPlJ9wcEkqREZyReaUbDmowT8="
DEVICE_ID = "lidomonitor"


app = Flask(__name__)

@app.route('/axis2/services/FIAPStorage', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("----- start -----\n")
        req = request.data
        req_dict = xmltodict.parse(req)
        mbm = req_dict["soapenv:Envelope"]["soapenv:Body"]["ns2:dataRQ"]["transport"]["body"]["pointSet"]["point"]
        #print(len(mbm))
        meter_data = []
        for point in mbm:
            m = {
                "point_id":point["@id"],
                "value_time":point["value"]["@time"],
                "value":point["value"]["#text"]
            }
            meter_data.append(m)

        t = time.time()
        d = datetime.now(pytz.timezone('Asia/Bangkok'))
        
        #Response Structure
        res = {
            "type" : "mbmmonitor",
            "timestamp": t,
            "datetime": str(d),
            "meter_data" : meter_data
        }
        print("----- Response data -----\n")
        print(res)
        print("\n----- end -----")
        
        try:
        # Create IoTHubRegistryManager
            registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

            #print ( 'Sending message: {0}'.format(i) )
            data = json.dumps(res)

            props={}
            props.update(contentType = "application/json")

            registry_manager.send_c2d_message(DEVICE_ID, data, properties=props)
            input("Press Enter to continue...\n")

        except Exception as ex:
            print ( f"Unexpected error {ex}" )
            return
        except KeyboardInterrupt:
            print ( "IoT Hub C2D Messaging service sample stopped" )

        return jsonify(res), 200
    else:
        # for test request external api
        r = requests.get('http://www.google.com')
        return r.text, 200
    
    return 'success', 200

if __name__ == '__main__':
   app.run(debug=True, port=5000)