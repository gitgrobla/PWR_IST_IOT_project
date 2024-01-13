import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt


broker = "10.108.33.122"
client = mqtt.Client()
client.connect(broker)