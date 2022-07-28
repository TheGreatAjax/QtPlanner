import sqlite3
import os

class Db:
    def __init__(self, filename):
        # filename = os.path.join('planner', filename)
        if not os.path.exists(filename):
            self.con = sqlite3.connect(filename)
            self.init_db(schema='planner/schema.sql')
        else:
            self.con = sqlite3.connect(filename)
        self.con.row_factory = sqlite3.Row

    def init_db(self, schema):
        with open(schema, encoding='utf-8') as f:
            self.con.executescript(f.read())

    def get_connection(self):
        return self.con
    
    def get_cursor(self):
        return self.con.cursor()
