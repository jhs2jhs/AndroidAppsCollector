import read
import db
import err

def google_play():
    try:
        db.db_init()
        read.categories_read_main()
        read.category_read_main()
    except Exception as e:
        err.except_p(e)
    try:
        read.app_read_main()
    except Exception as e:
        err.except_p(e)

def app_read_main_test():
    try:
        db.db_init()
        read.app_read_main()
    except Exception as e:
        err.except_p(e)

def app_read_test():
    db.db_init()
    app_id = 'com.tencent.mm'
    db.db_execute_g(db.sql_app_insert, (app_id,))
    read.app_read(app_id)
    read.video_read()
        

if __name__ == '__main__':
    #google_play()
    #app_read_main_test()
    app_read_test()
   
