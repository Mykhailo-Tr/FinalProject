from flask import Flask
from logger import logger
from SQL_db import DataBase
from json_db import JsonDatabase
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE, UPLOAD_FOLDER, DATABASE_FILE, JSON_FILE

app = Flask(__name__)
app.logger = logger
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "abc"
site_db = DataBase(DATABASE_FILE)
db = SQLAlchemy()
titles = JsonDatabase(JSON_FILE)
