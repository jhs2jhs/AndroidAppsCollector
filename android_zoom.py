import httplib
import json
from bs4 import BeautifulSoup
import bs4
import urlparse
import urllib
from datetime import datetime
import http
import db
import err
import time
import util

zoom_host_http = 'www.androidzoom.com'
zoom_conn_http = http.get_conn_http(zoom_host_http)
zoom_headers_http = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
zoom_root = 'watch'
def zoom_http_get(url):
    global zoom_conn_http
    if zoom_conn_http == None:
        zoom_conn_http = http.get_conn_http(zoom_host_http)
    status, body, zoom_conn_http = http.use_httplib_http(url, 'GET', '', zoom_conn_http, zoom_host_http, zoom_headers_http)
    return status, body
def zoom_http_post(url, url_body):
    global zoom_conn_http
    if zoom_conn_http == None:
        zoom_conn_http = http.get_conn_http(zoom_host_http)
    status, body, zoom_conn_http = http.use_httplib_http(url, 'POST', url_body, zoom_conn_http, zoom_host_http, zoom_headers_http)
    return status, body


####################
def categories_read_main():
    url = '/'
    print '** categories main %s **'%(url)
    status, body = zoom_http_get(url)
    if status != 200:
        raise Exception('zoom app home http connection errir:%s'%(str(status)))
    soup = BeautifulSoup(body)
    divs = soup.body.find_all(name='div', attrs={'id':'categories-list'})
    for div in divs:
        for d in div:
            if d.name.strip() != 'div':
                continue
            cate_group_name = d.h3.text.strip()
            ul = d.ul
            for li in ul:
                if li.a != None and li.a.has_key('href'):
                    cate_name = li.a.text.strip()
                    cate_path = li.a['href'].strip()
                    print cate_group_name, cate_name, cate_path
                    db.db_execute_g(db.sql_zoom_cate_insert, (cate_group_name, cate_name, cate_path, str(datetime.now())))
                    db.db_execute_g(db.sql_zoom_cate_read_insert, (cate_name, cate_path, '0', ))

def category_read_main():
    finish = True
    rows = db.db_get_g(db.sql_zoom_cate_read_get, ())
    for row in rows:
        finish = True
        cate_name = row[0]
        cate_path = row[1]
        cate_param = row[2]
        category_read(cate_name, cate_path, cate_param)
        break
        
def category_read(cate_name, cate_path, cate_param):
    status = 200
    while status == 200:
        url = '%s/?p=%s'%(cate_path, cate_param)
        print '** zoom category %s %s **'%(cate_param, cate_path)
        status, body = zoom_http_get(url)
        if status == 404:
            print '==: %s '%(str(status))
            break
        if status != 200:
            raise Exception('zoom app category https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        ul_fa = soup.find_all(name='ul', attrs={'id':'apps-list'})
        for li_f in ul_fa:
            a_fa = li_f.find_all(name='a', attrs={'class':'goTo'})
            print len(a_fa)
            for a_f in a_fa:
                if a_f.has_key('href'):
                    a_href = a_f['href'].strip()
                    a_title = a_f.text.strip()
                    db.db_execute_g(db.sql_zoom_app_insert, (a_title, a_href, ))
        cate_param = str(int(cate_param)+10)
        # update cate_param
        break
    print cate_path
    
    

if __name__  == '__main__':
    db.db_init()
    #categories_read_main()
    category_read_main()
