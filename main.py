import db
import err
import google_play
import youtube

def google_play_main():
    try:
        db.db_init()
        google_play.categories_read_main()
        google_play.category_read_main()
    except Exception as e:
        err.except_p(e)
    try:
        google_play.app_read_main()
    except Exception as e:
        err.except_p(e)

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
    google_play.app_read(app_id)
    youtube.video_read()
        

if __name__ == '__main__':
    #google_play()
    #app_read_main_test()
    app_read_test()
    #google_play.post_test()
    #google_play.post_t()
