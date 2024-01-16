# import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt

MY_ID = 1
REQ_STATUS = False
MY_TOPIC = f"parking/client/{MY_ID}"
REQUESTS_TOPICS = "parking/requests"
broker = "localhost"
client = mqtt.Client()

def connect():
    client.connect(broker)
    client.loop_start()

# server gave a response to my request
def on_message(client, userdata, message):
    global REQ_STATUS
    if REQ_STATUS:
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")
        REQ_STATUS = False

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MY_TOPIC)

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    client.loop_stop()

client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.on_disconnect = on_disconnect

connect()

def send_message(card_id):
    temp = f"{MY_ID}:{card_id}"
    client.publish(REQUESTS_TOPICS, card_id)
    REQ_STATUS = True

while(True):
    if input() == 'cmd':
        send_message('000000000')


client.disconnect()