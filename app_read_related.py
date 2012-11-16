import httplib
import json
from bs4 import BeautifulSoup
import bs4
import urlparse
import urllib
from datetime import datetime
import http
import db_app
import db_sql
import err
import time
import util
from cate_read_google_play import *
import sqlite3

def db_init():
    db_app.db_init()

def related_merge():
    rows = db_app.db_get_g(db_sql.sql_related_merge_get, ())
    i_t = len(rows)
    print '** start to merge related list %d **'%(i_t)
    i = 0 
    p = 0
    for row in rows:
        app_id = row[0]
        db_app.db_execute_g(db_sql.sql_related_merge_insert, (app_id, ))
        p, i = util.p_percent(p, i, i_t, 5)

def related_read_main():
    finish = True
    rows = db_app.db_get_g(db_sql.sql_related_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t)
        app_id = row[0]
        related_read(app_id)
        #util.sleep()
        #return 

def related_read(app_id):
    try:
        url = '/%s/details?id=%s'%(android_root, app_id)
        print '** related %s **'%(url)
        status, body = android_https_get(url)
        #print status, body
        if status == 404:
            print '== 404'
            db_app.db_execute_g(db_sql.sql_related_read_update, (1, str(datetime.now()), app_id))
            return 
        if status != 200:
            raise Exception('related read https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        related_view(app_id, soup)
        related_install(app_id, soup)
        db_app.db_execute_g(db_sql.sql_related_read_update, (1, str(datetime.now()), app_id))
        util.sleep()
    except Exception as e:
        err.except_p(e)

def related_view(app_id, soup):
    divs_fa = soup.find_all(name='div', attrs={'data-analyticsid':'related'})
    for divs in divs_fa:
        div_fa = divs.find_all(name='div', attrs={'class':'app-left-column-related-snippet-container rendered-app-snippet'})
        i = 0
        for div in div_fa:
            i = i + 1
            if div.has_key('data-docid'):
                also_app_id = div['data-docid']
                db_app.db_execute_g(db_sql.sql_related_install_insert, (app_id, also_app_id, i, ))
                print '\t', i, also_app_id

def related_install(app_id, soup):
    divs_fa = soup.find_all(name='div', attrs={'data-analyticsid':'users-also-installed'})
    for divs in divs_fa:
        div_fa = divs.find_all(name='div', attrs={'class':'app-left-column-related-snippet-container rendered-app-snippet'})
        i = 0
        for div in div_fa:
            i = i + 1
            if div.has_key('data-docid'):
                also_app_id = div['data-docid'].strip()
                db_app.db_execute_g(db_sql.sql_related_view_insert, (app_id, also_app_id, i, ))
                print '\t', i, also_app_id

def db_merge_related(db1, db2):
    print '* merge related from %s to %s *'%(db1, db2)
    conn_db1 = sqlite3.connect(db1)
    conn_db2 = sqlite3.connect(db2)
    c1 = conn_db1.cursor()
    c2 = conn_db2.cursor()
    sql1 = '''SELECT app_id, read_status, scrape_create_date, scrape_update_date FROM related'''
    c1.execute(sql1, ())
    rows = c1.fetchall()
    i_t = len(rows)
    i = 0
    p = 0
    for row in rows:
        app_id = row[0]
        read_status = row[1]
        scrape_create_date = row[2]
        scrape_update_date = row[3]
        sql2 = '''INSERT OR REPLACE INTO related (app_id, read_status, scrape_create_date, scrape_update_date) VALUES (?,?,?,?)'''
        c2.execute(sql2, (app_id, read_status, scrape_create_date, scrape_update_date, ))
        conn_db2.commit()
        p, i = util.p_percent(p, i, i_t, 1)
    c1.close()
    c2.close()

def db_merge_related_view(db1, db2):
    print '* merge related_view from %s to %s *'%(db1, db2)
    conn_db1 = sqlite3.connect(db1)
    conn_db2 = sqlite3.connect(db2)
    c1 = conn_db1.cursor()
    c2 = conn_db2.cursor()
    sql1 = '''SELECT app_id, also_app_id, place FROM related_view'''
    c1.execute(sql1, ())
    rows = c1.fetchall()
    i_t = len(rows)
    i = 0
    p = 0
    for row in rows:
        app_id = row[0]
        also_app_id = row[1]
        place = row[2]
        sql2 = '''INSERT OR IGNORE INTO related_view (app_id, also_app_id, place) VALUES (?,?,?)'''
        c2.execute(sql2, (app_id, also_app_id, place, ))
        conn_db2.commit()
        p, i = util.p_percent(p, i, i_t, 1)
    c1.close()
    c2.close()

def db_merge_related_install(db1, db2):
    print '* merge related_install from %s to %s *'%(db1, db2)
    conn_db1 = sqlite3.connect(db1)
    conn_db2 = sqlite3.connect(db2)
    c1 = conn_db1.cursor()
    c2 = conn_db2.cursor()
    sql1 = '''SELECT app_id, also_app_id, place FROM related_install'''
    c1.execute(sql1, ())
    rows = c1.fetchall()
    i_t = len(rows)
    i = 0
    p = 0
    for row in rows:
        app_id = row[0]
        also_app_id = row[1]
        place = row[2]
        sql2 = '''INSERT OR IGNORE INTO related_install (app_id, also_app_id, place) VALUES (?,?,?)'''
        c2.execute(sql2, (app_id, also_app_id, place, ))
        conn_db2.commit()
        p, i = util.p_percent(p, i, i_t, 1)
    c1.close()
    c2.close()


def db_merge_main(db1, db2):
    db_merge_related(db1, db2)
    print 
    db_merge_related_view(db1, db2)
    print 
    db_merge_related_install(db1, db2)


if __name__ == '__main__':
    db_init()
    #related_merge()
    #related_read_main()
    db_merge_main('./db_app_related.db', db_app.db_path)
    
