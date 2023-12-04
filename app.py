from flask import Flask
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_RECORD_QUERIES"] = False

db = SQLAlchemy(app)



# Импорт маршрутов
from routes import *

if __name__ == '__main__':

    app.run(debug=False)
