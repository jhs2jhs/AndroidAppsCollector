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

#####
def app_read_main():
    finish = True
    try:
        finish = app_read_main_temp()
        return finish
    except Exception as e:
        err.except_p('e')
        finish = False
        return finish

def app_read_main_temp():
    finish = True
    rows = db_app.db_get_g(db_sql.sql_app_read_get, ())
    i_t = len(rows)
    i = 0
    for row in rows:
        i = i + 1
        print '%d of %d'%(i, i_t), 
        finish = False
        app_id = row[0]
        app_read(app_id)
        util.sleep()
    return finish 

def app_read(app_id):
    try:
        url = '/%s/details?id=%s'%(android_root, app_id)
        print '** app %s **'%(url)
        status, body = android_https_get(url)
        #print status, body
        if status == 404:
            print '== 404'
            db_app.db_execute_g(db_sql.sql_app_read_update, (1, str(datetime.now()), app_id))
            return 
        if status != 200:
            raise Exception('app read https connection error: %s'%(str(status)))
        soup = BeautifulSoup(body)
        app_read_banner(app_id, soup)
        app_read_tab_overview(app_id, soup)
        app_read_tab_review(app_id, soup)
        app_read_tab_permission(app_id, soup)
        db_app.db_execute_g(db_sql.sql_app_read_update, (1, str(datetime.now()), app_id))
        #util.sleep()
    except Exception as e:
        err.except_p(e)


def app_read_banner(app_id, soup):
    banner_title = ''
    banner_developer_href = ''
    banner_developer_name = ''
    banner_icon_src = ''
    rating_figure = ''
    raters = ''
    price = ''
    banner_title_fa = soup.find_all(name='td', attrs={'class':'doc-banner-title-container'})
    if len(banner_title_fa) == 1:
        banner_title_f = banner_title_fa[0]
        if banner_title_f.h1 != None:
            banner_title = banner_title_f.h1.text
        if banner_title_f.a != None:
            if banner_title_f.a.has_key('href'):
                banner_developer_href = banner_title_f.a['href'].strip()
            if banner_title_f.a.text != None:
                banner_developer_name = banner_title_f.a.text.strip()
    banner_icon_fa = soup.find_all(name='div', attrs={'class':'doc-banner-icon'})
    for banner_icon in banner_icon_fa:
        if banner_icon.img != None:
            if banner_icon.img.has_key('src'):
                banner_icon_src = banner_icon.img['src'].strip()
    banner_annotation_fa = soup.find_all(name='div', attrs={'class':'badges-badge-title goog-inline-block'})
    for banner_annotation in banner_annotation_fa:
        banner_annotation_text = banner_annotation.text.strip()
        db_app.db_execute_g(db_sql.sql_app_awards_insert, (app_id, banner_annotation_text))
    rating_price_fa = soup.find_all(name='td', attrs={'class':'doc-details-ratings-price'})
    if len(rating_price_fa) == 1:
        rating_fa = rating_price_fa[0].find_all(name='div', attrs={'class':'ratings goog-inline-block'})
        for rating_f in rating_fa:
            if rating_f.has_key('title'):
                rating_title = rating_f['title'].strip()
                rating_figure = rating_title.split(' ')
                if len(rating_figure) >= 2:
                    rating_figure = rating_figure[1].strip()
            if rating_f.next_sibling != None:
                raters_f = rating_f.next_sibling
                if raters_f.text != None:
                    raters = raters_f.text
                    raters = raters.replace('(', '').replace(')', '').strip()
        price_fa = rating_price_fa[0].find_all(name='span', attrs={'class':'buy-button-price'})
        for price_f in price_fa:
            price = price_f.text
            price = price.upper().replace('BUY', '').strip()
    db_app.db_execute_g(db_sql.sql_app_banner_update, (banner_title, banner_icon_src, banner_developer_name, banner_developer_href, rating_figure, raters, price, app_id))
        

def app_read_tab_overview(app_id, soup):
    app_read_metadata(app_id, soup)
    app_read_overview(app_id, soup)
    app_read_screenshot(app_id, soup)
    app_read_video(app_id, soup)


def app_read_metadata(app_id, soup):
    meta_update = ''
    meta_current = ''
    meta_require = ''
    meta_install = ''
    meta_size = ''
    meta_category = ''
    meta_rating = ''
    metadata_fa = soup.find_all(name='div', attrs={'class':'doc-metadata'})
    for metadata_f in metadata_fa:
        meta_google_plus_fa = metadata_f.find_all(name='div', attrs={'class':'plus-share-container'})
        for meta_google_plus_f in meta_google_plus_fa:
            if len(meta_google_plus_f.contents)>0 and meta_google_plus_f.contents[0].has_key('href'):
                meta_google_plus_href = meta_google_plus_f.contents[0]['href'].strip()
                db_app.db_execute_g(db_sql.sql_app_google_plus_insert, (app_id, meta_google_plus_href))
        meta_update_fa = metadata_f.find_all(name='dt', text='Updated:')
        if len(meta_update_fa) > 0 and meta_update_fa[0].next_sibling != None:
            meta_update_f = meta_update_fa[0].next_sibling
            if meta_update_f.time != None:
                meta_update = meta_update_f.time.text.strip()
        meta_current_fa = metadata_f.find_all(name='dt', text='Current Version:')
        if len(meta_current_fa) > 0 and meta_current_fa[0].next_sibling != None:
            meta_current_f = meta_current_fa[0].next_sibling
            meta_current = meta_current_f.text.strip()
        meta_require_fa = metadata_f.find_all(name='dt', text='Requires Android:')
        if len(meta_require_fa) > 0 and meta_require_fa[0].next_sibling != None:
            meta_require_f = meta_require_fa[0].next_sibling
            meta_require = meta_require_f.text.strip()
        meta_category_fa = metadata_f.find_all(name='dt', text='Category:')
        if len(meta_category_fa) > 0 and meta_category_fa[0].next_sibling != None:
            meta_category_f = meta_category_fa[0].next_sibling
            meta_category = meta_category_f.text.strip()
        meta_install_fa = metadata_f.find_all(name='dt', text='Installs:')
        if len(meta_install_fa) > 0 and meta_install_fa[0].next_sibling != None:
            meta_install_f = meta_install_fa[0].next_sibling
            meta_install = meta_install_f.text
            meta_install = meta_install.upper().replace('LAST 30 DAYS', '').strip()
        meta_size_fa = metadata_f.find_all(name='dt', text='Size:')
        if len(meta_size_fa) > 0 and meta_size_fa[0].next_sibling != None:
            meta_size_f = meta_size_fa[0].next_sibling
            meta_size = meta_size_f.text.strip()
        meta_rating_fa = metadata_f.find_all(name='dt', text='Content Rating:')
        if len(meta_rating_fa) > 0 and meta_rating_fa[0].next_sibling != None:
            meta_rating_f = meta_rating_fa[0].next_sibling
            meta_rating = meta_rating_f.text.strip()
    db_app.db_execute_g(db_sql.sql_app_metadata_update, (meta_update, meta_current, meta_require, meta_install, meta_size, meta_category, meta_rating, app_id))
    

def app_read_overview(app_id, soup):
    desc = ''
    developer_website = ''
    developer_email = ''
    developer_privacy = ''
    overview_fa = soup.find_all(name='div', attrs={'class':'doc-overview'})
    for overview_f in overview_fa:
        desc_fa = overview_f.find_all(name='div', attrs={'id':'doc-original-text'})
        for desc_f in desc_fa:
            desc = desc_f.text.strip()
        developer_website_fa = overview_f.find_all(name='a', text="Visit Developer's Website")
        for developer_website_f in developer_website_fa:
            if developer_website_f.has_key('href'):
                developer_website = developer_website_f['href'].strip()
        developer_email_fa = overview_f.find_all(name='a', text='Email Developer')
        for developer_email_f in developer_email_fa:
            if developer_email_f.has_key('href'):
                developer_email = developer_email_f['href']
                developer_email = developer_email.replace('mailto:', '').strip()
        developer_privacy_fa = overview_f.find_all(name='a', text='Privacy Policy')
        for developer_privacy_f in developer_privacy_fa:
            if developer_privacy_f.has_key('href'):
                developer_privacy = developer_privacy_f['href'].strip()
    db_app.db_execute_g(db_sql.sql_app_overview_update, (desc, developer_website, developer_email, developer_privacy, app_id))

def app_read_screenshot(app_id, soup):
    screenshots_fa = soup.find_all(name='div', attrs={'class':'doc-overview-screenshots'})
    for screenshots_f in screenshots_fa:
        screenshot_fa = screenshots_f.find_all(name='img', attrs={'itemprop':'screenshots'})
        for screenshot_f in screenshot_fa:
            if screenshot_f.has_key('src'):
                screenshot = screenshot_f['src'].strip()
                db_app.db_execute_g(db_sql.sql_app_screenshot_insert, (app_id, screenshot))

def app_read_video(app_id, soup):
    videos_fa = soup.find_all(name='div', attrs={'class':'doc-overview-videos'})
    for videos_f in videos_fa:
        video_fa = videos_f.find_all(name='param', attrs={'name':'movie'})
        for video_f in video_fa:
            if video_f.has_key('value'):
                video = video_f['value'].strip()
                db_app.db_execute_g(db_sql.sql_app_video_insert, (app_id, video))

def app_read_tab_review(app_id, soup): ## needs to work out
    rating_0 = ''
    rating_1 = ''
    rating_2 = ''
    rating_3 = ''
    rating_4 = ''
    rating_5 = ''
    tab_review = soup.find_all(name='div', attrs={'class':'doc-reviews padded-content2'})
    if len(tab_review) <= 0:
        raise Exception('app tab review len <= 0')
    tab_review = tab_review[0]
    review_head_fa = tab_review.find_all(name='div', attrs={'class':'reviews-heading-container'})
    for review_head_f in review_head_fa:
        user_rating_fa = review_head_f.find_all(name='div', attrs={'class':'user-ratings'})
        if len(user_rating_fa) <= 0:
            return 
            #raise Exception('app tab review user rating len <= 0')
        user_rating_fa = user_rating_fa[0]
        rating_tr_fa = user_rating_fa.find_all(name='span', attrs={'class':'histogram-label'})
        for rating_tr_f in rating_tr_fa:
            rating_star = rating_figure = 'None'
            if rating_tr_f.has_key('data-rating'):
                rating_star = rating_tr_f['data-rating'].strip()
            if rating_tr_f.parent != None and rating_tr_f.parent.next_sibling != None:
                rating_figure = rating_tr_f.parent.next_sibling
                rating_figure = rating_figure.text.strip()
            if rating_star == '0':
                rating_0 = rating_figure
            if rating_star == '1':
                rating_1 = rating_figure
            if rating_star == '2':
                rating_2 = rating_figure
            if rating_star == '3':
                rating_3 = rating_figure
            if rating_star == '4':
                rating_4 = rating_figure
            if rating_star == '5':
                rating_5 = rating_figure
    db_app.db_execute_g(db_sql.sql_app_rating_update, (rating_0, rating_1, rating_2, rating_3, rating_4, rating_5, app_id))

def app_read_tab_permission(app_id, soup):
    perm_group_title = ''
    tab_permissions_fa = soup.find_all(name='div', attrs={'class':'doc-specs padded-content2'})
    if len(tab_permissions_fa) <= 0:
        raise Exception('app tab permission len <= 0')
    tab_permissions_fa = tab_permissions_fa[0]
    perm_fa = tab_permissions_fa.find_all(name='li', attrs={'class':'doc-permission-group'})
    for perm_f in perm_fa:
        for pc in perm_f.contents:
            if pc.has_key('class'):
                pcc = pc['class']
                if 'doc-permission-group-title' in pcc:
                    perm_group_title = pc.text.strip()
                if 'doc-permission-description' in pcc:
                    perm_each_desc = pc.text.strip()
                    db_app.db_execute_g(db_sql.sql_app_perm_insert, (app_id, perm_group_title, perm_each_desc))


def main():
    db_init()
    finish = False
    while finish == False:
        try:
            finish = app_read_main()
        except Exception as e:
            err.except_p(e)

def main_temp():
    db_init()
    finish = app_read_main_temp()

if __name__ == '__main__':
    main()
