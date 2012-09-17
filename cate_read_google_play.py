import httplib
import json
from bs4 import BeautifulSoup
import bs4
import urlparse
import urllib
from datetime import datetime
import http
import db_play
import db_sql
import err
import time
import util

android_host_https = 'play.google.com'
android_conn_https = http.get_conn_https(android_host_https)
android_headers_https = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
android_root = 'store/apps'
android_categories = 'category/APPLICATION'
def android_https_get(url):
    global android_conn_https
    if android_conn_https == None:
        android_conn_https = http.get_conn_https(android_host_https)
    status, body, android_conn_https = http.use_httplib_https(url, 'GET', '', android_conn_https, android_host_https, android_headers_https)
    return status, body
def android_https_post(url, url_body):
    global android_conn_https
    if android_conn_https == None:
        android_conn_https = http.get_conn_https(android_host_https)
    status, body, android_conn_https = http.use_httplib_https(url, 'POST', url_body, android_conn_https, android_host_https, android_headers_https)
    return status, body

def db_init():
    db_play.db_init()

####################
def categories_read_main():
    url = '/%s/%s'%(android_root, android_categories)
    print '** categories main %s **'%(url)
    status, body = android_https_get(url)
    if status != 200:
        raise Exception('app home https connection error: %s'%(str(status)))
    soup = BeautifulSoup(body)
    divs = soup.body.find_all(name='div', attrs={'class':'padded-content3 app-home-nav'})
    for div in divs:
        if len(div.contents) != 2:
            raise Exception('app home nav length != 2')
        h2 = div.contents[0]
        cate_group_name = h2.text.strip()
        ul = div.contents[1]
        lis = ul.find_all(name='li', attrs={'class':'category-item'})
        if len(lis) <= 0:
            raise Exception('app home nav li length <= 0')
        for li in lis:
            a = li.a
            if a == None:
                raise Exception('app home nav li a == None')
            if not a.has_key('href'):
                raise Exception('app home nav li a href has not href')
            cate_path = urlparse.urlparse(a['href']).path.strip()
            cate_name = a.text.strip()
            db_play.db_execute_g(db_sql.sql_cate_insert, (cate_group_name, cate_name, cate_path, str(datetime.now())))
            cate_i = 0
            while cate_i < 504:
                db_play.db_execute_g(db_sql.sql_cate_read_insert, (cate_name, cate_path, cate_i, 'topselling_free'))
                db_play.db_execute_g(db_sql.sql_cate_read_insert, (cate_name, cate_path, cate_i, 'topselling_paid'))
                cate_i = cate_i + 24

def category_read_main():
    finish = True
    rows = db_play.db_get_g(db_sql.sql_cate_read_get, ())
    for row in rows:
        finish = False
        cate_name = row[0]
        cate_path = row[1]
        cate_param = row[2]
        cate_type = row[3]
        try:
            category_read(cate_path, cate_name, cate_type, cate_param)
            db_play.db_execute_g(db_sql.sql_cate_read_update, (cate_name, cate_path, cate_param, cate_type, ))
        except Exception as e:
            err.except_p(e)
        util.sleep()
    return finish
            

def category_read(cate_path, cate_name, cate_type, cate_start):
    url = '%s/collection/%s?start=%s&num=24'%(cate_path, cate_type, cate_start)
    print '** category %s **'%(url)
    status, body = android_https_get(url)
    if status == 404: # not all category would have more 480 items. 
        print '==: %s '%(str(status))
        return 
    if status != 200:
        raise Exception('app category https connection error: %s'%(str(status)))
    soup = BeautifulSoup(body)
    divs = soup.find_all(name='div', attrs={'class':'snippet snippet-medium'})
    for div in divs:
        rank_divs = div.find_all(name='div', attrs={'class':'ordinal-value'})
        if len(rank_divs) != 1:
            raise Exception('category div ordinal-value len != 1')
        rank = rank_divs[0].text.strip()
        href_as = div.find_all(name='a', attrs={'class':'title'})
        if len(href_as) != 1:
            raise Exception('category div a href len != 1')
        if not href_as[0].has_key('href'):
            raise Exception('category div a href is empty')
        href = href_as[0]['href']
        href = urlparse.urlparse(href)
        href_qs = urlparse.parse_qs(href.query)
        href_path = href.path
        href_id = None
        if href_qs.has_key('id') and len(href_qs['id']) > 0:
            href_id = href_qs['id'][0]
        if href_id == None:
            raise Exception('category div a href urlparse wrong')
        app_id = href_id.strip()
        db_play.db_execute_g(db_sql.sql_app_insert_with_rank, (app_id, rank))
    

def main():
    db_init()
    finish = False ## comment this if run after first time
    while finish == False:
        try:
            categories_read_main()
            finish = category_read_main()
        except Exception as e:
            err.except_p(e)


if __name__  == '__main__':
    main()

