import err
import util
import app_read_overview
import app_read_review
import app_read_google_plus
import app_read_youtube
import cate_read_google_play
import cate_read_android_zoom
import cate_read_androlib
import db_app
import db_play
import db_zoom
import db_lib

def main():
    #cate_read()
    db_merge()
    app_read()

def db_merge():
    db_app.db_init()
    print '** start db_merge **'
    db_app.db_merge(db_play.db_path, db_app.db_path)
    db_app.db_merge(db_lib.db_path, db_app.db_path)
    db_app.db_merge(db_zoom.db_path, db_app.db_path)
    print '** end db_merge **'

def app_read():
    app_read_overview.main()
    app_read_youtube.main()
    app_read_google_plus.main()
    #app_read_review.main()

def cate_read():
    cate_read_google_play.main()
    cate_read_android_zoom.main()
    cate_read_androlib.main()
    

if __name__ == '__main__':
    main()


