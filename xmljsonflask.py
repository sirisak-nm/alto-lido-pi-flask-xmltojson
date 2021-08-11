from flask import Flask, request ,jsonify
import requests
import xmltodict
import json
from datetime import datetime
import time
import pytz
#from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import IoTHubDeviceClient
'''
from azure.iot.device import IoTHubDeviceClient


CONNECTION_STRING = "HostName=altolido.azure-devices.net;DeviceId=altolido_flask;SharedAccessKey=+4mufV2azfRfCGtrJc43/dtzcn/zCuR7yvfFceBLpKA="
device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

device_client.connect()

message_temp = {
 "xx": "yy"
}
msg = json.dumps(message_temp)

device_client.send_message(msg)
'''

#CONNECTION_STRING = "HostName=altoiothubprod.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=QYeYx2dZK4WYhtfBePlPlJ9wcEkqREZyReaUbDmowT8="
#DEVICE_ID = "lidomonitor"
CONNECTION_STRING = "HostName=altolido.azure-devices.net;DeviceId=altolido_flask;SharedAccessKey=+4mufV2azfRfCGtrJc43/dtzcn/zCuR7yvfFceBLpKA="
device_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)


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
            "meter_data" : meter_data,
            "gatewayid":"altolido_flask"
        }
        print("----- Response data -----\n")
        print(res)
        print("\n----- end -----")
        
        try:
        # Create IoTHubRegistryManager
            print("----- start -----\n")
            print("----- set parameter for connect to cosmosDB -----\n")
            
            #registry_manager = IoTHubRegistryManager(CONNECTION_STRING)

            #print ( 'Sending message: {0}'.format(i) )
            device_client.connect()
            data = json.dumps(res)

            #props={}
            #props.update(contentType = "application/json")

            print("----- save data to cosmosDB -----\n")
            device_client.send_message(data)

            #registry_manager.send_c2d_message(DEVICE_ID, data, properties=props)
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