# import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt
import db as repository

REQUESTS_TOPICS = "parking/requests"
CLIENT_TOPIC_URI = "parking/client"
broker = "localhost"
client = mqtt.Client()

# === CONNECTION ===

def connect():
    client.connect(broker)
    client.loop_start()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(REQUESTS_TOPICS)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    client.loop_stop()

# === MESSAGE HANDLING ===

def on_message(client, userdata, message):
    _decoded = message.payload.decode()
    _split = _decoded.split(":")
    if(len(_split) != 2):
        print("SERVER: Received malformed message")
        return
    _id = _split[0]
    _uid = _split[1]
    print(f"SERVER: Received message '{message.payload.decode()}' on topic '{message.topic}'")
    
   

    send_response(_id, 1)

def send_response(id, status):
    print('SERVER: Sending response to client')
    client.publish(f'{CLIENT_TOPIC_URI}/{id}', status)


# === MAIN ===

connect()

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

while True:
    a = 1

client.disconnect()
