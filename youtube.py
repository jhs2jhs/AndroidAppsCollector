import db
import http
import urllib

youtube_host_http = 'www.youtube.com'
youtube_conn_http = http.get_conn_http(youtube_host_http)
youtube_headers_http = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Language": "en-UK"}
youtube_root = 'watch'
def youtube_http_get(url):
    global youtube_conn_http
    status, body, youtube_conn_http = http.use_httplib_http(url, 'GET', '', youtube_conn_http, youtube_host_http, youtube_headers_http)
    return status, body
def youtube_http_post(url, url_body):
    global youtube_conn_http
    status, body, youtube_conn_http = http.use_httplib_http(url, 'POST', url_body, youtube_conn_http, youtube_host_http, youtube_headers_http)
    return status, body


################
def video_read():
    rows = db.db_get_g(db.sql_video_get, ())
    for row in rows:
        app_id = row[0]
        video_href = row[1]
        watched = row[2]
        video_href_d = video_href.split('/')[-1]
        video_href_d = video_href_d.split('?')[0].strip()
        param = {
            'v':video_href_d,
            }
        url_body = urllib.urlencode(param)
        url = '/%s?%s'%(youtube_root, url_body)
        status, body = youtube_http_get(url)
        print status, body
        print video_href_d
        break
