import sqlite3
from datetime import datetime
from sqlite3 import OperationalError
import matplotlib.pyplot as plt

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


def creation_table():
    con = sqlite3.connect('sqlite.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute('''CREATE TABLE ville(id integer primary key autoincrement, nom text, id_pays int)''')
    cur.execute('''CREATE TABLE pays(id integer primary key autoincrement, nom text)''')
    cur.execute('''CREATE TABLE releves(id integer primary key autoincrement, date text, id_ville int, 
    humidite double, pression double, temperature double)''')
    con.commit()


def insertion_donnees(humidite, pression, temperature, ville, pays) -> int:
    con = sqlite3.connect('sqlite.db', check_same_thread=False)
    cur = con.cursor()
    # On vérifie s'il faut insérer le pays ou
    # Simplement récupérer son id
    query = "SELECT COUNT(*) as nb FROM pays WHERE nom = '" + pays + "'"
    cur.execute(query)
    # Si le pays n'existe pas, on le crée
    if cur.fetchall()[0][0] == 0:
        query = "INSERT INTO pays('nom') VALUES('" + pays + "')"
        cur.execute(query)
    # On récupère l'id du pays
    query = "SELECT id FROM pays WHERE nom = '" + pays + "'"
    cur.execute(query)
    id_pays = cur.fetchall()[0][0]

    # On vérifie s'il faut insérer la ville ou
    # Simplement récupérer son id
    query = "SELECT COUNT(*) as nb FROM ville WHERE nom = '" + ville + "' AND id_pays = " + str(id_pays)
    cur.execute(query)
    # Si le pays n'existe pas, on le crée
    if cur.fetchall()[0][0] == 0:
        query = "INSERT INTO ville('nom', 'id_pays') VALUES('" + ville + "', " + str(id_pays) + ")"
        cur.execute(query)
        print("Insertion effectuée")
    # On récupère l'id du pays
    query = "SELECT id FROM ville WHERE nom = '" + ville + "'"
    cur.execute(query)
    id_ville = cur.fetchall()[0][0]

    # On vérifie que les mesures ne sont pas trop proches
    date = datetime.now().strftime("%Y-%m-%d %Hh")
    query = "SELECT COUNT(*) FROM releves WHERE date = '" + date + "' AND id_ville = " + str(id_ville)
    cur.execute(query)
    # Si aucune mesure pour cette date existe, on l'effectue
    if cur.fetchall()[0][0] == 0:
        query = "INSERT INTO releves('date', 'id_ville', 'humidite', 'pression', 'temperature') VALUES('" \
                + date + "', " + str(id_ville) + ", " + str(humidite) + ", " + str(pression) + ", " + str(temperature) \
                + ")"
        cur.execute(query)
    else:
        print("La mesure a déjà été prise cette heure")

    con.commit()
    return id_ville


def recuperation_donnees(id_ville) -> list:
    con = sqlite3.connect('sqlite.db', check_same_thread=False)
    cur = con.cursor()
    query = "SELECT * FROM releves WHERE id_ville = " + str(id_ville)
    cur.execute(query)
    dates = []
    humidites = []
    pressions = []
    temperatures = []
    for row in cur.fetchall():
        dates.append(row[1])
        humidites.append(row[3])
        pressions.append(row[4])
        temperatures.append(row[5])

    con.commit()
    return [dates, humidites, pressions, temperatures]


def texte_exploitable(texte):
    texte = texte.lower()
    sans_caracteres_speciaux = ''
    for character in texte:
        if character.isalnum():
            sans_caracteres_speciaux += character
    texte = sans_caracteres_speciaux
    return texte


def generation_img_graphique(donnees, id_donnees, titre, nom_img):
    fig = plt.figure()
    plt.xticks(ticks=range(len(donnees[0])), rotation=90)
    plt.title(titre)
    plt.plot(donnees[0], donnees[id_donnees])
    fig.savefig(f"./static/images/{nom_img}.jpg", bbox_inches='tight', dpi=150)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()

    if form.validate_on_submit():
        ville = texte_exploitable(form.ville.data)
        pays = texte_exploitable(form.pays.data)

        meteo = requests.get("http://wttr.in/" + pays + "+" + ville + "?format=j1")
        temperature = meteo.json()["current_condition"][0]["temp_C"]
        humidite = meteo.json()["current_condition"][0]["humidity"]
        pression = meteo.json()["current_condition"][0]["pressure"]

        try:
            creation_table()
        except OperationalError:
            print("Les tables sont déjà créées")

        try:
            id_ville = insertion_donnees(humidite, pression, temperature, ville, pays)
            donnees_stat = recuperation_donnees(id_ville)
            generation_img_graphique(donnees_stat, 1, "Humidité", "humidite_plot")
            generation_img_graphique(donnees_stat, 2, "Pression", "pression_plot")
            generation_img_graphique(donnees_stat, 3, "Température", "temperature_plot")
        except Exception as e:
            print(e)

        localisation = {"ville": ville, "pays": pays}
        actuellement = {"temperature": temperature, "humidite": humidite, "pression": pression}
        return render_template('affichage.html', donnees={"localisation": localisation, "actuellement": actuellement})

    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run()
