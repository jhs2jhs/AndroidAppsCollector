import db
import err
import google_play
import youtube
import util
import android_zoom
import androlib

def google_play_main():
    db.db_init()
    '''
    finish = False ## comment this if run after first time
    while finish == False:
        try:
            google_play.categories_read_main()
            finish = google_play.category_read_main()
            util.sleep()
        except Exception as e:
            err.except_p(e)
    '''
            
    
def android_zoom_main():
    db.db_init()
    try:
        #android_zoom.categories_read_main() ## comment this if run after first time
        #android_zoom.category_read_main() ## comment this if run after first time
        android_zoom.app_read_main()
    except Exception as e:
        err.except_p(e)

def androlib_main():
    db.db_init()
    try:
        #androlib.language_read_main() ## comment this if run after first time
        #androlib.home_read_main() ## comment this if run after first time
        #androlib.home_read_max_main() ## comment this if run after first time
        androlib.cate_read_main()
        androlib.cate_link_read_main()
    except Exception as e:
        err.except_p(e)

def app_read_main():
    finish = False
    while finish == False:
        try:
            finish = google_play.app_read_main()
        except Exception as e:
            err.except_p(e)
    finish = False
    while finish == False:
        try:
            finish = youtube.video_read_main()
        except Exception as e:
            err.except_p(e)


def review_read_main():
    finish = False
    google_play.review_read_main_init()
    while finish == False:
        try:
            finish = google_play.review_read_main()
        except Exception as e:
            err.except_p(e)        

if __name__ == '__main__':
    #google_play_main()
    #android_zoom_main()
    androlib_main()
    #app_read_main()
    #review_read_main()







def app_read_main_test():
    try:
        db.db_init()
        google_play.app_read_main()
    except Exception as e:
        err.except_p(e)

def app_read_test():
    db.db_init()
    app_id = 'com.tencent.mm'
    db.db_execute_g(db.sql_app_insert, (app_id,))
    #google_play.app_read(app_id)
    #youtube.video_read_main()
    google_play.review_read_main()
