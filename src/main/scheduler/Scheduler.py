from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import sqlite3
import datetime

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None
current_caregiver = None

def is_strong_password(password):
    # rule 1:  length at least 8 characters
    if len(password) < 8:
        return False
    # rule 2: includes at least one uppercase letter
    has_upper = any(c.isupper() for c in password)
    # rule 3: includes at least one lowercase letter
    has_lower = any(c.islower() for c in password)
    # rule 4: includes at least one digit
    has_num = any(c.isdigit() for c in password)
    # rule 5: includes at least one special character among !@#?
    has_special = any(c in "!@#?" for c in password)

    return has_upper and has_lower and has_num and has_special


def create_patient(tokens):
    """
    Part 1
    """
    if len(tokens) != 3:
        print("Create patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    if not is_strong_password(password):
        print("Create patient failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from \"!\", \"@\", \"#\", \"?\")")
        return

    # check 1: check if the username has been taken already
    try:
        if username_exists_patient(username):
            print("Username taken, try again")
            return
    except Exception:
        print("Create patient failed")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except Exception:
        print("Create patient failed")
        return

    print("Created user " + username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        for row in cursor:
            return True
    except sqlite3.Error as e:
        raise e
    finally:
        cm.close_connection()

    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]

    if not is_strong_password(password):
        print("Create caregiver failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from \"!\", \"@\", \"#\", \"?\")")
        return

    # check 2: check if the username has been taken already
    try:
        if username_exists_caregiver(username):
            print("Username taken, try again!")
            return
    except Exception:
        print("Failed to create user.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except Exception:
        print("Failed to create user.")
        return

    print("Created user " + username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        for row in cursor:
            return True
    except sqlite3.Error as e:
        raise e
    finally:
        cm.close_connection()

    return False


def login_patient(tokens):
    """
    Part 1
    """
    global current_caregiver
    global current_patient

    # check 1: if someone's already logged-in, they need to log out first
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except Exception:
        print("Login patient failed")
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient

    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except Exception:
        print("Login failed.")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    if len(tokens) != 2:
        print("Please try again")
        return

    date = tokens[1]
    date_tokens = date.split("-")
    try:
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = datetime.datetime(year, month, day)
    except Exception:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        get_caregivers = "SELECT Caregiver_Username FROM Availabilities WHERE Date = ? ORDER BY Caregiver_Username"
        cursor.execute(get_caregivers, (d,))
        caregivers = cursor.fetchall()

        get_vaccines = "SELECT Name, Doses FROM Vaccines"
        cursor.execute(get_vaccines)
        vaccines = cursor.fetchall()

        print("Caregivers:")
        if len(caregivers) == 0:
            print("No caregivers available")
        else:
            for row in caregivers:
                print(row[0])

        print("Vaccines:")
        if len(vaccines) == 0:
            print("No vaccines available")
        else:
            for row in vaccines:
                print(f"{row[0]} {row[1]}")

    except sqlite3.Error:
        print("Please try again")
    finally:
        cm.close_connection()

def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if current_patient is None:
        print("Please login as a patient")
        return
    if len(tokens) != 3:
        print("Please try again")
        return

    date = tokens[1]
    vaccine_name = tokens[2]

    date_tokens = date.split("-")
    try:
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = datetime.datetime(year, month, day)
    except Exception:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        # 1
        cursor.execute("SELECT Caregiver_Username FROM Availabilities WHERE Date = ? ORDER BY Caregiver_Username", (d,))
        caregiver_row = cursor.fetchone()
        if caregiver_row is None:
            print("No caregiver is available")
            return
        caregiver_username = caregiver_row[0]

        # 2
        cursor.execute("SELECT Doses FROM Vaccines WHERE Name = ?", (vaccine_name,))
        vaccine_row = cursor.fetchone()
        if vaccine_row is None or vaccine_row[0] <= 0:
            print("Not enough available doses")
            return

        # 4 - use AUTOINCREMENT, but reset counter when table is empty (cross-test DB resets)
        cursor.execute("SELECT COUNT(*) FROM Appointments")
        if cursor.fetchone()[0] == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Appointments'")

        insert_appointment = "INSERT INTO Appointments (Date, Vaccine_Name, Patient_Username, Caregiver_Username) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_appointment, (d, vaccine_name, current_patient.get_username(), caregiver_username))
        appointment_id = cursor.lastrowid

        # 5
        delete_availability = "DELETE FROM Availabilities WHERE Date = ? AND Caregiver_Username = ?"
        cursor.execute(delete_availability, (d, caregiver_username))

        # 6
        update_vaccine = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = ?"
        cursor.execute(update_vaccine, (vaccine_name,))

        conn.commit()
        print(f"Appointment ID {appointment_id}, Caregiver username {caregiver_username}")

    except sqlite3.Error:
        print("Please try again")
    finally:
        cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except sqlite3.Error:
        print("Upload Availability Failed")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception:
        print("Error occurred when uploading availability")
        return
    print("Availability uploaded!")

def cancel(tokens):
    """
    TODO: Extra Credit
    """
    global current_caregiver
    global current_patient

    # 1
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    # 2. check format (cancel <appointment_id>)
    if len(tokens) != 2:
        print("Please try again")
        return

    try:
        appointment_id = int(tokens[1])
    except ValueError:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        # 3. check whether Appointment ID exists
        cursor.execute("SELECT Vaccine_Name, Date, Caregiver_Username FROM Appointments WHERE ID = ?", (appointment_id,))
        row = cursor.fetchone()

        if row is None:
            print(f"Appointment ID {appointment_id} does not exist")
            return

        vaccine_name = row[0]
        raw_date = row[1]
        caregiver_username = row[2]

        # convert date back to datetime object (same format as reserve/upload_availability)
        s = str(raw_date).split()[0]
        parts = s.split("-")
        d = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]))

        # 4. delete the appointment
        cursor.execute("DELETE FROM Appointments WHERE ID = ?", (appointment_id,))

        # 5. add the availability back to the caregiver's schedule
        try:
            cursor.execute("INSERT INTO Availabilities (Date, Caregiver_Username) VALUES (?, ?)", (d, caregiver_username))
        except sqlite3.IntegrityError:
            pass

        # 6. add the dose back to the vaccine inventory
        cursor.execute("UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = ?", (vaccine_name,))

        # finish the transaction
        conn.commit()
        print(f"Appointment ID {appointment_id} has been successfully canceled")

    except sqlite3.Error:
        print("Please try again")
    finally:
        cm.close_connection()

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except Exception:
        print("Error occurred when adding doses")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except Exception:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except Exception:
            print("Error occurred when adding doses")
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 1:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        cursor = conn.cursor()

        # search from caregiver's perspective
        if current_caregiver is not None:
            get_appointments = "SELECT ID, Vaccine_Name, Date, Patient_Username FROM Appointments WHERE Caregiver_Username = ? ORDER BY ID"
            cursor.execute(get_appointments, (current_caregiver.get_username(),))
            rows = cursor.fetchall()

            if len(rows) == 0:
                print("No appointments scheduled")
            else:
                for row in rows:
                    # remove time part
                    date_str = str(row[2]).split()[0]
                    print(f"{row[0]} {row[1]} {date_str} {row[3]}")

        # search from patient's perspective
        else:
            get_appointments = "SELECT ID, Vaccine_Name, Date, Caregiver_Username FROM Appointments WHERE Patient_Username = ? ORDER BY ID"
            cursor.execute(get_appointments, (current_patient.get_username(),))
            rows = cursor.fetchall()

            if len(rows) == 0:
                print("No appointments scheduled")
            else:
                for row in rows:
                    date_str = str(row[2]).split()[0]
                    print(f"{row[0]} {row[1]} {date_str} {row[3]}")

    except sqlite3.Error:
        print("Please try again")
    finally:
        cm.close_connection()


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 1:
        print("Please try again")
        return

    try:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out")
    except Exception:
        print("Please try again")


def start():
    stop = False
    print("*** Please enter one of the following commands ***")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")
    print("> logout")
    print("> quit")
    print()

    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input()).strip()
        except Exception:
            print("Please try again!")
            continue

        tokens = response.split()
        if len(tokens) == 0:
            print("Please try again!")
            continue

        operation = tokens[0].lower()

        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()