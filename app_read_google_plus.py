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
       
plus_host_https = 'plusone.google.com'
plus_conn_https = http.get_conn_https(plus_host_https)
plus_headers_https = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
def plus_https_get(url):
    global plus_conn_https
    if plus_conn_https == None:
        plus_conn_https = http.get_conn_https(plus_host_https)
    status, body, plus_conn_https = http.use_httplib_https(url, 'GET', '', plus_conn_https, plus_host_https, plus_headers_https)
    return status, body
def plus_https_post(url, url_body):
    global plus_conn_https
    if plus_conn_https == None:
        plus_conn_https = http.get_conn_https(plus_host_https)
    status, body, plus_conn_https = http.use_httplib_https(url, 'POST', url_body, plus_conn_https, plus_host_https, plus_headers_https)
    return status, body

###################
def google_plus_read_main():
    finish = True
    rows = db_app.db_get_g(db_sql.sql_app_google_plus_get, ())
    for row in rows:
        finish = False
        app_id = row[0]
        google_plus_href = row[1]
        try:
            google_plus_read(app_id, google_plus_href, )
            util.sleep()
        except Exception as e:
            err.except_p(e)

def google_plus_read(app_id, google_plus_href):
    params = {
        'url':google_plus_href,
        }
    param = urllib.urlencode(params)
    url = '/u/0/_/+1/fastbutton?%s'%(param)
    #print param, url
    status, body = plus_https_get(url)
    if status == 404:
        print '==: 404'
        db_app.db_execute_g(db_sql.sql_app_google_plus_update, ('-1', str(datetime.now()), app_id, google_plus_href, ))
        return
    if status != 200:
        raise Exception('app google plus https connection error: %s'%(str(status)))
    soup = BeautifulSoup(body)
    div_fa = soup.find_all(name='div', attrs={'id':'aggregateCount'})
    for div_f in div_fa:
        google_plus_figure = div_f.text.strip()
        print google_plus_figure
        db_app.db_execute_g(db_sql.sql_app_google_plus_update, (google_plus_figure, str(datetime.now()), app_id, google_plus_href, ))

    
def main():
    db_app.db_init()
    finish = False
    while finish == False:
        try:
            finish = google_plus_read_main()
        except Exception as e:
            err.except_p(e) 

if __name__ == '__main__':
    main()
