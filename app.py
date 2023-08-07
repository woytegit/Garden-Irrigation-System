from operator import and_, or_
from os import name
from markupsafe import escape
from flask import Flask, request, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import immediateload
from sqlalchemy.sql import text
from datetime import date, datetime
import subprocess

from sqlalchemy.sql.expression import distinct

# import pymysql
# from flask_bootstrap import Bootstrap
# from flask_wtf import FlaskForm
# from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField, DateField
# from wtforms.validators import InputRequired, Length, Regexp, NumberRange


app = Flask(__name__)

# Flask-WTF requires an enryption key - the string can be anything
# app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'

# Flask-Bootstrap requires this line
# Bootstrap(app)

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


# class Pracownicy(db.Model):
#     __tablename__ = 'Pracownicy'
#     id = db.Column(db.Integer, primary_key=True)
#     imie = db.Column(db.String)
#     nazwisko = db.Column(db.String)
#     stanowisko = db.Column(db.String)
#     uprawnienia = db.Column(db.Integer)

#     def __init__(self, imie, nazwisko, stanowisko, uprawnienia):
#         self.id = None
#         self.imie = imie
#         self.nazwisko = nazwisko
#         self.stanowisko = stanowisko
#         self.uprawnienia = uprawnienia


# class Kategorie_zadan(db.Model):
#     __tablename__ = 'Kategorie_zadan'
#     id = db.Column(db.Integer, primary_key=True)
#     nazwa = db.Column(db.String)

#     def __init__(self, nazwa):
#         self.id = None
#         self.nazwa = nazwa


# class Stanowiska(db.Model):
#     __tablename__ = 'Stanowiska'
#     id = db.Column(db.Integer, primary_key=True)
#     nazwa = db.Column(db.String)

#     def __init__(self, nazwa):
#         self.id = None
#         self.nazwa = nazwa


# class Uprawnienia(db.Model):
#     __tablename__ = 'Uprawnienia'
#     id = db.Column(db.Integer, primary_key=True)
#     nazwa = db.Column(db.String)

#     def __init__(self, nazwa):
#         self.id = None
#         self.nazwa = nazwa

# functions


# def load_all_task_categories():
#     categories_temp = Kategorie_zadan.query.order_by(
#         Kategorie_zadan.nazwa).all()
#     for item in categories_temp:
#         task_categories[item.id] = item.nazwa
#     return task_categories


# def load_all_workers():
#     workers_temp = Pracownicy.query.order_by(Pracownicy.nazwisko).all()
#     for person in workers_temp:
#         workers_dict[person.id] = {'imie': person.imie, 'nazwisko': person.nazwisko,
#                                    'stanowisko': person.stanowisko, 'uprawienia': person.uprawnienia}
#     return workers_dict


# def setup_filter_lists():
#     kalendarz = Kalendarz.query.all()
#     for item in kalendarz:
#         if item.kategoria not in category_list:
#             category_list.append(item.kategoria)
#         if item.wstawil not in moder_guy:
#             moder_guy.append(item.wstawil)
#     category_list.sort()
#     moder_guy.sort()


################################################
# routes

@app.route('/')
def homepage():
    # if not len(task_categories):
    # setup_filter_lists()
    # task_categories = load_all_task_categories()
    # print(load_all_task_categories())
    # print(load_all_workers())
    print('Lists updated')
    # print(task_categories)
    return redirect('/database')


@app.route('/database', methods=['GET', 'POST'])
def testdb():
    print(request.method)
    try:
        kalendarz = RelayDB.query.all()
        return render_template('database.html',  output_data=kalendarz)

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


@app.route('/run_external_script')
def add_event_form():  # def run_external_script():
    try:
        # Replace "your_script.py" with the path to your external script
        subprocess.run(['python', 'script.py'], check=True)
        return 'External script executed successfully.'
    except subprocess.CalledProcessError as e:
        return f'Error: {e}'


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
