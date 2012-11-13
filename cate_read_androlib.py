import httplib
import json
from bs4 import BeautifulSoup
import bs4
import urlparse
import urllib
from datetime import datetime
import http
import db_sql
import db_lib
import err
import time
import util

lib_host_http = 'www.androlib.com'
lib_headers_http = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
lib_root = 'watch'
# http, comment if using proxy
'''
lib_conn_http = http.get_conn_http(lib_host_http)
def lib_http_get(url):
    global lib_conn_http
    global lib_host_http
    print lib_host_http, '==='
    if lib_conn_http == None:
        lib_conn_http = http.get_conn_http(lib_host_http)
    status, body, lib_conn_http = http.use_httplib_http(url, 'GET', '', lib_conn_http, lib_host_http, lib_headers_http)
    return status, body
def lib_http_post(url, url_body):
    global lib_conn_http
    global lib_host_http
    if lib_conn_http == None:
        lib_conn_http = http.get_conn_http(lib_host_http)
    status, body, lib_conn_http = http.use_httplib_http(url, 'POST', url_body, lib_conn_http, lib_host_http, lib_headers_http)
    return status, body
'''

# http proxy, comment if not using proxy
lib_conn_http = http.get_conn_http_proxy(lib_host_http)
def host_http_proxy():
    global lib_host_http
    url_proxy = 'http://%s'%lib_host_http
    return url_proxy
def lib_http_get(url):
    global lib_conn_http
    global lib_host_http
    #print lib_host_http, '==='
    if lib_conn_http == None:
        #print lib_conn_http, 'None'
        lib_conn_http = http.get_conn_http_proxy(lib_host_http)
    url_proxy = host_http_proxy()
    #print url_proxy, 'url_proxy'
    status, body, lib_conn_http = http.use_httplib_http_proxy(url, 'GET', '', lib_conn_http, url_proxy, lib_headers_http)
    return status, body
def lib_http_post(url, url_body):
    global lib_conn_http
    global lib_host_http
    if lib_conn_http == None:
        lib_conn_http = http.get_conn_http_proxy(lib_host_http)
    url_proxy = host_http_proxy()
    status, body, lib_conn_http = http.use_httplib_http_proxy(url, 'POST', url_body, lib_conn_http, url_proxy, lib_headers_http)
    return status, body




def db_init():
    db_lib.db_init()

####################
def language_read_main():
    url = '/'
    print '** language option %s **'%(url)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('lib lang htp error %s'%(str(status)))
    soup = BeautifulSoup(body)
    divs = soup.find_all(name='div', attrs={'class':'flagt'})
    for div in divs:
        for d in div:
            if d.name == 'a' and d.has_key('href'):
                lang_href = d['href'].strip()
                lang_title = d['title'].strip()
                db_lib.db_execute_g(db_sql.sql_lib_lang_insert, (lang_href, lang_title, str(datetime.now())))


def home_read_main():
    global lib_host_http
    global lib_conn_http
    rows = db_lib.db_get_g(db_sql.sql_lib_lang_get, ())
    for row in rows:
        lang_href = row[0]
        lang_title = row[1]
        lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
        lib_conn_http = http.get_conn_http(lib_host_http)
        ''' # if working on horizon pc, uncommit this if and commit above two lines. 
        if lib_host_http != lang_href.replace('http://', '').replace('/', '').strip():
            lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
            lib_conn_http = http.get_conn_http(lib_host_http)
        '''
        try:
            home_read(lang_href)
            db_lib.db_execute_g(db_sql.sql_lib_lang_update, (lang_href,))
            util.sleep_i(1)
        except Exception as e:
            err.except_p(e)
        #print '======='
        #break
                
def home_read(lang_href):
    url = '/' ### looks like proxy needs to have /
    print '** home %s | %s **'%(url, lang_href)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('lib home_read http error %s'%str(status))
    soup = BeautifulSoup(body)
    menu_fa = soup.find_all(name='a', attrs={'class':'menulink'})
    if len(menu_fa) != 2:
        raise Exception('lib home_read len(menu_fa) != 2')
    for menu_f in menu_fa:
        if menu_f.has_key('href'):
            menu_href = menu_f['href'].strip()
            menu_name = menu_f.text.strip()
            #print menu_name, menu_href
            db_lib.db_execute_g(db_sql.sql_lib_lang_cate_insert, (lang_href, menu_href, menu_name, str(datetime.now())))
    
def home_read_test():
    global lib_host_http
    global lib_conn_http
    print lib_host_http, lib_conn_http

def home_read_max_main():
    global lib_host_http
    global lib_conn_http
    rows = db_lib.db_get_g(db_sql.sql_lib_lang_cate_get, ())
    for row in rows:
        lang_href = row[0]
        cate_path = row[1]
        cate_title = row[2]
        cate_param_max = row[3]
        lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
        lib_conn_http = http.get_conn_http(lib_host_http)
        ''' # if working on horizon pc, uncommit this if, otherwise, commit above two lines. 
        if lib_host_http != lang_href.replace('http://', '').replace('/', '').strip():
            lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
            lib_conn_http = http.get_conn_http(lib_host_http)
        '''
        try:
            home_read_max(lang_href, cate_path, cate_title)
        except Exception as e:
            err.except_p(e)
        print '======='

def home_read_max(lang_href, menu_href, menu_name):        
    url = menu_href
    print '** home cate max %s %s **'%(menu_name, url)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('lib home_read_sub http error %s'%(str(status)))
    soup = BeautifulSoup(body)
    div_fa = soup.find_all(name='div', attrs={'class':'itmCatLstContent'})
    if len(div_fa) > 0:
        div_f = div_fa[0]
        if div_f.a != None and div_f.a.has_key('href'):
            cate_href = div_f.a['href'].strip()
            cate_name = div_f.a.text.strip()
            p_num_read(lang_href, menu_href, cate_href, cate_name)
            util.sleep_i(1)

def p_num_read(lang_href, menu_href, cate_href, cate_name):
    url = '%s'%(cate_href)
    print '** cate page max p_num %s %s **'%(cate_name, url)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('=== p_num_read http error %s '%(str(status)))
    soup = BeautifulSoup(body)
    last_fa = soup.find_all(name='div', attrs={'class':'pg_suiv'})
    if len(last_fa) <= 0:
        raise Exception('p_num_read len(last_fa) <= 0')
    last_ps = []
    last_next = -1
    last_final = -1
    for last_f in last_fa:
        last_a_fa = last_f.find_all(name='a')
        for last_a in last_a_fa:
            if last_a.has_key('href'):
                last_a_href = last_a['href'].strip()
                last_a_qs = urlparse.urlparse(last_a_href).query
                last_a_num = urlparse.parse_qs(last_a_qs)
                if last_a_num.has_key('p') and len(last_a_num['p'])>0:
                    last_p = last_a_num['p'][0]
                    last_ps.append(int(last_p))
        last_ps.sort()
    if len(last_ps) == 2:
        last_next = last_ps[0]
        last_final = last_ps[1]
    if last_final == -1:
        raise Exception('lib p_num_read last_final == -1')
    for i in range(0, last_final+1):
        db_lib.db_execute_g(db_sql.sql_lib_lang_cate_read_insert, (lang_href, cate_href, i, str(datetime.now())))
    db_lib.db_execute_g(db_sql.sql_lib_lang_cate_update, (last_final, lang_href, menu_href)) # becareful the menu_href here is different to cate_href
    print last_ps, last_next, last_final

def cate_read_main():
    global lib_host_http
    global lib_conn_http
    rows = db_lib.db_get_g(db_sql.sql_lib_lang_cate_read_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t), 
        lang_href = row[0]
        cate_path = row[1]
        cate_param = row[2]
        if lib_host_http != lang_href.replace('http://', '').replace('/', '').strip():
            lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
            lib_conn_http = http.get_conn_http(lib_host_http)
        try:
            cate_read(lang_href, cate_path, cate_param)
            util.sleep_i(1)
        except Exception as e:
            err.except_p(e)
        

def cate_read(lang_href, cate_path, cate_param):
    url = '%s?p=%s'%(cate_path, cate_param)
    print '** lib cate_read %s **'%(url)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('lib cate_read http error %s'%(str(status)))
    soup = BeautifulSoup(body)
    a_fa = soup.find_all(name='a', attrs={'class':'asLsttitle'})
    for a_f in a_fa:
        if a_f.has_key('href'):
            link_href = a_f['href'].strip()
            link_name = a_f.text.strip()
            link_id = '0'
            if a_f.has_key('id'):
                link_id = a_f['id'].strip()
            #print link_href, link_name
            db_lib.db_execute_g(db_sql.sql_lib_lang_cate_link_read_insert, (lang_href, cate_path, cate_param, link_href, link_name, link_id))
    db_lib.db_execute_g(db_sql.sql_lib_lang_cate_read_update, (lang_href, cate_path, cate_param))

def cate_link_read_main():
    global lib_host_http
    global lib_conn_http
    rows = db_lib.db_get_g(db_sql.sql_lib_lang_cate_link_read_get, ())
    for row in rows:
        lang_href = row[0]
        cate_path = row[1]
        cate_param = row[2]
        link_href = row[3]
        if lib_host_http != lang_href.replace('http://', '').replace('/', '').strip():
            lib_host_http = lang_href.replace('http://', '').replace('/', '').strip()
            lib_conn_http = http.get_conn_http(lib_host_http)
        try:
            cate_link_read(link_href, lang_href, cate_path, cate_param)
            util.sleep_i(1)
        except Exception as e:
            err.except_p(e)
        
def cate_link_read(link_href, lang_href, cate_path, cate_param):
    url = link_href
    print '** lib cate_link_read %s **'%(url)
    status, body = lib_http_get(url)
    if status != 200:
        raise Exception('lib cate_read http error %s'%(str(status)))
    ### edit bellow
    soup = BeautifulSoup(body)
    div_fa = soup.find_all(name='div', attrs={'class':'ui-widget-content ui-corner-all assetextra'})
    for div_f in div_fa:
        b_fa = div_f.find_all(name='b')
        if len(b_fa)>3:
            b_f = b_fa[2]
            app_id = b_f.text.strip()
            db_lib.db_execute_g(db_sql.sql_app_insert, (app_id,))
            db_lib.db_execute_g(db_sql.sql_lib_lang_cate_link_read_update, (app_id, lang_href, cate_path, cate_param))
            print app_id


def main():
    db_init()
    try:
        language_read_main() ## comment this if run after first time
        home_read_main() ## comment this if run after first time
        home_read_max_main() ## comment this if run after first time
        cate_read_main()
        cate_link_read_main()
    except Exception as e:
        err.except_p(e)

    
        
if __name__  == '__main__':
    main()
