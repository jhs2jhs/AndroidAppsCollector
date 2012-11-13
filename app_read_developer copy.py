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

def db_init():
    db_app.db_init()

def developer_merge():
    rows = db_app.db_get_g(db_sql.sql_developer_merge_get, ())
    i_t = len(rows)
    print '** start to merge developer list %d **'%(i_t)
    i = 0 
    p = 0
    for row in rows:
        developer_href = row[0]
        developer_website = row[1]
        db_app.db_execute_g(db_sql.sql_developer_merge_insert, (developer_href, developer_website, ))
        p, i = util.p_percent(p, i, i_t, 5)

def developer_read_store_main():
    finish = True
    rows = db_app.db_get_g(db_sql.sql_developer_read_store_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t)
        developer_href = row[0]
        start_num = row[1]
        developer_read_store_loop(developer_href, start_num)
        #return 

def developer_read_store_loop(developer_href, start_num):
    start_num = int(start_num)
    flag = True
    while flag == True:
        flag = developer_read_store(developer_href, start_num)
        start_num = start_num + 12
        util.sleep()

def developer_read_store(developer_href, start_num):
    url = '%s&start=%d&num=12'%(developer_href, start_num)
    print '** developer %s **'%(url)
    try:
        status, body = android_https_get(url)
        if status == 404:
            print '== 404'
            db_app.db_execute_g(db_sql.sql_developer_store_read_status_update, (developer_href, )) 
            return False
        if status != 200:
            raise Exception('app read https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        developer_read_store_website(developer_href, soup)
        developer_read_store_app(developer_href, soup)
        db_app.db_execute_g(db_sql.sql_developer_store_start_num_update, (start_num, developer_href,)) ## record this page has been successfully read
        return True
    except Exception as e:
        err.except_p(e)
        return False

def developer_read_store_app(developer_href, soup):
    apps_fa = soup.find_all(name='li', attrs={'class':'goog-inline-block'})
    #print 'app number: %d'%(len(apps_fa))
    for li in apps_fa:
        if li.has_key('data-docid'):
            app_id = li['data-docid'].strip()
            db_app.db_execute_g(db_sql.sql_developer_app_insert, (developer_href, app_id, ))
            print '\t%s'%(app_id)

def developer_read_store_website(developer_href, soup):
    website_fa = soup.find_all(name='div', attrs={'class':'developer-website'})
    if len(website_fa) == 1:
        website_f = website_fa[0]
        if website_f.a != None:
            if website_f.a.has_key('href'):
                developer_website = website_f.a['href'].strip()
                db_app.db_execute_g(db_sql.sql_developer_website_update, (developer_website, developer_href, ))
                #print developer_website


'''
select * from (
select developer_href, count(*) as c
from app 
where developer_href is not null
group by developer_href ) as a order by a.c

 and developer_href is '/store/apps/developer?id=Tencent+Technology+(Shenzhen)+Company+Ltd.'        
'''


if __name__ == '__main__':
    db_init()
    developer_merge()
    developer_read_store_main()
