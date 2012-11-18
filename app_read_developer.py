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
import db_developer

def db_init():
    db_developer.db_init()
    db_app.db_init()

def developer_merge():
    rows = db_app.db_get_g(db_sql.sql_developer_merge_get, ())
    i_t = len(rows)
    print '** start to merge developer test list %d from %s to %s **'%(i_t, db_app.db_path, db_developer.db_path)
    i = 0 
    p = 0
    db = db_developer.db
    c = db.cursor()
    for row in rows:
        developer_href = row[0]
        developer_website = row[1]
        c.execute(db_sql.sql_developer_merge_insert, (developer_href, developer_website, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

def developer_read_store_main():
    finish = True
    rows = db_developer.db_get_g(db_sql.sql_developer_read_store_get, ())
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
            db_developer.db_execute_g(db_sql.sql_developer_store_read_status_update, (developer_href, )) 
            return False
        if status != 200:
            raise Exception('app read https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        developer_read_store_website(developer_href, soup)
        developer_read_store_app(developer_href, soup)
        db_developer.db_execute_g(db_sql.sql_developer_store_start_num_update, (start_num, developer_href,)) ## record this page has been successfully read
        return True
    except Exception as e:
        err.except_p(e)
        return False

def developer_read_store_app(developer_href, soup):
    apps_fa = soup.find_all(name='li', attrs={'class':'goog-inline-block'})
    for li in apps_fa:
        if li.has_key('data-docid'):
            app_id = li['data-docid'].strip()
            db_developer.db_execute_g(db_sql.sql_developer_app_insert, (developer_href, app_id, ))
            print '\t%s'%(app_id)

def developer_read_store_website(developer_href, soup):
    website_fa = soup.find_all(name='div', attrs={'class':'developer-website'})
    if len(website_fa) == 1:
        website_f = website_fa[0]
        if website_f.a != None:
            if website_f.a.has_key('href'):
                developer_website = website_f.a['href'].strip()
                db_developer.db_execute_g(db_sql.sql_developer_website_update, (developer_website, developer_href, ))
                #print developer_website


############ developer external web site check, it does not need to within google player page 
## developer merge 
def website_merge():
    rows = db_developer.db_get_g(db_sql.sql_developer_website_merge_get, ())
    i_t = len(rows)
    print '** start to merge developer social %d **'%(i_t)
    i = 0
    p = 0
    db = db_developer.db
    c = db.cursor()
    for row in rows:
        developer_website = row[0]
        c.execute(db_sql.sql_developer_website_merge_insert, (developer_website, ))
        p, i = util.p_percent_copy(p, i, i_t, 5, db)
    db.commit()
    c.close()

def website_read_main():
    print 'start'
    rows = db_developer.db_get_g(db_sql.sql_developer_website_read_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t), 
        developer_website = row[0]
        website_qs = urlparse.urlparse(developer_website.strip()).query
        website_q = urlparse.parse_qs(website_qs)
        if website_q.has_key('q') and len(website_q['q'])>0:
            real_href = website_q['q'][0].strip()
            db_developer.db_execute_g(db_sql.sql_developer_website_real_href_update, (real_href, developer_website, ))
            if len(real_href) < 8:
                db_developer.db_execute_g(db_sql.sql_developer_website_read_status_update, (developer_website, ))
                continue
            print real_href
            if 'facebook.com' in real_href:
                db_developer.db_execute_g(db_sql.sql_developer_website_facebook_update, (real_href, developer_website, ))
                continue
            if 'twitter.com' in real_href:
                db_developer.db_execute_g(db_sql.sql_developer_website_twitter_update, (real_href, developer_website, ))
                continue
            if 'plus.google.com' in real_href:
                db_developer.db_execute_g(db_sql.sql_developer_website_google_plus_update, (real_href, developer_website, ))
                continue
            if 'youtube.com' in real_href:
                db_developer.db_execute_g(db_sql.sql_developer_website_youtube_update, (real_href, developer_website, ))
                continue
            website_read(developer_website, real_href)
            #break

import urllib2
import re
import mechanize
br = mechanize.Browser()
#br.set_proxies({"http": "joe:password@myproxy.example.com:3128","ftp": "proxy.example.com",}) # proxy example 
#br.set_proxies({'http':''})
br.set_handle_refresh(True)
br.set_handle_robots(False)
#br.set_debug_redirects(True)
#br.set_debug_http(True)

def website_read(developer_website, real_href):
    url = real_href
    try:
        resp = br.open(url)
        #print '** redirect:', br.geturl()
        body = resp.read()
        soup = BeautifulSoup(body)
        website_twitter(developer_website, soup)
        website_facebook(developer_website, soup)
        website_youtube(developer_website, soup)
        website_google_plus(developer_website, soup)
        db_developer.db_execute_g(db_sql.sql_developer_website_read_status_update, (developer_website, ))
        br.clear_history()
    except urllib2.URLError as e:  #### need to fingure out error handler
        err.except_p(e)
    except urllib2.HTTPError as e:
        err.except_p(e)

def website_twitter(developer_website, soup):
    hrefs = ''
    href_fa = soup.find_all(href=re.compile('twitter.com'))
    for href_f in href_fa:
        if href_f.has_key('href'):
            href = href_f['href']
            hrefs = '%s:%s'%(hrefs, href)
            print '\t%s'%href
    #print hrefs
    db_developer.db_execute_g(db_sql.sql_developer_website_twitter_update, (hrefs, developer_website, ))

def website_facebook(developer_website, soup):
    hrefs = ''
    href_fa = soup.find_all(href=re.compile('facebook.com'))
    for href_f in href_fa:
        if href_f.has_key('href'):
            href = href_f['href']
            hrefs = '%s:%s'%(hrefs, href)
            print '\t%s'%href
    #print hrefs
    db_developer.db_execute_g(db_sql.sql_developer_website_facebook_update, (hrefs, developer_website, ))

def website_youtube(developer_website, soup):
    hrefs = ''
    href_fa = soup.find_all(href=re.compile('youtube.com'))
    for href_f in href_fa:
        if href_f.has_key('href'):
            href = href_f['href']
            hrefs = '%s:%s'%(hrefs, href)
            print '\t%s'%href
    #print hrefs
    db_developer.db_execute_g(db_sql.sql_developer_website_youtube_update, (hrefs, developer_website, ))

def website_google_plus(developer_website, soup):
    hrefs = ''
    href_fa = soup.find_all(href=re.compile('plus.google.com'))
    for href_f in href_fa:
        if href_f.has_key('href'):
            href = href_f['href']
            hrefs = '%s:%s'%(hrefs, href)
            print '\t%s'%href
    #print hrefs
    db_developer.db_execute_g(db_sql.sql_developer_website_google_plus_update, (hrefs, developer_website, ))

#### db merge 
def db_merge_developer():
    rows = db_developer.db_get_g(db_sql.sql_merge_developer_app_get_developer, ())
    i_t = len(rows)
    print '* merge developer from %s to %s %d *'%(db_developer.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        developer_href = row[0]
        start_num = row[1]
        store_read_status = row[2]
        developer_website = row[3]
        scrape_create_date = row[4]
        scrape_update_date = row[5]
        c.execute(db_sql.sql_merge_developer_app_insert_developer, (developer_href, start_num, store_read_status, developer_website, scrape_create_date, scrape_update_date, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

def db_merge_developer_app():
    rows = db_developer.db_get_g(db_sql.sql_merge_developer_app_get_developer_app, ())
    i_t = len(rows)
    print '* merge developer_app from %s to %s %d *'%(db_developer.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        developer_href = row[0]
        app_id = row[1]
        c.execute(db_sql.sql_merge_developer_app_insert_developer_app, (developer_href, app_id ))
        c.execute(db_sql.sql_app_insert, (app_id, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

def db_merge_developer_social():
    rows = db_developer.db_get_g(db_sql.sql_merge_developer_app_get_developer_social, ())
    i_t = len(rows)
    print '* merge developer_social from %s to %s %d *'%(db_developer.db_path, db_app.db_path, i_t)
    i = 0
    p = 0
    db = db_app.db
    c = db.cursor()
    for row in rows:
        developer_website = row[0]
        real_href = row[1]
        twitter_href = row[2]
        facebook_href = row[3]
        google_plus_href = row[4]
        youtube_href = row[5]
        website_read_status = row[6]
        scrape_create_date = row[3]
        scrape_update_date = row[4]
        c.execute(db_sql.sql_merge_developer_app_insert_developer_social, (developer_website, real_href, twitter_href, facebook_href, google_plus_href, youtube_href, website_read_status, scrape_create_date, scrape_update_date, ))
        p, i = util.p_percent_copy(p, i, i_t, 1, db)
    db.commit()
    c.close()

    

def from_developer_to_app_developer():
    db_init()
    developer_merge()
    #developer_read_store_main()

def from_app_to_developer_developer():
    db_init()
    db_merge_developer()
    db_merge_developer_app()

def from_developer_to_app_website():
    db_init()
    website_merge()
    website_read_main()

def from_app_to_developer_website():
    db_init()
    db_merge_developer_social()


if __name__ == '__main__':
    #from_developer_to_app_developer()
    from_app_to_developer_developer()
    #
    #from_developer_to_app_website()
    #from_app_to_developer_website()
