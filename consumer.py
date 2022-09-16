import logging
from dotenv import load_dotenv
from signalwire.relay.consumer import Consumer
import os

load_dotenv()
project = os.getenv('PROJECTID')
token = os.getenv('AUTHTOKEN')


class CustomConsumer(Consumer):
    def setup(self):
        self.project = project
        self.token = token
        self.contexts = ['test']

    async def ready(self):
        print('Your consumer is ready!')

    async def on_task(self, message):
        logging.info('Handle inbound task')
        logging.info(message)
        task_action = message['action']
        task_from = message['from']
        task_to = message['to']
        if task_action == 'call':
            dial_result = await self.client.calling.dial(to_number=task_to, from_number=task_from)
            if dial_result.successful is False:
                logging.info('Outbound call not answered or failed')
                return
            call = dial_result.call
            await call.play_tts(text='Welcome to SignalWire!')
            logging.info('Hanging up...')
            await call.hangup()
        if task_action == 'message':
            result = await self.client.messaging.send(context='office', to_number=task_to, from_number=task_from,
                                                      body='We are sending this from our Relay Consumer!')


consumer = CustomConsumer()
consumer.run()
