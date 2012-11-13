import db_sql
import db_app
import http
import urllib
import err
from bs4 import BeautifulSoup
from datetime import datetime
import util

youtube_host_http = 'www.youtube.com'
youtube_conn_http = http.get_conn_http(youtube_host_http)
youtube_headers_http = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
youtube_root = 'watch'
######### http without proxy

def youtube_http_get(url):
    global youtube_conn_http
    if youtube_conn_http == None:
        youtube_conn_http = http.get_conn_http(youtube_host_http)
    status, body, youtube_conn_http = http.use_httplib_http(url, 'GET', '', youtube_conn_http, youtube_host_http, youtube_headers_http)
    return status, body
def youtube_http_post(url, url_body):
    global youtube_conn_http
    if youtube_conn_http == None:
        youtube_conn_http = http.get_conn_http(youtube_host_http)
    status, body, youtube_conn_http = http.use_httplib_http(url, 'POST', url_body, youtube_conn_http, youtube_host_http, youtube_headers_http)
    return status, body
'''
# http proxy here: if not in proxy, please comment thsese lines
youtube_conn_http = http.get_conn_http_proxy(youtube_host_http)
def host_http_proxy ():
    global youtube_host_http
    url_proxy = 'http://%s'%youtube_host_http
    return url_proxy
def youtube_http_get(url):
    global youtube_conn_http
    if youtube_conn_http == None:
        youtube_conn_http = http.get_conn_http_proxy(youtube_host_http)
    url_proxy = host_http_proxy()
    status, body, youtube_conn_http = http.use_httplib_http_proxy(url, 'GET', '', youtube_conn_http, url_proxy, youtube_headers_http)
    return status, body
def youtube_http_post(url, url_body):
    global youtube_conn_http
    if youtube_conn_http == None:
        youtube_conn_http = http.get_conn_http_proxy(youtube_host_http)
    url_proxy = host_http_proxy()
    status, body, youtube_conn_http = http.use_httplib_http_proxy(url, youtube_url_proxy, 'POST', url_body, youtube_conn_http, url_proxy, youtube_headers_http)
    return status, body
'''



################
def video_read_main():
    finish = True
    rows = db_app.db_get_g(db_sql.sql_video_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t), 
        finish = False
        app_id = row[0]
        video_href = row[1]
        view_total = row[2]
        video_href_d = video_href.split('/')[-1]
        video_id = video_href_d.split('?')[0].strip()
        try:
            video_read(video_id, app_id, video_href)
            util.sleep()
        except Exception as e:
            err.except_p(e)
    return finish

def video_read(video_id, app_id, video_href):
    view_total = ''
    view_likes = ''
    view_dislikes = ''
    comments = ''
    param = {
        'v':video_id,
        }
    url_body = urllib.urlencode(param)
    url = '/%s?%s'%(youtube_root, url_body)
    print '** youtube : %s **'%(url)
    status, body = youtube_http_get(url)
    if status == 404:
        db_app.db_execute_g(db_sql.sql_video_update_404, (str(datetime.now()), 1, app_id, video_href))
        return 
    if status != 200:
        raise Exception('youtube http connection status:%s'%(str(status)))
    soup = BeautifulSoup(body)
    view_total_fa = soup.find_all(name='span', attrs={'class':'watch-view-count'})
    for view_total_f in view_total_fa:
        if view_total_f.strong != None and view_total_f.strong.text != None:
            view_total = view_total_f.strong.text.strip()
    view_likes_fa = soup.find_all(name='span', attrs={'class':'likes'})
    for view_likes_f in view_likes_fa:
        view_likes = view_likes_f.text.strip()
    view_dislikes_fa = soup.find_all(name='span', attrs={'class':'dislikes'})
    for view_dislikes_f in view_dislikes_fa:
        view_dislikes = view_dislikes_f.text.strip()
    comments_fa = soup.find_all(name='span', attrs={'class':'comments-section-stat'})
    for comments_f in comments_fa:
        comments = comments_f.text.replace('(', '').replace(')', '').strip()
    print view_total, view_likes, view_dislikes, comments
    db_app.db_execute_g(db_sql.sql_video_update, (view_total, view_likes, view_dislikes, comments, str(datetime.now()), 1, app_id, video_href))
    

def main():
    db_app.db_init()
    finish = False
    while finish == False:
        try:
            finish = video_read_main()
        except Exception as e:
            err.except_p(e)
                        

if __name__ == '__main__':
    main()
