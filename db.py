import sqlite3
import os

class Db:
    def __init__(self, filename):
        cwd = os.getcwd()
        if not os.path.basename(cwd) == 'planner':
            os.chdir(cwd + '/planner')
        if not os.path.exists(filename):
            self.con = sqlite3.connect(filename)
            self.init_db(schema='./schema.sql')
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
