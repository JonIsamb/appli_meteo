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


def insertionDonnees(humidite, pression, temperature, ville, pays):
    print("insertion TODO")

def texteExploitable(texte):
    texte = texte.lower()
    sansCaracteresSpeciaux = ''
    for character in texte:
        if character.isalnum():
            sansCaracteresSpeciaux += character
    texte = sansCaracteresSpeciaux
    return texte


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()

    if form.validate_on_submit():
        ville = texteExploitable(form.ville.data)
        pays = texteExploitable(form.pays.data)

        meteo = requests.get("http://wttr.in/" + pays + "+" + ville + "?format=j1")
        temperature = meteo.json()["current_condition"][0]["temp_C"]
        humidite = meteo.json()["current_condition"][0]["humidity"]
        pression = meteo.json()["current_condition"][0]["pressure"]

        try:
            creationTable()
        except OperationalError:
            print("Table existante !")

        try:
            insertionDonnees(humidite, pression, temperature, ville, pays)
        except Exception:
            print("Probeleme d'insertion !")

        return ville + ", " + pays + " : <br />temperature : " + temperature + "<br /> humidite : " + humidite + "<br /> pression : " + pression

    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run()
