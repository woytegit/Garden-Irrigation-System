from operator import and_, or_
from os import name
from markupsafe import escape
from flask import Flask, request, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import immediateload
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import distinct
from datetime import date, datetime
import subprocess
import os
import sys
import signal

# Only import on RPi
# import RPi.GPIO as GPIO

app = Flask(__name__)

# the name of the database; add path if necessary
db_name = 'garden_data.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

# each table in the database needs a class to be created for it
# db.Model is required - don't change it

# NOTHING BELOW THIS LINE NEEDS TO CHANGE
# this route will test the database connection and nothing more

# Global variable to store the process running the external script
script_process = None

# classes


class RelayDB(db.Model):
    __tablename__ = 'relays'
    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    def __init__(self, pin, duration, active):
        self.id = None
        self.gpio_pin = pin
        self.duration_time = duration
        self.is_active = active

################################################
# routes


@app.route('/')
def homepage():
    print('Lists updated')
    return redirect('/database')


@app.route('/database', methods=['GET', 'POST'])
def testdb():
    print(request.method)
    try:
        relaysData = RelayDB.query.all()
        return render_template('database.html',  output_data=relaysData)

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/database_update/<int:id>', methods=['GET', 'POST'])
def update(id):
    event_to_update = RelayDB.query.get_or_404(id)
    if request.method == "POST":
        event_to_update.pin = int(request.form['gpio_pin_number'])
        event_to_update.duration = int(request.form['duration_time'])
        event_to_update.active = int(request.form['is_enable'])
        print("Updated event_to_update:", event_to_update)

        try:
            db.session.commit()
            print("POST successful")
            return redirect(url_for('.testdb'))

        except Exception as e:
            print("Error during commit:", str(e))
            error_text = "<p>The error:<br>" + str(e) + "</p>"
            hed = '<h1>Something is broken.</h1>'
            return hed + error_text

    else:
        return render_template("database_update.html", event_to_update=event_to_update)


@app.route('/start_script')
def start_script():
    global script_process

    # Check if the script is already running
    if script_process is not None and script_process.poll() is None:
        return "The script is already running."

    # # Replace "script.py" with the path to your external script UNIX
    # script_process = subprocess.Popen(
    #     ['python', 'script.py'], preexec_fn=os.setsid)

    # Replace "script.py" with the path to your external script Windows
    script_process = subprocess.Popen(
        [sys.executable, 'script.py'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    return "External script started."


@app.route('/stop_script')
def stop_script():
    global script_process

    # Check if the script is running
    if script_process is None or script_process.poll() is not None:
        return "The script is not running."

    # # Stop the script process UNIX
    # os.killpg(os.getpgid(script_process.pid), signal.SIGTERM)
    # script_process = None

    # Stop the script process Windows
    script_process.terminate()
    script_process = None

    # GPIO.setmode(GPIO.BMC)
    relaysToTerminate = RelayDB.query.all()
    print("Script has been stopped manually")
    for relayToStop in relaysToTerminate:
        # Function that turns of all relays after termination the script

        # GPIO.setup(relayToStop.pin, GPIO.OUT)
        print("GPIO.setup(relayToStop.pin, GPIO.OUT)")
        # GPIO.output(relayToStop.pin, GPIO.LOW)
        print("GPIO.output(relayToStop.pin, GPIO.LOW)")
        print(
            f"Relay no.{relayToStop.id} is deactived with status GPIO.input(relayToStop.pin)")

    # GPIO.cleanup()
    print("GPIO.cleanup()")

    return "External script stopped."


@app.route("/database_delete/<int:id>")
def delete(id):
    event_to_delete = RelayDB.query.get_or_404(id)
    try:
        # db.session.delete(event_to_delete)
        # db.session.commit()
        # return redirect(url_for('.testdb'))
        print("Nice try, but not this time :)")
        return 'Nice try, but not this time :) You cannot delete anything from database'

    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


@app.route('/about')
def about():
    print(request.method)
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == "__main__":
    app.debug = True
    app.run()
