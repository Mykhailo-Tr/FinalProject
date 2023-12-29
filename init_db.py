import sqlite3
from logger import logger
from config import DATABASE_FILE


connection = sqlite3.connect(DATABASE_FILE)


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
logger.info(f"Database schema has been initialized for : {DATABASE_FILE}.")
