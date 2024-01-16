# import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt

REQUESTS_TOPICS = "parking/requests"
CLIENT_TOPIC_URI = "parking/client/"
broker = "localhost"
client = mqtt.Client()
client.connect(broker)


def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(REQUESTS_TOPICS)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    client.loop_stop()

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.loop_forever()

client.disconnect()
