from flask import Flask
from logger import logger
from config import SQLALCHEMY_DATABASE, UPLOAD_FOLDER

app = Flask(__name__)
app.logger = logger
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "abc"
