import time
import datetime
import sqlite3

# Only import on RPi
# import RPi.GPIO as GPIO

# Function to create the database and table of timestamps (execute only once to set up the database)


def create_timestamp_table():
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timestamps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            manual BOOL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to create the database and table of timestamps


def create_relays_table():
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pin INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            active BOOL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert data for a relay


def insert_relay_data(pin, duration, active):
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO relays (pin, duration, active) VALUES (?, ?, ?)
    ''', (pin, duration, active))
    conn.commit()
    conn.close()

# Function to update the active time for a relay


def update_relay_duration(relay_id, duration):
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE relays SET duration = ? WHERE id = ?
    ''', (duration, relay_id))
    conn.commit()
    conn.close()

# Function to update the active status for a relay


def update_relay_status(relay_id, active):
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE relays SET active = ? WHERE id = ?
    ''', (active, relay_id))
    conn.commit()
    conn.close()

# Function to fetch all relay data


def get_all_relays():
    conn = sqlite3.connect('garden_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM relays')
    relays = cursor.fetchall()
    conn.close()
    return relays

# Function to save the timestamp to the database


def save_timestamp_to_db(timeDelay, manual):
    try:
        # Get the current timestamp
        current_timestamp = datetime.datetime.now()
        manual
        # Connect to the database
        conn = sqlite3.connect('garden_data.db')
        cursor = conn.cursor()

        # Fetch the last timestamp from the database (if any)
        cursor.execute(
            'SELECT timestamp FROM timestamps ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            last_timestamp_str = result[0]
            last_timestamp = datetime.datetime.strptime(
                last_timestamp_str, '%Y-%m-%d %H:%M:%S')

            # Check if the time difference is less than the specified time delay
            time_difference = current_timestamp - last_timestamp
            if time_difference.total_seconds() < timeDelay and not manual:
                print(
                    f"Warning: Program is running too frequently (less than {timeDelay // 60} minutes).")
                conn.close()
                return True  # Return True if the warning was issued

        # Insert the current timestamp to the database
        cursor.execute('INSERT INTO timestamps (timestamp, manual) VALUES (?,?)',
                       (current_timestamp.strftime('%Y-%m-%d %H:%M:%S'), manual))
        conn.commit()
        conn.close()
        print("Timestamp saved successfully.")
        return False  # Return False if no warning was issued
    except Exception as e:
        print(f"Error: {e}")
        return False  # Return False if an error occurred


def runSystem(relaysTable):
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setmode(GPIO.BCM)
    print("GPIO.setmode(GPIO.BCM)")
    for relay in relaysTable:
        if relay[3]:
            # GPIO.setup(relay[1], GPIO.OUT)
            print(f"GPIO.setup({relay[1]}, GPIO.OUT)")
            # GPIO.output(relay[1], GPIO.HIGH)
            print(f"GPIO.output({relay[1]}, GPIO.HIGH)")
            print(
                f"Relay no.{relay[0]} is active for {relay[2]} seconds with status GPIO.input(relay[1])")
            time.sleep(relay[2])
            # GPIO.output(relay[1], GPIO.LOW)
            print(f"GPIO.output({relay[1]}, GPIO.LOW)")
            print("====================")
    # GPIO.cleanup()
    print("GPIO.cleanup()")


def setupParameters():
    if len(get_all_relays()) == 0:
        insert_relay_data(5, 10, 0)
        insert_relay_data(6, 5, 0)
        insert_relay_data(13, 10, 0)
        insert_relay_data(19, 5, 0)
        insert_relay_data(26, 10, 0)
        insert_relay_data(21, 5, 0)


# Example usage:
if __name__ == "__main__":

    # Create the table (execute only once to set up the database)
    create_relays_table()

    # Set up the database and table (execute only once to set up the database)
    create_timestamp_table()

    # Insert data for a relay (pin, duration, active)
    setupParameters()

    if False:
        # Update the active status for a relay by its ID
        update_relay_status(1, True)  # Set relay with ID 1 as active
        update_relay_status(2, False)  # Set relay with ID 2 as active
        update_relay_status(3, True)  # Set relay with ID 3 as active
        update_relay_status(4, True)  # Set relay with ID 4 as active
        update_relay_status(5, False)  # Set relay with ID 5 as active
        update_relay_status(6, True)  # Set relay with ID 6 as active
    # update_relay_status(3, True)  # Set relay with ID 3 as active
    # update_relay_duration(1, 12)

    # Call the function with the time delay (300 seconds in this example)
    warning_issued = save_timestamp_to_db(timeDelay=60, manual=False)
    warning_issued = False
    # Call the function to execute watering stuff
    if not warning_issued:
        all_relays = get_all_relays()
        runSystem(all_relays)
