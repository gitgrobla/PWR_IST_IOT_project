import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt
from mfrc522 import MFRC522
import board
import neopixel
import time
from PIL import Image, ImageOps
import lib.oled.SSD1331 as SSD1331


MY_ID = 1
REQ_STATUS = False
MY_TOPIC = f"parking/client/{MY_ID}"
REQUESTS_TOPICS = "parking/requests"
BLOCK_PERIOD = 3.0
last_response_timestamp = datetime.timestamp(datetime.now()) - BLOCK_PERIOD

# broker config

broker = "10.108.33.122"
port = 1883
client = mqtt.Client()

pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)
disp = SSD1331.SSD1331()
disp.Init()
disp.clear()

DISPLAY_SIZE = (disp.width, disp.height)

REJECTED_IMAGE = Image.open("./Images/rejected_icon.png")
ACCEPTED_IMAGE = Image.open("./Images/accepted_icon.png")
AWAITING_IMAGE = Image.open("./Images/awaiting_icon.png")


# === CONNECTION ===

def connect():
    client.connect(broker, port)
    client.loop_start()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MY_TOPIC)

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    client.loop_stop()

# === ALERTS ===

def showScreen(image):
    disp.clear()
    #image = Image.open(path)
    #draw = ImageDraw.Draw(image)
    disp.ShowImage(image,0,0)

def buzzer_state(state):
     GPIO.output(buzzerPin, not state)  # pylint: disable=no-member

def buzzer_accept():
    buzzer_state(True)
    time.sleep(1)
    buzzer_state(False)

def buzzer_reject():
    for i in range(0, 3):
        buzzer_state(True)
        time.sleep(0.25)
        buzzer_state(False)
        time.sleep(0.25)

def card_accepted_alert():
    showScreen(ACCEPTED_IMAGE)
    
    pixels.fill((0, 255, 0))
    pixels.show()
    
    buzzer_accept()

    pixels.fill((0, 0, 0))
    pixels.show()

    showScreen(AWAITING_IMAGE)

def card_rejected_alert():
    showScreen(REJECTED_IMAGE)
    
    pixels.fill((255, 0, 0))
    pixels.show()
    
    buzzer_reject()

    pixels.fill((0, 0, 0))
    pixels.show()

    showScreen(AWAITING_IMAGE)

# === MESSAGE HANDLING ===

# server gave a response to my request
def on_message(client, userdata, message):
    global REQ_STATUS
    global last_response_timestamp

    if REQ_STATUS == True:
        _decoded = message.payload.decode()
        # tutaj logika reakcji na response servera
        if(_decoded == '1'):
            print('SERVER: Request accepted')
            card_accepted_alert()
        else:
            print('SERVER: Request denied')
            card_rejected_alert()

        last_response_timestamp = datetime.timestamp(datetime.now())
        REQ_STATUS = False

    
def send_message(card_id):
    global REQ_STATUS
    temp = f"{MY_ID}:{card_id}"
    client.publish(REQUESTS_TOPICS, temp)
    REQ_STATUS = True

# === CARD SCANNING ===

def uid_to_number(uid):
    num = 0
    
    for i in range(0, len(uid)):
        num += uid[i] << (i*8)
    return num

def scanning_loop():
    MIFAREReader = MFRC522()
    global last_response_timestamp
    global REQ_STATUS

    while True:
        (status, _) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            if status == MIFAREReader.MI_OK \
                and datetime.timestamp(datetime.now()) - last_response_timestamp > BLOCK_PERIOD \
                and not REQ_STATUS:
                
                card_id = uid_to_number(uid)
                send_message(card_id)

# === MAIN ===

client.on_connect = on_connect
client.on_message = on_message
# client.on_log = on_log
client.on_disconnect = on_disconnect

def main():
    connect()
    showScreen(AWAITING_IMAGE)
    scanning_loop()

if __name__ == '__main__':
    
    try:
        main()
    finally:
        client.disconnect()
        disp.clear()
        disp.reset()
        GPIO.cleanup()

