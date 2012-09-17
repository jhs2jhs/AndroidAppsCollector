import sqlite3

sql_init = '''
------- androlib start
CREATE TABLE IF NOT EXISTS lib_lang (
  lang_href TEXT NOT NULL UNIQUE, 
  lang_title TEXT NOT NULL,
  read_status TEXT NOT NULL DEFAULT 0,
  lang_create_date TEXT,
  lang_update_date TEXT
);
CREATE TABLE IF NOT EXISTS lib_lang_cate (
  lang_href TEXT NOT NULL,
  cate_path TEXT NOT NULL,
  cate_title TEXT,
  cate_param TEXT NOT NULL DEFAULT 0, 
  cate_param_max TEXT NOT NULL DEFAULT 0,
  read_status TEXT NOT NULL DEFAULT 0, 
  cate_create_date TEXT,
  cate_update_date TEXT,
  UNIQUE (lang_href, cate_path)
);
CREATE TABLE IF NOT EXISTS lib_lang_cate_read (
  lang_href TEXT NOT NULL,
  cate_path TEXT NOT NULL,
  cate_param TEXT NOT NULL,
  read_status TEXT NOT NULL DEFAULT 0,
  cate_create_date TEXT,
  cate_update_date TEXT,
  UNIQUE (lang_href, cate_path, cate_param)
);
CREATE TABLE IF NOT EXISTS lib_lang_cate_link_read (
  lang_href TEXT NOT NULL,
  cate_path TEXT NOT NULL,
  cate_param TEXT NOT NULL,
  link_href TEXT NOT NULL,
  link_name TEXT NOT NULL,
  link_id TEXT,
  app_id TEXT,
  read_status TEXT NOT NULL DEFAULT 0,
  cate_create_date TEXT,
  cate_update_date TEXT,
  UNIQUE (lang_href, cate_path, cate_param, link_href)
);
-------- androlib end
-------- android_zoom start
CREATE TABLE IF NOT EXISTS category_android_zoom (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cate_group TEXT NOT NULL, 
  cate_name TEXT NOT NULL,
  cate_path TEXT NOT NULL UNIQUE,
  cate_create_date TEXT,
  cate_update_date TEXT,
  UNIQUE (cate_group, cate_name, cate_path)
);
CREATE TABLE IF NOT EXISTS category_android_zoom_read (
  cate_name TEXT NOT NULL, 
  cate_path TEXT NOT NULL,
  cate_param TEXT NOT NULL DEFAULT 0, -- last successful 
  cate_type TEXT,
  read_status TEXT NOT NULL DEFAULT 0,
  UNIQUE (cate_path)
);
CREATE TABLE IF NOT EXISTS app_android_zoom_read (
  app_name TEXT NOT NULL, 
  app_path TEXT NOT NULL,
  app_id TEXT,
  read_status TEXT NOT NULL DEFAULT 0,
  UNIQUE (app_path)
);
-------------- android_zoom end
-------------- google_play start
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
--------------- google_play end

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
  content_rating TEXT, 
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
  google_plus_figure TEXT, -- -1 means web is not available 
  read_status TEXT DEFAULT 0,
  scrape_create_date TEXT, 
  scrape_update_date TEXT, 
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
  read_status TEXT DEFAULT 0,
  view_total TEXT DEFAULT -1,
  view_likes TEXT DEFAULT -1,
  view_dislikes TEXT DEFAULT -1,
  comments TEXT DEFAULT -1,
  scrape_create_date TEXT, 
  scrape_update_date TEXT, 
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
  scrape_create_date TEXT, 
  scrape_update_date TEXT
);
CREATE TABLE IF NOT EXISTS review_read (
  app_id TEXT NOT NULL UNIQUE,
  read_status TEXT DEFAULT 0,
  pageNum TEXT NOT NULL DEFAULT 0,
  review_type TEXT DEFAULT 1, 
  review_sort_order TEXT DEFAULT 0
);
CREATE TABLE IF NOT EXISTS permission (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  app_id TEXT NOT NULL,
  perm_group TEXT, 
  perm_individual TEXT, 
  UNIQUE (app_id, perm_group, perm_individual)
);
'''

#################

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
sql_app_insert_with_rank = '''
INSERT OR IGNORE INTO app (app_id, rank) VALUES (?,?)
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
sql_app_google_plus_get = '''
SELECT app_id, google_plus_href FROM share WHERE read_status = 0
'''
sql_app_google_plus_update = '''
UPDATE share SET read_status=1, google_plus_figure=?, scrape_create_date=? WHERE app_id=? AND google_plus_href=?
'''
sql_app_metadata_update = '''
UPDATE app SET update_date=?, current_version=?, requires_android=?, installs=?, file_size=?, category=?, content_rating=? WHERE app_id = ?
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
sql_app_rating_update = '''
UPDATE app SET rating_0=?, rating_1=?, rating_2=?, rating_3=?, rating_4=?, rating_5=? WHERE app_id=?
'''
sql_video_get = '''
SELECT app_id, video, view_total FROM videos WHERE read_status = 0
'''
sql_video_update = '''
UPDATE videos SET view_total=?, view_likes=?, view_dislikes=?, comments=?, scrape_create_date=?, read_status=? WHERE app_id=? AND video=?
'''
sql_video_update_404 = '''
UPDATE videos SET scrape_create_date=?, read_status=? WHERE app_id=? AND video=?
'''
sql_app_read_update = '''
UPDATE app SET read_status=?, scrape_create_date=? WHERE app_id=?
'''
sql_review_app_get = '''
SELECT app_id FROM app 
'''
sql_review_read_insert = '''
INSERT OR IGNORE INTO review_read (app_id) VALUES (?)
'''
sql_review_read_get = '''
SELECT app_id, pageNum, review_type, review_sort_order FROM review_read WHERE read_status = 0
'''
sql_review_insert = '''
INSERT OR IGNORE INTO review (review_id, app_id, reviewer, date, device, version, title, comment, review_star, scrape_create_date) VALUES (?,?,?,?,?,?,?,?,?,?)
'''
sql_review_read_update = '''
UPDATE review_read SET pageNum=? WHERE app_id=?
'''
sql_review_read_status_update = '''
UPDATE review_read SET read_status = 1 WHERE app_id=?
'''

#### google plus


####### zoom 
sql_zoom_cate_insert = '''
INSERT OR IGNORE INTO category_android_zoom (cate_group, cate_name, cate_path, cate_create_date) VALUES (?,?,?,?)
'''
sql_zoom_cate_read_insert = '''
INSERT OR IGNORE INTO category_android_zoom_read (cate_name, cate_path, cate_param) VALUES (?,?,?)
'''
sql_zoom_cate_read_update = '''
UPDATE category_android_zoom_read SET read_status = 1 WHERE cate_path=? 
'''
sql_zoom_cate_read_param_update = '''
UPDATE category_android_zoom_read SET cate_param = ? WHERE cate_path=? 
'''
sql_zoom_cate_read_get = '''
SELECT cate_name, cate_path, cate_param FROM category_android_zoom_read WHERE read_status = 0
'''
sql_zoom_app_insert = '''
INSERT OR IGNORE INTO app_android_zoom_read (app_name, app_path) VALUES (?,?)
'''
sql_zoom_app_update = '''
UPDATE app_android_zoom_read SET app_id = ?, read_status = 1 WHERE app_path = ?
'''
sql_zoom_app_get = '''
SELECT app_name, app_path, app_id, read_status FROM app_android_zoom_read WHERE read_status = 0
'''


#################
sql_lib_lang_insert = '''
INSERT OR IGNORE INTO lib_lang (lang_href, lang_title, lang_create_date) VALUES (?,?,?)
'''
sql_lib_lang_get = '''
SELECT lang_href, lang_title FROM lib_lang WHERE read_status = 0
'''
sql_lib_lang_update = '''
UPDATE lib_lang SET read_status = 1 WHERE lang_href = ?
'''
sql_lib_lang_cate_insert = '''
INSERT OR IGNORE INTO lib_lang_cate (lang_href, cate_path, cate_title, cate_create_date) VALUES (?,?,?,?)
'''
sql_lib_lang_cate_get = '''
SELECT lang_href, cate_path, cate_title, cate_param_max FROM lib_lang_cate WHERE read_status = 0
'''
sql_lib_lang_cate_read_insert = '''
INSERT OR IGNORE INTO lib_lang_cate_read (lang_href, cate_path, cate_param, cate_create_date) VALUES (?,?,?,?)
'''
sql_lib_lang_cate_update = '''
UPDATE lib_lang_cate SET cate_param_max = ?, read_status = 1 WHERE lang_href = ? AND cate_path = ?
'''
sql_lib_lang_cate_read_get = '''
SELECT lang_href, cate_path, cate_param FROM lib_lang_cate_read WHERE read_status = 0 ORDER BY lang_href, cate_path, cate_param
'''
sql_lib_lang_cate_read_update = '''
UPDATE lib_lang_cate_read SET read_status = 1 WHERE lang_href = ? AND cate_path = ? AND cate_param = ?
'''
sql_lib_lang_cate_link_read_insert = '''
INSERT OR IGNORE INTO lib_lang_cate_link_read (lang_href, cate_path, cate_param, link_href, link_name, link_id) VALUES (?,?,?,?,?,?)
'''
sql_lib_lang_cate_link_read_get = '''
SELECT lang_href, cate_path, cate_param, link_href FROM lib_lang_cate_link_read WHERE read_status = 0
'''
sql_lib_lang_cate_link_read_update = '''
UPDATE lib_lang_cate_link_read SET app_id = ?, read_status = 1 WHERE lang_href=? AND cate_path=? AND cate_param=?
'''

if __name__ == '__main__':
    db_init()
