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


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()

    if form.validate_on_submit():
        ville = form.ville.data
        meteo = requests.get("http://wttr.in/" + ville + "?format=j1")
        con = sqlite3.connect('sqlite.db', check_same_thread=False)
        cur = con.cursor()

        try:
            cur.execute('''CREATE TABLE adresse(date text, rue text, label text, x float, y float)''')
            con.commit()
        except OperationalError:
            print("Table existante !")

        return ville + " : " + meteo.json()["current_condition"][0]["temp_C"] + "&degC"

    return render_template('form.html', form=form)


if __name__ == '__main__':
    app.run()
