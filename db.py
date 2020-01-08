import sqlite3
import os
from dotenv import load_dotenv
from flask import g

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def connect_db():
    sql = sqlite3.connect(DATABASE_URL)
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()

    return g.sqlite_db
