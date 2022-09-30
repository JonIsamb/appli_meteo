import sqlite3
from sqlite3 import OperationalError

from flask import Flask, render_template
import requests as requests
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'Ma clé secrète'


class Form(FlaskForm):
    ville = StringField('ville', validators=[DataRequired()])
    pays = StringField('pays', validators=[DataRequired()])


def creationTable():
    con = sqlite3.connect('sqlite.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute('''CREATE TABLE ville(id int, nom text, codePostal text)''')
    con.commit()
    cur.execute('''CREATE TABLE pays(id int, nom text)''')
    con.commit()
    cur.execute('''CREATE TABLE releves(
    id int, date text, id_ville int, id_pays int, 
    humidite double, pression double, temperature double)''')
    con.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()

    if form.validate_on_submit():
        ville = form.ville.data
        pays = form.pays.data
        meteo = requests.get("http://wttr.in/" + pays + "+" + ville + "?format=j1")
        con = sqlite3.connect('sqlite.db', check_same_thread=False)
        cur = con.cursor()

        try:
            creationTable()
        except OperationalError:
            print("Table existante !")

        return ville + " : " + meteo.json()["current_condition"][0]["temp_C"] + "&degC"

    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run()
