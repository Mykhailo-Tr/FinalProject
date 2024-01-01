import sqlite3
from logger import logger
from config import DATABASE_FILE, SQL_SCHEMA_FILE


connection = sqlite3.connect(DATABASE_FILE)


with open(SQL_SCHEMA_FILE) as f:
    connection.executescript(f.read())

cur = connection.cursor()
logger.info(f"Database schema has been initialized for : {DATABASE_FILE}.")
