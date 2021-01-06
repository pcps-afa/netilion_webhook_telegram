import os
import json
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect

# Declare a flask app
app = Flask(__name__)

@app.route('/newvalue', methods=['POST'])
def newvalue():
    json_obj = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(json_obj, indent=4))
    #first off, I need to GET the image from Netilion
    b64_creds = os.getevn('NETILION_B64_CREDS')
    api_key = os.getevn('NETILION_API_KEY')

    auth_hdr = "Basic: " + b64_creds

    asset_id = json_obj["content"]["asset"]["id"]
    value 
    #now we check whether the asset ID is assigned to the tag

    get_asset_instrumentations_url = 'https://api.netilion.endress.com/v1/assets/' + str(asset_id) + '/instrumentations?per_page=100'
    headers={'Accept': 'application/json', 'Api-key': api_key, 'Authorization': auth_hdr}
    get_instrumentations_response = requests.get(get_asset_instrumentations_url, headers=headers)

    if get_instrumentations_response.status == 204:
        json_instrumentations = get_instrumentations_response.json()
        print("Request:")
        print(json.dumps(req, indent=4))
        #if json_instrumentations['instrumentations'] != []:
            #if yes, then we check each tag for thresholds & compare the value to it
        for instrumentation in json_instrumentations['instrumentations']:
            instrumentation_id = json_instrumentations['instrumentations']['id']
            get_instrumentations_threshold_url = 'https://api.netilion.endress.com/v1/instrumentations/'+ str(instrumentation_id) +'/thresholds'
            get_threshold_response = requests.get(get_instrumentations_threshold_url, headers=headers)
            if get_threshold_response.status == 204:
                json_thresholds = get_threshold_response.json()
                for threshold in json_thresholds:
                    #we only want to do compare the "low" threshold in this example application, but of course we could expand this to the "high" threshold easily
                    if 'low' in threshold:
                        low_threshold_value = threshold['low'] 
                        low_threshold_key = threshold['key']
                        #if low_threshold_key = 


        #if yes, then we check each tag for thresholds & compare the value to it
            #if threshold is exceeded,then check whether a message was already sent out for this tag & threshold today
                #if not, then send out the message to Telegram and update the database with an entry to stop any future spam


    
    return jsonify({"message": "Netilion Webhooks don't actually care whether we return anything, but we will anyways because it's a good habit."})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')