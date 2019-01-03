import config.database as database
import mysql.connector

class SQLConnection():

    def __init__(self):
        self.cnx = mysql.connector.connect(**database.pop_user)

    def __enter__(self):
        cursor = self.cursor()
        return cursor

    def __exit__(self, type, value, tb):
        if tb is None:
            self.commit()
            self.cnx.close()
        else:
            # print(value)
            self.rollback()
            self.cnx.close()
            return False

    def cursor(self):
        cursor = self.cnx.cursor()
        return cursor

    def commit(self):
        self.cnx.commit()

    def rollback(self):
        self.cnx.rollback()


with SQLConnection() as sql:
    sql.execute('select * from patients where id = 1')
    row = sql.fetchone()
    print(row)
