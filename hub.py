# import RPi.GPIO as GPIO
# from config import *  # pylint: disable=unused-wildcard-import
import datetime
import paho.mqtt.client as mqtt
import db as repository

REQUESTS_TOPICS = "parking/requests"
CLIENT_TOPIC_URI = "parking/client"
broker = "localhost"
client = mqtt.Client()

NO_RESULT = 1
NO_EXIT = 2
EXIT_ALREADY_SAVED = 3

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
    
    try:
        card = repository.get_card_by_rfid(_uid)
        if(card == None):
            return send_response(_id, 0)

        (card_id, card_rfid, card_blocked) = card

        if(card_blocked == 1):
            return send_response(_id,0)

        employee_id = repository.get_employee_id_by_card_id(card_id)

        if(employee_id == None):
            return send_response(_id, 0)

        (status, last_presence) = repository.get_last_employee_presences(employee_id)
        print(status, last_presence)
        if(status == NO_EXIT):
            print("ADD EXIT")
            repository.add_exit(last_presence[0], datetime.datetime.now(), _id)
        else:
            print("ADD PRESENCE")
            repository.add_presence(card_id, employee_id, datetime.datetime.now(), _id)

        send_response(_id, 1)

    except Exception as e:
        print(e)
        return send_response(_id, 0)



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
