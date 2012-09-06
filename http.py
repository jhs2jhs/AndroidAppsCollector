import httplib
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
import urlparse
import urllib

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
            break
        break

def category_read(cate_path, cate_name):
    cate_type = 'topselling_free'
    category_read_base(cate_path, cate_name, cate_type)
    print '====='
    #cate_type = 'topselling_paid'
    #category_read_base(cate_path, cate_name, cate_type)
    print '=='

def category_read_base(cate_path, cate_name, cate_type):
    cate_start = 0
    i = 0
    status = 200
    while status != 403:
         status, cate_current = category_read_loop(cate_path, cate_name, cate_type, cate_start)
         #print status, cate_start, cate_current
         i = i + 1
         cate_start = cate_start + 24
         break
    print status, cate_start, cate_current, cate_path

def category_read_loop(cate_path, cate_name, cate_type, cate_start):
    url = '%s/collection/%s?start=%d&num=24'%(cate_path, cate_type, cate_start)
    #print '** category %s **'%(url)
    status, body = use_httplib_https(url, host, headers)
    #print status
    #print body
    if status == 403:
        #raise Exception('exeet the amount of request')
        return status, cate_start
    if status != 200:
        print '$$$$$$$$$$', status, url
        #raise Exception('app category https connection error')
        return status, cate_start
    soup = BeautifulSoup(body)
    divs = soup.find_all(name='div', attrs={'class':'snippet snippet-medium'})
    for div in divs:
        #print div
        rank_divs = div.find_all(name='div', attrs={'class':'ordinal-value'})
        if len(rank_divs) != 1:
            raise Exception('category div ordinal-value len != 1')
        rank = rank_divs[0].text
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
        app_id = href_id
        #app_url = {'id':href_id}
        #app_url = urllib.urlencode(app_url)
        #app_url = '%s?%s'%(href_path, app_url)
        #print rank, app_url
        app_read(app_id)
        break
    return status, cate_start

def app_read(app_id):
    app_id = 'com.tencent.mm'
    url = '/%s/details?id=%s'%(android_root, app_id)
    print '** app %s **'%(url)
    status, body = use_httplib_https(url, host, headers)
    if status != 200:
        ## exception
        return status, app_id
    soup = BeautifulSoup(body)
    banner_title_fa = soup.find_all(name='td', attrs={'class':'doc-banner-title-container'})
    if len(banner_title_fa) != 1:
        print 'error: banner title '
    banner_title_f = banner_title_fa[0]
    if banner_title_f.h1 == None:
        print 'except'
    banner_title = banner_title_f.h1.text
    if banner_title_f.a == None:
        print 'except'
    if not banner_title_f.a.has_key('href'):
        print 'except'
    banner_developer_href = banner_title_f.a['href']
    if not banner_title_f.a.text == None:
        print 'except'
    banner_developer_name = banner_title_f.a.text
    print banner_title, banner_developer_href, banner_developer_name
    banner_annotation_fa = soup.find_all(name='div', attrs={'class':'badges-badge-title goog-inline-block'})
    for banner_annotation in banner_annotation_fa:
        banner_annotation_text = banner_annotation.text
        print banner_annotation_text
    banner_icon_fa = soup.find_all(name='div', attrs={'class':'doc-banner-icon'})
    for banner_icon in banner_icon_fa:
        if banner_icon.img != None:
            if banner_icon.img.has_key('src'):
                banner_icon_src = banner_icon.img['src']
                print banner_icon_src
    rating_price_fa = soup.find_all(name='td', attrs={'class':'doc-details-ratings-price'})
    if len(rating_price_fa) != 1:
        print 'except'
    rating_fa = rating_price_fa[0].find_all(name='div', attrs={'class':'ratings goog-inline-block'})
    for rating_f in rating_fa:
        if rating_f.has_key('title'):
            rating_title = rating_f['title']
            rating_figure = rating_title.split(' ')
            if len(rating_figure) >= 2:
                rating_figure = rating_figure[1]
            else:
                rating_figure = 'None'
            print rating_title, rating_figure
            if rating_f.next_sibling == None:
                print 'except'
            raters_f = rating_f.next_sibling
            if raters_f.text == None:
                print 'except'
            raters = raters_f.text
            raters = raters.replace('(', '').replace(')', '').strip()
            print raters
    price_fa = rating_price_fa[0].find_all(name='span', attrs={'class':'buy-button-price'})
    for price_f in price_fa:
        price = price_f.text
        price = price.upper().replace('BUY', '').strip()
        print price
    metadata_fa = soup.find_all(name='div', attrs={'class':'doc-metadata'})
    #print metadata_fa
    for metadata_f in metadata_fa:
        meta_google_plus_fa = metadata_f.find_all(name='div', attrs={'class':'plus-share-container'})
        for meta_google_plus_f in meta_google_plus_fa:
            if len(meta_google_plus_f.contents)>0 and meta_google_plus_f.contents[0].has_key('href'):
                meta_google_plus_href = meta_google_plus_f.contents[0]['href']
                print meta_google_plus_href
                'https://plusone.google.com/u/0/_/+1/fastbutton?url=https%3A%2F%2Fmarket.android.com%2Fdetails%3Fid%3Dcom.rovio.angrybirds'
        meta_update_fa = metadata_f.find_all(name='dt', text='Updated:')
        if len(meta_update_fa) > 0 and meta_update_fa[0].next_sibling != None:
            meta_update_f = meta_update_fa[0].next_sibling
            if meta_update_f.time != None:
                meta_update = meta_update_f.time.text
                print meta_update
        meta_current_fa = metadata_f.find_all(name='dt', text='Current Version:')
        if len(meta_current_fa) > 0 and meta_current_fa[0].next_sibling != None:
            meta_current_f = meta_current_fa[0].next_sibling
            meta_current = meta_current_f.text
            print meta_current
        meta_require_fa = metadata_f.find_all(name='dt', text='Requires Android:')
        if len(meta_require_fa) > 0 and meta_require_fa[0].next_sibling != None:
            meta_require_f = meta_require_fa[0].next_sibling
            meta_require = meta_require_f.text
            print meta_require
        meta_install_fa = metadata_f.find_all(name='dt', text='Installs:')
        if len(meta_install_fa) > 0 and meta_install_fa[0].next_sibling != None:
            meta_install_f = meta_install_fa[0].next_sibling
            meta_install = meta_install_f.text
            meta_install = meta_install.upper().replace('LAST 30 DAYS', '').strip()
            print meta_install
        meta_size_fa = metadata_f.find_all(name='dt', text='Size:')
        if len(meta_size_fa) > 0 and meta_size_fa[0].next_sibling != None:
            meta_size_f = meta_size_fa[0].next_sibling
            meta_size = meta_size_f.text
            print meta_size
    overview_fa = soup.find_all(name='div', attrs={'class':'doc-overview'})
    #print overview_fa
    for overview_f in overview_fa:
        desc_fa = overview_f.find_all(name='div', attrs={'id':'doc-original-text'})
        for desc_f in desc_fa:
            desc = desc_f.text
            print desc
        developer_website_fa = overview_f.find_all(name='a', text="Visit Developer's Website")
        for developer_website_f in developer_website_fa:
            if developer_website_f.has_key('href'):
                developer_website = developer_website_f['href']
                print developer_website
        developer_email_fa = overview_f.find_all(name='a', text='Email Developer')
        for developer_email_f in developer_email_fa:
            if developer_email_f.has_key('href'):
                developer_email = developer_email_f['href']
                developer_email = developer_email.replace('mailto:', '').strip()
                print developer_email
    screenshots_fa = soup.find_all(name='div', attrs={'class':'doc-overview-screenshots'})
    #print screenshots_fa
    for screenshots_f in screenshots_fa:
        screenshot_fa = screenshots_f.find_all(name='img', attrs={'itemprop':'screenshots'})
        for screenshot_f in screenshot_fa:
            if screenshot_f.has_key('src'):
                screenshot = screenshot_f['src']
                print screenshot
    videos_fa = soup.find_all(name='div', attrs={'class':'doc-overview-videos'})
    #print videos_fa
    for videos_f in videos_fa:
        video_fa = videos_f.find_all(name='param', attrs={'name':'movie'})
        for video_f in video_fa:
            if video_f.has_key('value'):
                video = video_f['value']
                print video
    tab_review = soup.find_all(name='div', attrs={'class':'doc-reviews padded-content2'})
    if len(tab_review) <= 0:
        print 'except'
    tab_review = tab_review[0]
    review_head_fa = tab_review.find_all(name='div', attrs={'class':'reviews-heading-container'})
    for review_head_f in review_head_fa:
        user_rating_fa = review_head_f.find_all(name='div', attrs={'class':'user-ratings'})
        if len(user_rating_fa) <= 0:
            print 'except'
        user_rating_fa = user_rating_fa[0]
        rating_tr_fa = user_rating_fa.find_all(name='span', attrs={'class':'histogram-label'})
        for rating_tr_f in rating_tr_fa:
            rating_star = rating_figure = 'None'
            if rating_tr_f.has_key('data-rating'):
                rating_star = rating_tr_f['data-rating']
            #print rating_tr_f.parent.next_s
            if rating_tr_f.parent != None and rating_tr_f.parent.next_sibling != None:
                rating_figure = rating_tr_f.parent.next_sibling
                rating_figure = rating_figure.text.strip()
            print rating_star, rating_figure
    #review_content_fa = tab_review.find_all(name='div', attrs={'class':'doc-user-reviews-list'})
    #review_content_fa = tab_review.find_all(name='div', attrs={'class':'doc-user-reviews-page num-pagination-page'})
    review_content_fa = tab_review.find_all(name='div', attrs={'class':'doc-reviews-container'})
    for review_content_f in review_content_fa:
        #print review_content_f.prettify()
        print '=========='
    ############# how to get review all out? need to look at the javascript 
    tab_permissions_fa = soup.find_all(name='div', attrs={'class':'doc-specs padded-content2'})
    if len(tab_permissions_fa) <= 0:
        print 'except'
    tab_permissions_fa = tab_permissions_fa[0]
    perm_fa = tab_permissions_fa.find_all(name='li', attrs={'class':'doc-permission-group'})
    for perm_f in perm_fa:
        for pc in perm_f.contents:
            if pc.has_key('class'):
                pcc = pc['class']
                if 'doc-permission-group-title' in pcc:
                    perm_group_title = pc.text
                    print 'group', perm_group_title
                if 'doc-permission-description' in pcc:
                    perm_each_desc = pc.text
                    print 'individual', perm_each_desc
        
    

if __name__ == '__main__':
    categories_read()
    #a = httplib.HTTPSConnection('')
