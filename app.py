import os
import json
import requests
import urllib.parse
from datetime import date
from sqlalchemy import create_engine
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect

# Declare a flask app
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_obj = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(json_obj, indent=4))
    #first off, I need to GET the image from Netilion
    b64_creds = os.getenv('NETILION_B64_CREDS')
    api_key = os.getenv('NETILION_API_KEY')

    auth_hdr = "Basic: " + b64_creds

    asset_id = json_obj["content"]["asset"]["id"]
    value_key = json_obj["content"]["value"]["key"]
    value = json_obj["content"]["value"]["value"]
    #now we check whether the asset ID is assigned to the tag

    get_asset_instrumentations_url = 'https://api.netilion.endress.com/v1/assets/' + str(asset_id) + '/instrumentations?per_page=100'
    headers={'Accept': 'application/json', 'Api-key': api_key, 'Authorization': auth_hdr}
    get_instrumentations_response = requests.get(get_asset_instrumentations_url, headers=headers)

    if get_instrumentations_response.status_code == 204:
        json_instrumentations = get_instrumentations_response.json()
        #An asset can be assigned to multiple Tags in Netilion, so we iterate through the Tags:
        for instrumentation in json_instrumentations['instrumentations']:
            instrumentation_id = instrumentation['id']
            tagname = instrumentation['tag']
            get_instrumentations_threshold_url = 'https://api.netilion.endress.com/v1/instrumentations/'+ str(instrumentation_id) +'/thresholds'
            get_threshold_response = requests.get(get_instrumentations_threshold_url, headers=headers)
            if get_threshold_response.status_code == 204:
                json_thresholds = get_threshold_response.json()
                #There can be multiple thresholds in Netilion, so we iterate through them.
                for threshold in json_thresholds:
                    #we only want to do compare the "low" threshold in this example application, but of course we could expand this to the "high" threshold easily
                    if 'low' in threshold:
                        low_threshold_value = threshold['low'] 
                        low_threshold_key = threshold['key']
                        if low_threshold_key == value_key:
                            if value < low_threshold_value:
                                #this means that the real value is lower than the threshold of, so now we can get active :-)
                                #now check whether a message was already sent out for this tag & threshold today (remember, we don't want to cause too much spam...)
                                send_message = False
                                engine = create_engine(os.getenv('DATABASE_URL'))
                                connection = engine.connect()
                                today = str(date.today())
                                task = connection.execute('select * from instrumentation_threshold_log where instrumentation_id='+"'"+str(instrumentation_id)+"'"+'and date='+"'"+today+"'"+'and threshold='+"'"+'low'+"'")
                                connection.close()
                                for row in task:
                                    send_message = True
                                if send_message:
                                    #Let's send out the messages via Telegram!
                                    text_message = urllib.parse.quote('Tag ' + tagname + ' has reached low threshold. Contact your supplier here to re-order:')
                                    requests.get('https://api.telegram.org/bot'+ os.getenv('TELEGRAM_API_TOKEN') +'/sendMessage?chat_id=-'+ os.getenv('TELEGRAM_CHAT_ID') +'&text='+text_message)
                                    contact_info = 'phone_number=0617157575&first_name=Joe'
                                    requests.get('https://api.telegram.org/bot'+ os.getenv('TELEGRAM_API_TOKEN') +'/sendContact?chat_id=-'+ os.getenv('TELEGRAM_CHAT_ID') +'&'+contact_info)
                                    #And finally update the database with an entry
                                    connection = engine.connect()
                                    today = str(date.today())
                                    task = connection.execute('insert into instrumentation_threshold_log(instrumentation_id, date, threshold) values (' + "'" + instrumentation_id +"'"+ ',' + "'" + today +"'"+ ',' + "'" + 'low' + "'" + ');')
                                    connection.close()

                                    return jsonify({"message": "Netilion Webhooks don't actually care whether we return anything, but we will anyways because it's a good habit."})
                                       

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')