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

# === CONNECTION ===

def connect():
    client.connect(broker)
    client.loop_start()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MY_TOPIC)

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    client.loop_stop()

# === MESSAGE HANDLING ===

# server gave a response to my request
def on_message(client, userdata, message):
    global REQ_STATUS
    if REQ_STATUS == True:
        _decoded = message.payload.decode()
        # tutaj logika reakcji na response servera
        if(_decoded == '1'):
            print('SERVER: Request accepted')
        else:
            print('SERVER: Request denied')

        REQ_STATUS = False

    
def send_message(card_id):
    global REQ_STATUS
    temp = f"{MY_ID}:{card_id}"
    client.publish(REQUESTS_TOPICS, temp)
    REQ_STATUS = True

# === MAIN ===

client.on_connect = on_connect
client.on_message = on_message
# client.on_log = on_log
client.on_disconnect = on_disconnect

connect()

while(True):
    if input() == 'cmd':
        #w tym miejscu w zasadzie musimy wpisac logike skanowania RFID
        send_message('000000000')


client.disconnect()