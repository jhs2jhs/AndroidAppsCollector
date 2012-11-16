import sqlite3
import db_sql
import util

db_path = './db_app_related.db'

def get_db():
    db = sqlite3.connect(db_path)
    return db

db = get_db()

def db_init():
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.executescript(db_sql.sql_init)
    db.commit()
    c.execute('SELECT * FROM SQLITE_MASTER')
    tables = c.fetchall()
    print '** related tables: %s **'%(str(len(tables)))
    c.close()

def db_execute_g(sql, params): # in general
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.execute(sql, params)
    db.commit()
    c.close()

def db_get_g(sql, params):
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.execute(sql, params)
    r = c.fetchall()
    c.close()
    return r

