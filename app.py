from flask import Flask
import requests as requests

app = Flask(__name__)


@app.route('/')
def index():
    ville = "Lens"
    meteo = requests.get("http://wttr.in/" + ville + "?format=j1")

    return ville + " : " + meteo.json()["current_condition"][0]["temp_C"] + "&degC"


if __name__ == '__main__':
    app.run()
