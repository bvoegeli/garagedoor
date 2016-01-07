import sqlite3
import time

class logger(object):
    def __init__(self, table_name, database="data_log.sqlite", clear_table=False):
        ''' logger stores data to an sqlite database.
        table_name is the name of the table where data will be stored.
        database is the filename the sqlite database will be stored in.'''
        self.table_name = table_name
        self.database = database
        self.conn = sqlite3.connect(self.database)
        self.cur = self.conn.cursor()
        self.first_store = True
        if clear_table:
            txt = "drop table %s;" % (table_name)
            try:
                self.cur.execute(txt)
                self._commit()
            except sqlite3.OperationalError as e:
                print e
                print("Table not cleared (may not exist): %s" % (table_name))
                pass
    def store(self,data):
        ''' store a new record in the sqlite database.
        data is a dictionary, indexed by column name.
        If the table already exists, then all columns must also already exist or an exception will occur.'''
        columns = data.keys()
        columns.sort()
        if self.first_store:
            txt = "create table " + self.table_name + " ( "
            for column in columns:
                txt += column + ", "
            txt += "datetime )"
            try:
                self.cur.execute(txt)
                self._commit()
            except sqlite3.OperationalError as e:
                pass ### assume this is because table already exists...
            self.first_store = False
        txt = "insert into " + self.table_name + " ( "
        for column in columns:
            txt += column + ", "
        txt += "datetime)VALUES ("
        for column in columns:
            try:
                txt +=str(float(data[column])) + ", "
            except TypeError as e:
                #print e
                txt += "\"" + str(data[column]) + "\", "
            except ValueError as e: #strings raise ValueError, not TypeError
                txt += "\"" + str(data[column]) + "\", "
        txt += "datetime());"
        try:
            self.cur.execute(txt) 
        except sqlite3.OperationalError as e: ## on exception, try inserting any new columns
            print ("sqlite3.OperationalError Exception occurred!")
            print ("---> Are you sure all of the columns in the 'data' dictionary argument")
            print ("     already exist in table "+self.table_name+"?")
            raise e
    def _commit(self):
        self.conn.commit()
        self.cur.execute("PRAGMA locking_mode = NORMAL")