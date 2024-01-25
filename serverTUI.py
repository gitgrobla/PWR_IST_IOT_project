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

from typing import Dict, Tuple, Optional, List

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
                buzzer_accept()
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
        print("3 - block card")
        print("4 - block card employee")
        print("5 - unlock card employee")
        print("6 - raport")

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
            tui_block_card()

        elif(option == 4):
            tui_block_card_employee()

        elif(option == 5):
            tui_unlock_card_employee()

        elif(option == 6):
            raport()


def raport():

    raport = db.get_all_employees_work_registers(datetime(2000,1,1))

    print_work_registers(raport)



def print_work_registers(work_registers: Dict[int, db.WorkRegister]):
    for employee_id, work_register in work_registers.items():
        print(f"Employee ID: {employee_id}")
        print(f"Number of Entries: {work_register.entries_num}")
        print(f"Number of Exits: {work_register.exits_num}")
        print(f"Total Work Hours: {work_register.work_hours}")
        print("\n") 


def get_name_and_lastname():
    name = ""
    lastName = ""

    while(name == "" or lastName == ""):
        try:
            name = input("Name: ")
            lastName = input("Lastname:")
        except ValueError:
            print("Error input")
            continue
        
    return name,lastName

def tui_add_employee():

    nameAndLastname = get_name_and_lastname()
    
    if(db.add_employee(nameAndLastname[0] , nameAndLastname[1])):
        print("Added")
    else:
        print("Database error")


def tui_add_card_employee():

    nameAndLastname = get_name_and_lastname()

    employeeList = db.get_employee_by_personal_data(nameAndLastname[0] , nameAndLastname[1])

    if(len(employeeList) == 0):
        print("Wrong name and lastname")
        return
    elif (len(employeeList) > 1):

        for employee in employeeList:
            print(f"ID: {employee[2]}, Name: {employee[0]}, Lastname: {employee[1]}")
        
        selectedId = int(input("Enter the employee ID to choose: "))

        for employee in employeeList:
            if employee[2] == selectedId:
                employeeId = employee[2]
                break
        
        print(employeeId)
    else:
        employeeId = employeeList[0][2]

    if(employeeId != None):
        print("Przyloz karte")
        cardId = scanning_loop()
        print(cardId)
        print(employeeId)

        if(db.add_card(cardId,0)):
            print("Zarejestrowano karte")
        else:
            buzzer_reject()
            print("Karta jest już zajeta")
            return

        


        if(db.add_employee_card(db.get_card_by_rfid(cardId)[0],employeeId)):
            print("Added")
        else:
            print("Error database")
    else:
        print("Wrong name and lastname or ID")


def tui_block_card():

    cardId = scanning_loop()
    
    if(db.block_card(db.get_card_by_rfid(cardId)[0])):
        print("Blocked")
    else:
        print("Database error")



def tui_block_card_employee():

    nameAndLastname = get_name_and_lastname()

    employeeList = db.get_employee_by_personal_data(nameAndLastname[0] , nameAndLastname[1])

    if(len(employeeList) == 0):
        print("Wrong name and lastname")
        return
    elif (len(employeeList) > 1):

        for employee in employeeList:
            print(f"ID: {employee[2]}, Name: {employee[0]}, Lastname: {employee[1]}")
        
        selectedId = int(input("Enter the employee ID to choose: "))

        for employee in employeeList:
            if employee[2] == selectedId:
                employeeId = employee[2]
                break
        
        print(employeeId)
    else:
        employeeId = employeeList[0][2]

    if(employeeId != None):
        print(employeeId)
        if(db.block_card_by_card_id(db.get_card_id_by_employee_id(employeeId))):
            print("Blocked")
        else:
            print("Database error")
    else:
        print("Wrong name and lastname or ID")



def tui_unlock_card_employee():

    nameAndLastname = get_name_and_lastname()

    employeeList = db.get_employee_by_personal_data(nameAndLastname[0] , nameAndLastname[1])

    if(len(employeeList) == 0):
        print("Wrong name and lastname")
        return
    elif (len(employeeList) > 1):

        for employee in employeeList:
            print(f"ID: {employee[2]}, Name: {employee[0]}, Lastname: {employee[1]}")
        
        selectedId = int(input("Enter the employee ID to choose: "))

        for employee in employeeList:
            if employee[2] == selectedId:
                employeeId = employee[2]
                break
        
        print(employeeId)
    else:
        employeeId = employeeList[0][2]

    if(employeeId != None):
        print(employeeId)

        if(db.unlock_card_by_card_id(db.get_card_id_by_employee_id(employeeId))):
            print("Unlocked")
        else:
            print("Database error")
    else:
        print("Wrong name and lastname or ID")


   


    



def main():
    tui()

if __name__ == '__main__':
    
    try:
        main()
    except Exception as e:
        print(e)