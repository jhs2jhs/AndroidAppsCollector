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
import db_related

def db_init():
    db_related.db_init()
    db_app.db_init()

def related_read_merge():
    rows = db_app.db_get_g(db_sql.sql_related_merge_get, ())
    i_t = len(rows)
    print '** start to merge related list %d from %s to %s %d **'%(i_t, db_app.db_path, db_related.db_path, i_t)
    i = 0 
    p = 0
    db = db_related.db
    c = db.cursor()
    for row in rows:
        app_id = row[0]
        c.execute(db_sql.sql_related_merge_insert, (app_id, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
        #print str(p)+'%'+'..',
    db.commit()
    c.close()

def related_read_main():
    finish = True
    rows = db_related.db_get_g(db_sql.sql_related_get, ())
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
            db_related.db_execute_g(db_sql.sql_related_read_update, (1, str(datetime.now()), app_id))
            return 
        if status != 200:
            raise Exception('related read https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        related_view(app_id, soup)
        related_install(app_id, soup)
        db_related.db_execute_g(db_sql.sql_related_read_update, (1, str(datetime.now()), app_id))
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
                db_related.db_execute_g(db_sql.sql_related_view_insert, (app_id, also_app_id, i, ))
                print '\t', i, also_app_id


#### db_merge 
def db_merge_related():
    rows = db_related.db_get_g(db_sql.sql_merge_related_app_get_related, ())
    i_t = len(rows)
    print '* merge related from %s to %s %d *'%(db_related.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        app_id = row[0]
        read_status = row[1]
        scrape_create_date = row[2]
        scrape_update_date = row[3]
        c.execute(db_sql.sql_merge_related_app_insert_related, (app_id, read_status, scrape_create_date, scrape_update_date, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

def db_merge_related_view():
    rows = db_related.db_get_g(db_sql.sql_merge_related_app_get_related_view, ())
    i_t = len(rows)
    print '* merge related_view from %s to %s %d *'%(db_related.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        app_id = row[0]
        also_app_id = row[1]
        place = row[2]
        c.execute(db_sql.sql_merge_related_app_insert_related_view, (app_id, also_app_id, place,))
        c.execute(db_sql.sql_app_insert, (also_app_id, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

def db_merge_related_install():
    rows = db_related.db_get_g(db_sql.sql_merge_related_app_get_related_install, ())
    i_t = len(rows)
    print '* merge related_install from %s to %s %d *'%(db_related.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        app_id = row[0]
        also_app_id = row[1]
        place = row[2]
        c.execute(db_sql.sql_merge_related_app_insert_related_install, (app_id, also_app_id, place, ))
        c.execute(db_sql.sql_app_insert, (also_app_id, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)


def db_merge_main():
    db_merge_related()
    print 
    db_merge_related_view()
    print 
    db_merge_related_install()


def from_app_to_related(): # to read related
    db_init()
    #related_read_merge()
    related_read_main()

def from_related_to_app():
    db_init()
    db_merge_main()

if __name__ == '__main__':
    #from_app_to_related()
    from_related_to_app()
    
