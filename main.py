from flask import (Flask, redirect, session, render_template, request, send_from_directory, url_for)
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'miloja1502'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

@app.route('/')
def index():
    return "Hola Flask"


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
