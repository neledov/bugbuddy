
from itty import *
import urllib2
import json
import requests
import re

bot_email = "bugbuddy@spark.io"
bot_name = "bug buddy"
bearer = ''

previous_msg = ''

def sendSparkGET(url):

    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data):

    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

@post('/sparkwebhook')
def index(request):
    global previous_msg
    webhook = json.loads(request.body)
    print webhook['data']['personEmail']
    print webhook['data']['id']
    print webhook['data']['roomId']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)

    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        print 'MESSAGE RECIEVED'
        if '/getbug' in in_message:
            in_message = in_message.replace('/getbug ','')
            in_message = re.sub(r'[\"\'\/]', " ", in_message)
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": "Collecting information, this may take a few moments - please wait..."})
            msg = requests.get('http://18.195.157.34:5000/bug/description_text='+ in_message).text
            msg = msg.strip('"')
            msg = msg.strip('[')
            msg = msg.replace("'", '')
            msg = msg.strip(']')

            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "markdown": msg})
            print 'MSG SENT'
    return "true"

run_itty(server='wsgiref', host='0.0.0.0', port=10010)