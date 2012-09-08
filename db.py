import sqlite3

sql_init = '''
CREATE TABLE IF NOT EXISTS category (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cate_group TEXT NOT NULL, 
  cate_name TEXT NOT NULL,
  cate_path TEXT NOT NULL UNIQUE,
  cate_create_date TEXT,
  cate_update_date TEXT,
  UNIQUE (cate_group, cate_name, cate_path)
);
CREATE TABLE IF NOT EXISTS category_read (
  cate_name TEXT NOT NULL, 
  cate_path TEXT NOT NULL,
  cate_param TEXT NOT NULL, 
  cate_type TEXT NOT NULL,
  read_status TEXT NOT NULL DEFAULT 0,
  UNIQUE (cate_path, cate_param, cate_type)
);
CREATE TABLE IF NOT EXISTS app (
  app_id TEXT NOT NULL UNIQUE, 
  title TEXT,
  icon TEXT, 
  developer_name TEXT,
  developer_href TEXT, 
  developer_website TEXT, 
  developer_email TEXT, 
  developer_privacy TEXT, 
  desc TEXT, 
  update_date TEXT, 
  current_version TEXT, 
  requires_android TEXT, 
  category TEXT, 
  installs TEXT, 
  file_size TEXT, 
  price TEXT, 
  content_rating TEXT, -- what is this?
  rating_total TEXT,
  rating_average TEXT DEFAULT 0,
  rating_0 TEXT DEFAULT 0,
  rating_1 TEXT DEFAULT 0,
  rating_2 TEXT DEFAULT 0,
  rating_3 TEXT DEFAULT 0,
  rating_4 TEXT DEFAULT 0,
  rating_5 TEXT DEFAULT 0,
  rank TEXT DEFAULT -1, 
  scrape_create_date TEXT,
  scrape_update_date TEXT,
  read_status TEXT DEFAULT 0
);
CREATE TABLE IF NOT EXISTS share (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  google_plus_href TEXT,
  google_plus_figure TEXT,
  read_status TEXT DEFAULT 0,
  google_create_date TEXT, 
  google_update_date TEXT, 
  UNIQUE (app_id, google_plus_href)
);
CREATE TABLE IF NOT EXISTS awards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  award TEXT NOT NULL, 
  UNIQUE (app_id, award)
);
CREATE TABLE IF NOT EXISTS screenshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  screenshot TEXT NOT NULL, 
  UNIQUE (app_id, screenshot)
);
CREATE TABLE IF NOT EXISTS videos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  video TEXT NOT NULL, 
  watched TEXT, 
  watched_create_date TEXT, 
  watched_update_date TEXT, 
  UNIQUE (app_id, video)
);
CREATE TABLE IF NOT EXISTS review (
  review_id TEXT NOT NULL UNIQUE,
  app_id TEXT NOT NULL,
  reviewer TEXT, 
  date TEXT, 
  device TEXT, 
  version TEXT,
  title TEXT,
  comment TEXT, 
  review_star TEXT,
  review_create_date TEXT, 
  review_update_date TEXT
);
CREATE TABLE IF NOT EXISTS permission (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  perm_group TEXT, 
  perm_individual TEXT, 
  UNIQUE (app_id, perm_group, perm_individual)
);
'''

db_path = './android.db'
def get_db():
    db = sqlite3.connect(db_path)
    return db

db = get_db()

def db_init():
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.executescript(sql_init)
    db.commit()
    c.execute('SELECT * FROM SQLITE_MASTER')
    tables = c.fetchall()
    print '** tables: %s **'%(str(len(tables)))
    c.close()

def db_execute_g(sql, params): # in general
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.execute(sql, params)
    db.commit()
    c.close()

def db_get_g(sql, params):
    global db
    if db == None:
        db = get_db()
    c = db.cursor()
    c.execute(sql, params)
    r = c.fetchall()
    c.close()
    return r

sql_cate_insert = '''
INSERT OR IGNORE INTO category (cate_group, cate_name, cate_path, cate_create_date) VALUES (?,?,?,?)
'''
sql_cate_read_insert = '''
INSERT OR IGNORE INTO category_read (cate_name, cate_path, cate_param, cate_type) VALUES (?,?,?,?)
'''
sql_cate_read_update = '''
UPDATE category_read SET read_status = 1 WHERE cate_name=? AND cate_path=? AND cate_param=? AND cate_type=?
'''
sql_cate_read_get = '''
SELECT cate_name, cate_path, cate_param, cate_type FROM category_read WHERE read_status = 0
'''
sql_app_insert = '''
INSERT OR IGNORE INTO app (app_id) VALUES (?)
'''
sql_app_read_get = '''
SELECT app_id FROM app WHERE read_status = 0
'''
sql_app_banner_update = '''
UPDATE app SET title=?, icon=?, developer_name=?, developer_href=?, rating_average=?, rating_total=?, price=? WHERE app_id = ?
'''
sql_app_awards_insert = '''
INSERT OR IGNORE INTO awards (app_id, award) VALUES (?,?)
'''
sql_app_google_plus_insert = '''
INSERT OR IGNORE INTO share (app_id, google_plus_href) VALUES (?,?)
'''
sql_app_metadata_update = '''
UPDATE app SET update_date=?, current_version=?, requires_android=?, installs=?, file_size=? WHERE app_id = ?
'''
sql_app_overview_update = '''
UPDATE app SET desc=?, developer_website=?, developer_email=?, developer_privacy=? WHERE app_id=?
'''
sql_app_screenshot_insert = '''
INSERT OR IGNORE INTO screenshots (app_id, screenshot) VALUES (?,?)
'''
sql_app_video_insert = '''
INSERT OR IGNORE INTO videos (app_id, video) VALUES (?,?)
'''
sql_app_perm_insert = '''
INSERT OR IGNORE INTO permission (app_id, perm_group, perm_individual) VALUES (?,?,?)
'''



if __name__ == '__main__':
    db_init()
