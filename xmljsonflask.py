from flask import Flask, request ,jsonify
import requests
import xmltodict
import json
from datetime import datetime
import time
import pytz
from azure.iot.hub import IoTHubRegistryManager

CONNECTION_STRING = "altolido.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=hb9hjoQJSbSfBTbyCFEmiB+J6/zp2Aht0/t1eWInuQ0="
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
            "device_id":"mbm1_id",
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
            print("----- start -----\n")
            print("----- set parameter for connect to cosmosDB -----\n")
            registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

            #print ( 'Sending message: {0}'.format(i) )
            data = json.dumps(res)

            props={}
            props.update(contentType = "application/json")

            print("----- save data to cosmosDB -----\n")

            registry_manager.send_c2d_message(DEVICE_ID, data, properties=props)
            #input("Press Enter to continue...\n")
            print("----- end -----\n")

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