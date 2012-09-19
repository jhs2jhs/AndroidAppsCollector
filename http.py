import httplib
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
import urlparse
import urllib

strict = 1
timeout = 120
source_address = None
'''
headers = {
    "Connection":"keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
    #"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept": "application/xml",
    "Accept-Language": "en-US,en;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
}
'''
#headers = {}

# https does not requires proxy configuration
# http requires proxy configuration, please use get_conn_http_proxy

############## http proxy (https does not need proxy setting) in Nottingham University #############
host_proxy = '128.243.253.109'
port_proxy = 8080
def get_conn_http_proxy(host):
    conn = httplib.HTTPConnection(host=host_proxy, port=port_proxy, strict=strict, timeout=timeout, source_address=source_address)
    return conn

def use_httplib_http_proxy(url,  method, url_body, conn, url_proxy, headers):
    try:
        if conn == None:
            #print conn, type(conn)
            conn = get_conn_http_proxy(host_proxy)
        url = url_proxy+url
        #print url, 'url'
        conn.request(method=method, url=url, body=url_body, headers=headers)
        status, body = use_httplib_http_resp(conn, headers)
        return status, body, conn
    except Exception as e:
        print '####exception', e, type(conn), conn
        conn.close()
        conn = None
        return -1, e, conn




############# http #############
port_http = 80

def get_conn_http(host):
    conn = httplib.HTTPConnection(host=host, port=port_http, strict=strict, timeout=timeout, source_address=source_address)
    return conn

def use_httplib_http(url, method, url_body, conn, host, headers):
    try:
        if conn == None:
            print conn, type(conn)
            conn = get_conn_http(host)
        conn.request(method=method, url=url, body=url_body, headers=headers)
        status, body = use_httplib_http_resp(conn, headers)
        return status, body, conn
    except Exception as e:
        print '####exception', e, type(conn), conn
        conn.close()
        conn = None
        return -1, e, conn

def use_httplib_redirect(host, url, headers):
    print host, url, "======= redirect ========"
    try:
        conn_c = httplib.HTTPConnection(host=host) # leave port as default
        conn_c.request(method="GET", url=url, headers=headers)
        status, body = use_httplib_http_resp(conn_c, headers)
        conn_c.close()
        return status, body
    except Exception as e:
        print 'exception', e
        return -1, e

def use_httplib_http_resp(conn, headers):
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


############# https #############
port_https = 443

def get_conn_https(host):
    conn = httplib.HTTPSConnection(host=host, port=port_https, strict=strict, timeout=timeout, source_address=source_address)
    return conn

def use_httplib_https(url, method, url_body, conn, host, headers):
    try:
        if conn == None:
            print conn, type(conn)
            conn = get_conn_https(host)
        conn.request(method=method, url=url, body=url_body, headers=headers)
        status, body = use_httplib_https_resp(conn, headers)
        return status, body, conn
    except Exception as e:
        print '####exception', e, type(conn), conn
        conn.close()
        conn = None
        return -1, e, conn

def use_httplib_https_redirect(host, url, headers):
    print host, url, "======= redirect ========"
    try:
        conn_c = httplib.HTTPSConnection(host=host) # leave port as default?
        conn_c.request(method='GET', url=url, headers=headers)
        status, body = use_httplib_https_resp(conn_c, headers)
        conn_c.close()
        return status, body
    except Exception as e:
        print 'exception', e
        return -1, e

def use_httplib_https_resp(conn, headers):
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


if __name__ == '__main__':
    print 'hello'
