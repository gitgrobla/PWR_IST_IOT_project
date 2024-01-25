#!/usr/bin/env python3

import datetime
import sqlite3
import os, sys, random

from typing import Dict, Tuple, Optional, List

# This should be changed. We can also create new folder and path where we can store our database. 
DEFAULT_PROJECT_DATABASE_PATH = "./iot_database.db" 
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SYSTEM_VAR_NAME = "IOT_PROJECT_DATABASE_PATH"

NO_RESULT = 1
NO_EXIT = 2
EXIT_ALREADY_SAVED = 3

EmployeeTuple = Tuple[str, str, str] # NAME, LAST NAME, ID


RFIDS = [];
IS_BLOCKED_BOOLS = [False, False, False, True]
EMPLOYEES_NAMES = ["John", "Donald", "Taylor", ""]
EMPLOYEES_LASTNAMES = ["Cena", "Duck", "Swift" ""]

class WorkRegister:

    def __init__(self, employee_id, entries_num, exits_num, work_hours, start_date, end_date):
        self.employee_id = employee_id
        self.entries_num = entries_num
        self.exits_num = exits_num
        self.work_hours = work_hours
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return f"Employee ID: {self.employee_id}\nNumber of entries: {self.entries_num}\nNumber of exits: {self.exits_num}\nWorktime in hours: {self.work_hours} (between {self.start_date.strftime(DATETIME_FORMAT)} and {self.end_date.strftime(DATETIME_FORMAT)})"


def get_sys_var(name) -> str:
    sys_var_value = os.environ.get(name)
    if sys_var_value is not None: return sys_var_value
    return DEFAULT_PROJECT_DATABASE_PATH

def create_database(db_name: str = DEFAULT_PROJECT_DATABASE_PATH, dropped_old_db: bool = True):

    if dropped_old_db and os.path.exists(db_name):
        os.remove(db_name)
        print("Dropped old database")

    try:
        with sqlite3.connect(db_name) as connection:

            cursor = connection.cursor()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS Cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rfid INTEGER UNIQUE NOT NULL,
                is_blocked INTEGER NOT NULL DEFAULT 0
                )"""
            )

            connection.commit()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                last_name TEXT NOT NULL
                )"""
            )

            connection.commit()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS Employees_cards (
                card_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                PRIMARY KEY (card_id, employee_id),
                FOREIGN KEY (card_id) REFERENCES Cards(id),
                FOREIGN KEY (employee_id) REFERENCES Employees(id)
                )"""
            )

            connection.commit()

            cursor.execute(
                """CREATE TABLE IF NOT EXISTS Presences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    entry_date DATETIME NOT NULL,
                    exit_date DATETIME,
                    entry_place INTEGER NOT NULL,
                    exit_place INTEGER,
                    FOREIGN KEY (card_id) REFERENCES Cards(id),
                    FOREIGN KEY (employee_id) REFERENCES Employees(id),
                    CHECK (exit_date IS NULL OR entry_date <= exit_date)
                )"""
            )

            connection.commit()

            cursor.execute(
                """CREATE TRIGGER prevent_blocked_cards_insert
                    BEFORE INSERT ON Presences
                    FOR EACH ROW
                    WHEN (SELECT is_blocked FROM Cards WHERE id = NEW.card_id) = 1
                    BEGIN
                        -- Jeśli karta jest zablokowana, uniemożliwiamy dodanie lub aktualizację rekordu
                        SELECT RAISE(ABORT, 'Nie można dodać rekordu dla zablokowanej karty.');
                    END;
                """)
            
            connection.commit()

            cursor.execute(
                """CREATE TRIGGER prevent_blocked_cards_update
                    BEFORE UPDATE ON Presences
                    FOR EACH ROW
                    WHEN (SELECT is_blocked FROM Cards WHERE id = NEW.card_id) = 1
                    BEGIN
                        -- Jeśli karta jest zablokowana, uniemożliwiamy dodanie lub aktualizację rekordu
                        SELECT RAISE(ABORT, 'Nie można modyfikować rekordu dla zablokowanej karty.');
                    END;
                """)
            
            connection.commit()
            
            print("The new database created.")

    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)

def execute_query(query: str) -> bool:
    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()

            cursor.execute(query)

            connection.commit()

    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)
        return False;

    return True

def add_employee(name: str, last_name: str) -> bool:

    return execute_query(f"INSERT INTO Employees(name, last_name) VALUES ('{name}', '{last_name}')")

def add_card(rfid: int, is_blocked: bool) -> bool:

    is_blocked_as_int = 1 if is_blocked else 0

    return execute_query( f"INSERT INTO Cards(rfid, is_blocked) VALUES ({rfid}, {is_blocked_as_int})")

def get_employee_id_by_card_id(card_id: int) -> int:
    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()

            query = f"SELECT employee_id FROM Employees_cards WHERE card_id = {card_id}"

            cursor.execute(query)

            result = cursor.fetchone()

            if result == None:
                return None

            return result[0]

    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)
        return None;

def get_card_by_rfid(rfid: int) -> int:
    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()

            query = f"SELECT * FROM Cards WHERE rfid = {rfid}"

            cursor.execute(query)

            result = cursor.fetchone()

            if result == None:
                return None

            return result

    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)
        return None;

def add_employee_card(card_id: int, employee_id: int) -> bool:

    return execute_query(f"INSERT INTO Employees_cards(card_id, employee_id) VALUES ({card_id}, {employee_id})")


def add_presence(card_id: int, employee_id: int, entry_date: datetime, entry_place: int, exit_date: datetime = None,  exit_place: int = None) -> bool:

    exit_date_to_table = 'NULL' if exit_date == None else exit_date.strftime(DATETIME_FORMAT)
    exit_place_to_table = 'NULL' if exit_place == None else exit_place

    return execute_query(f"INSERT INTO Presences(card_id, employee_id, entry_date, entry_place, exit_date, exit_place) VALUES ({card_id}, {employee_id}, '{entry_date.strftime(DATETIME_FORMAT)}', {entry_place}, '{exit_date_to_table}', {exit_place_to_table} )")


def add_exit(presence_id: int, exit_date: datetime, exit_place: int) -> bool:

    exit_date_to_table = exit_date.strftime(DATETIME_FORMAT)

    return execute_query(f"UPDATE Presences SET exit_date = '{exit_date_to_table}', exit_place = {exit_place} WHERE id = {presence_id}")


def get_timedelta(date1: str, date2: str) -> int:
    datetime1 = datetime.datetime.strptime(date1, DATETIME_FORMAT)
    datetime2 = datetime.datetime.strptime(date2, DATETIME_FORMAT)
    timedelta = datetime2 - datetime1
    return int(timedelta.total_seconds() / 60)


def get_employee_work_register(employee_id, start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()) -> WorkRegister:
    if end_date < start_date: return None

    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()

            start_date_as_string = start_date.strftime(DATETIME_FORMAT)
            end_date_as_string = end_date.strftime(DATETIME_FORMAT)

            query = f"SELECT * FROM Presences WHERE employee_id = {employee_id} AND entry_date >= '{start_date_as_string}' AND exit_date IS NOT NULL AND exit_date <= '{end_date_as_string}'"

            results = cursor.execute(query)

            work_time_in_minutes = 0
            counter = 0
            for row in results:
                work_time_in_minutes += get_timedelta(row[3], row[4])
                counter += 1

            work_time_in_hours = int(work_time_in_minutes / 60)

            return WorkRegister(employee_id, counter, counter, work_time_in_hours, start_date, end_date)


    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)
        return None;


def get_all_employees_work_registers(start_date: datetime.datetime, end_date: datetime.datetime = datetime.datetime.now()) -> Dict[int, WorkRegister]:
    if end_date < start_date: return None

    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()

            start_date_as_string = start_date.strftime(DATETIME_FORMAT)
            end_date_as_string = end_date.strftime(DATETIME_FORMAT)

            result_dict = dict()

            query = f"SELECT * FROM Presences WHERE entry_date >= '{start_date_as_string}' AND exit_date IS NOT NULL AND exit_date <= '{end_date_as_string}'"

            results = cursor.execute(query)

            for row in results:
                current_id = row[2]
                current_wr = result_dict.get(current_id)
                if current_wr is not None:
                    current_wr.work_hours += get_timedelta(row[3], row[4])
                    current_wr.entries_num += 1
                    current_wr.exits_num += 1
                else:
                    result_dict[current_id] = WorkRegister(current_id, 1, 1, get_timedelta(row[3], row[4]), start_date, end_date)

            return {key: WorkRegister(
                        value.employee_id,
                        value.entries_num,
                        value.exits_num,
                        int(value.work_hours / 60),
                        value.start_date,
                        value.end_date
                    ) for key, value in result_dict.items()}


    except sqlite3.Error as e:
        print("Error during connection with database: ", e, file=sys.stderr)
        return None;


def block_card(card_id) -> bool:
    query = f"UPDATE Cards SET is_blocked = 1 WHERE id = {card_id}"
    return execute_query(query)


def block_card_by_employee_id(employee_id) -> bool:
    query = f"UPDATE Cards SET is_blocked = 1 WHERE id = {employee_id}"
    return execute_query(query)


def unlock_card_by_employee_id(employee_id) -> bool:
    query = f"UPDATE Cards SET is_blocked = 0 WHERE id = {employee_id}"
    return execute_query(query)


def generate_random_date_pair() -> Tuple[datetime.datetime, datetime.datetime]:
    random_date = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))

    random_date_later = random_date + datetime.timedelta(hours=random.randint(0, 12))

    return random_date, random_date_later


def fill_database_with_init_data() -> None:

    for name, last_name in zip(EMPLOYEES_NAMES, EMPLOYEES_LASTNAMES):
        add_employee(name, last_name)


def get_last_employee_presences(employee_id: int) -> Tuple[int, Optional[Tuple]]:

    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()
            query = f"SELECT * FROM Presences WHERE employee_id = {employee_id} ORDER BY entry_date DESC LIMIT 1"

            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
            if result == []:
                return (NO_RESULT, None)
            
            if len(result) == 1:
                last_presence = result[0]
                last_presence_exit_date = last_presence[4]
                if last_presence_exit_date == 'NULL':
                    return (NO_EXIT, last_presence)
                else:
                    return (EXIT_ALREADY_SAVED, last_presence)
                
            raise ValueError("Database error")

    except Exception as e:
        print(e, file=sys.stderr)


def get_employee(query: str) -> List[EmployeeTuple]:
    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            return [] if result == None else result
        
    except Exception as e:
        print(e, file=sys.stderr)
        

def get_employee_by_personal_data(name: str, last_name: str) -> List[EmployeeTuple]:
    return get_employee(f"SELECT name, last_name, id FROM Employees WHERE name = '{name}' AND last_name = '{last_name}' ORDER BY 1,2,3")
        

def get_employee_by_id(employee_id: int) -> List[EmployeeTuple]:
    return get_employee(f"SELECT name, last_name, id FROM Employees WHERE id = {employee_id} ORDER BY 1,2,3")


def get_all_employees_data(has_blocked_card: bool = True) -> List[EmployeeTuple]:
    try:
        with sqlite3.connect(DEFAULT_PROJECT_DATABASE_PATH) as connection:
            cursor = connection.cursor()
            is_blocked_as_int = 1 if has_blocked_card else 0
            if has_blocked_card:
                query = f"""SELECT E.name name, E.last_name last_name, E.id id
                            FROM (Employees E JOIN Employees_cards EC ON E.id = EC.card_id) Q JOIN Cards C ON Q.card_id = C.id 
                            WHERE C.is_blocked = {is_blocked_as_int}
                            ORDER BY 1, 2, 3""";

            cursor.execute(query)
            result = cursor.fetchall()

            return [] if result == None else result
        
    except Exception as e:
        print(e, file=sys.stderr)


# def main():
#     db_path = get_sys_var(SYSTEM_VAR_NAME)
#     create_database(db_path, True)
#     add_card(1, 0)
#     add_card(2, 1)
#     add_card(3, 0)
#     add_card(4, 0)
#     add_employee("John", "Smith")
#     add_employee("Eva", "Stone")
#     add_employee("Donald", "Duck")
#     add_employee_card(1, 1)
#     add_employee_card(2, 2)
#     add_employee_card(3, 3)
#     add_presence(1, 1, datetime.datetime.now(), 1)
#     # add_presence(2, 2, datetime.datetime.now(), 2)
#     add_presence(3, 3, datetime.datetime.now(), 3)

#     # add_exit(1, datetime.datetime(2023, 1, 14, 3, 2, 1), 10)

#     wr = get_employee_work_register(1, datetime.datetime(2023, 1, 1, 0, 0, 0), datetime.datetime.now())
#     print(wr)

#     wr_dict = get_all_employees_work_registers(datetime.datetime(2023, 1, 1, 0, 0, 0), datetime.datetime.now())
#     for _, wr in wr_dict.items():
#         print(wr)

#     block_card(3)

#     print(get_all_employees_data())
#     print(get_employee_by_personal_data("Donald", "Duck"))


if __name__ == '__main__':
    create_database()
    fill_database_with_init_data()
    add_card(1, False)
    add_employee_card(1,1)
