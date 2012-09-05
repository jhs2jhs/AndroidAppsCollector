import httplib
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
import urlparse

host = 'play.google.com'
android_root = 'store/apps'
android_categories = 'category/APPLICATION'

port_http = 80
port_https = 443
strict = 1
timeout = 10
source_address = None
headers = {
    "Connection":"keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
    #"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept": "application/xml",
    "Accept-Language": "en-US,en;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
}
headers = {}

def get_conn_https(host):
    conn = httplib.HTTPSConnection(host=host, port=port_https, strict=strict, timeout=timeout, source_address=source_address)
    return conn

conn = get_conn_https(host)

def use_httplib_https(url, host, headers):
    global conn
    try:
        if conn == None:
            print conn, type(conn)
            conn = get_conn_https(host)
        conn.request(method='GET', url=url, headers=headers)
        #print '**ready'
        status, body = use_httplib_https_resp(conn)
        return status, body
    except Exception as e:
        print '####exception', e, type(conn), conn
        conn.close()
        conn = None
        return -1, e

def use_httplib__https_redirect(host, url, headers):
    print host, url, "======= redirect ========"
    try:
        conn_c = httplib.HTTPSConnection(host=host) # leave port as default?
        conn_c.request(method="GET", url=url, headers=headers)
        status, body = use_httplib_https_resp(conn)
        conn_c.close()
        return status, body
    except Exception as e:
        print 'exception', e
        return -1, e

def use_httplib_https_resp(conn):
    resp = conn.getresponse()
    #print "*//togo"
    status_resp = resp.status
    reason_resp = resp.reason
    headers_resp = resp.getheaders() 
    #print headers_resp
    if 300 <= status_resp < 400 : # redirect
        location = resp.getheader('Location')
        parsed = urlparse.urlparse(location)
        host_r = parsed.netloc
        url_r = parsed.path
        if location != None: # return None if it is not exist
            return use_httplib_https_redirect(host_r, url_r, headers)
        else:
            return status_resp, 'Location is None:'
    msg_resp = resp.msg
    body_resp = resp.read()
    v_resp = resp.version
    return status_resp, body_resp


def categories_read():
    url = '/%s/%s'%(android_root, android_categories)
    print '** categories main %s **'%(url)
    status, body = use_httplib_https(url, host, headers)
    if status != 200:
        raise Exception('app home https connection error')
    soup = BeautifulSoup(body)
    divs = soup.body.find_all(name='div', attrs={'class':'padded-content3 app-home-nav'})
    for div in divs:
        if len(div.contents) != 2:
            raise Exception('app home nav length != 2')
        h2 = div.contents[0]
        cate_main_name = h2.text
        print cate_main_name
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
            cate_path = urlparse.urlparse(a['href']).path
            cate_name = a.text
            print cate_main_name, cate_name, cate_path
            category_read(cate_path, cate_name)

def category_read(cate_path, cate_name):
    url = '%s/%s'(cate_path, 'collection/topselling_free')
    print '** category url **'%(url)
    status, body = use_httplib_https(url, host, headers)
    if status != 200:
        raise Exception('app category https connection error')
    soup = BeautifulSoup(body)
    


if __name__ == '__main__':
    categories_read()
    #a = httplib.HTTPSConnection('')
