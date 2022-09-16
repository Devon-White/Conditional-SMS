import os
from dotenv import load_dotenv
from pyngrok import ngrok
from signalwire.messaging_response import MessagingResponse
from flask import Flask, request
from signalwire.rest import Client as signalwire_client
from signalwire.relay.task import Task

load_dotenv()
project = os.getenv('PROJECTID')
token = os.getenv('AUTHTOKEN')

task = Task(project=project, token=token)
client = signalwire_client(os.getenv('PROJECTID'), os.getenv('AUTHTOKEN'), signalwire_space_url=os.getenv('SPACEURL'))


app = Flask(__name__)


@app.route("/sms_app", methods=['GET', 'POST'])
def sms_app():
    our_num = request.values.get('To')
    cus_num = request.values.get('From')
    body = request.values.get('Body', None)
    resp = MessagingResponse()
    data = {
        'action': 'message',
        'from': our_num,
        'to': cus_num,
    }
    if body.lower() == 'y':
        resp.message("HTTP SMS test")
    elif body.lower() == 'n':
        success = task.deliver('test', data)
        if success:
            print('Task Delivered')
        else:
            print('Task Not delivered')

    else:
        resp.message(f'Would you like to test a SMS?\nRespond with Y for HTTP Respond with N for Relay)')
    return str(resp)


def start_ngrok():
    url = ngrok.connect(5000).public_url
    print(' * Tunnel URL:', url)
    client.incoming_phone_numbers.list(
        phone_number=os.getenv('SW_PHONE_NUMBER'))[0].update(
        sms_url=url + '/sms_app')


if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        start_ngrok()
    app.run(debug=True)
