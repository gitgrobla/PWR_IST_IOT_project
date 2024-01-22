import RPi.GPIO as GPIO
from config import *  # pylint: disable=unused-wildcard-import
from datetime import datetime
import paho.mqtt.client as mqtt
from mfrc522 import MFRC522
import board
import neopixel
import time
import db 
import lib.oled.SSD1331 as SSD1331



MY_ID = 1
REQ_STATUS = False
MY_TOPIC = f"parking/client/{MY_ID}"
REQUESTS_TOPICS = "parking/requests"
BLOCK_PERIOD = 2.0
last_response_timestamp = datetime.timestamp(datetime.now()) - BLOCK_PERIOD
broker = "10.108.33.122"
client = mqtt.Client()

pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)


# === ALERTS ===
    
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
    disp.show(ACCEPTED_IMAGE, 0, 0)
    
    pixels.fill((0, 255, 0))
    pixels.show()
    
    buzzer_accept()

    pixels.fill((0, 0, 0))
    pixels.show()

    disp.show(AWAITING_IMAGE, 0, 0)

def card_rejected_alert():
    disp.show(REJECTED_IMAGE, 0, 0)
    
    pixels.fill((255, 0, 0))
    pixels.show()
    
    buzzer_reject()

    pixels.fill((0, 0, 0))
    pixels.show()

    disp.show(AWAITING_IMAGE, 0, 0)


# === CARD SCANNING ===

def uid_to_number(uid):
    num = 0
    
    for i in range(0, len(uid)):
        num += uid[i] << (i*8)
    return num

def scanning_loop():
    MIFAREReader = MFRC522()

    while True:
        (status, _) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status == MIFAREReader.MI_OK:
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            if status == MIFAREReader.MI_OK \
                and datetime.timestamp(datetime.now()) - last_response_timestamp > BLOCK_PERIOD \
                and not REQ_STATUS:
                
                card_id = uid_to_number(uid)
                return card_id





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






# ==== TUI =====

def tui():

    option = -1

    while(option != 0):

        print("0 - exit")
        print("1 - add card to employee")
        print("2 - add employee")
        print("3 - block cart")
        print("4 - block cart employee")
        print("5 - unlock cart")
        print("6 - unlock cart employee")

        try:
            option = int(input(">"))
        except ValueError:
            print("Error input")
            continue

        if(option == 1):
            tui_add_card_employee()
        elif(option == 2):
            tui_add_employee()
        elif(option == 3):
            tui_block_cart()
        elif(option == 4):
            tui_block_card_employee()
        elif(option == 5):
            print(option)
        elif(option == 6):
            print(option) #TODO


def get_name_and_lastname():
        while(name != null and lastName != null):
            try:
                name = input("Name: ")
                lastName = input("Lastname:")
            except ValueError:
                print("Error input")
                continue
            
        return name,lastName

def tui_add_employee():

    nameAndLastname = get_name_and_lastname()
    
    if(add_employee(nameAndLastname[0] , nameAndLastname[1])):
        print("Added")
    else:
        print("Database error")


def tui_add_card_employee():

    nameAndLastname = get_name_and_lastname()

    employeeList = get_employee_id(nameAndLastname[0] , nameAndLastname[1])

    if(len(employeeList) == 0):
        print("Wrong name and lastname")
    elif (len(employeeList) > 1):

        for employee in employeeList:
            print(f"ID: {pracownik[0]}, Name: {pracownik[1]}, Lastname: {pracownik[2]}")
        
        selectedId = int(input("Enter the employee ID to choose: "))

        for employee in employeeList:
            if employee[0] == selectedId:
                employeeId = employee[0]
                break
        
        
    else:
        employeeId = employeeList[0][0]

    if(employeeId != null):
        cardId = scanning_loop()
        
        if(add_employee_card(cardId,employeeId)):
            print("Added")
        else:
            print("Error database")
    else:
        print("Wrong name and lastname or ID")


def tui_block_cart():

    cardId = scanning_loop()
    
    if(block_card(cardId)):
        print("Blocked")
    else:
        print("Database error")



def tui_block_card_employee():

    nameAndLastname = get_name_and_lastname()

    employeeList = get_employee_id(nameAndLastname[0] , nameAndLastname[1])

    if(len(employeeList) == 0):
        print("Wrong name and lastname")
    elif (len(employeeList) > 1):

        for employee in employeeList:
            print(f"ID: {pracownik[0]}, Name: {pracownik[1]}, Lastname: {pracownik[2]}")
        
        selectedId = int(input("Enter the employee ID to choose: "))

        for employee in employeeList:
            if employee[0] == selectedId:
                employeeId = employee[0]
                break
        
        
    else:
        employeeId = employeeList[0][0]

    if(employeeId != null):
        if():#TODO
            print("Blocked")
        else:
            print("Database error")
    else:
        print("Wrong name and lastname or ID")



def tui_unlock_cart():

    cardId = scanning_loop()
    
    if(unlock_card(cardId)):
        print("Unlocked")
    else:
        print("Database error")


        


    



def main():
    scanning_loop()

if __name__ == '__main__':
    
    try:
        main()
    except:
        pass