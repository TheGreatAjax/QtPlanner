import sqlite3
import os

class Db:
    __schema_file = 'database/schema.sql'
    __db_file = 'database/tasks.db'

    def _init_db():
        if not os.path.exists(Db.__db_file):
            with open(Db.__schema_file, encoding='utf-8') as f:
                sqlite3.connect(Db.__db_file).executescript(f.read())
    
    def __init__(self):
        self.con = sqlite3.connect(Db.__db_file)
        self.con.row_factory = sqlite3.Row

    def get_connection(self):
        return self.con
    
    def get_cursor(self):
        return self.con.cursor()
