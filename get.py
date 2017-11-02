# coding:utf-8
import os, re, sys, time
import io
import requests
import json
import bs4 # beautifulSoupe4
import sqlite3
from datetime import datetime
    
# sqlLiteに画像リストを格納するため、DBを定義
dbname = 'database.db'
conn = sqlite3.connect(dbname)
conn.text_factory = str
c = conn.cursor()

def main():
    # テーブル初期化
    sql = 'DROP TABLE IF EXISTS pinterest'
    c.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS pinterest (id INTEGER PRIMARY KEY, save_id INTEGER, url STRING, status STRING, description STRING, search_word STRING, date DATETIME)'
    c.execute(sql)
    
    # 検索
    image_info_list = search("立ち絵 女 ", 1000)
    image_info_list = search("anime girl", 1000)
    image_info_list = search("ソシャゲ  女", 1000)
    image_info_list = search("トイズドライブ", 1000)
    image_info_list = search("グリムノーツ", 1000)
    image_info_list = search("スクエニ 女", 1000)
    image_info_list = search("ファルコム 女", 1000)
    image_info_list = search("英雄伝説 女", 1000)
    image_info_list = search("ガスト 女", 100)
    image_info_list = search("SEGA 女", 100)
    image_info_list = search("岸田メル 女", 100)
    image_info_list = search("のアトリエ", 100)
    image_info_list = search("ブレイブソード×ブレイズソウル", 100)
    image_info_list = search("魔界戦記ディスガイア", 100)
    image_info_list = search("テイルズ 女", 100)
    image_info_list = search("レジェンヌ", 100)
    image_info_list = search("ラスピリ", 100)
    image_info_list = search("白猫プロジェクト", 100)
    image_info_list = search("#白猫シェアハウス", 100)
    image_info_list = search("エンドブレイカー", 100)
    image_info_list = search("ファントムオブキル", 100)
    image_info_list = search("ガールフレンド仮", 100)
    image_info_list = search("エンドライド 女", 100)
    image_info_list = search("Cygames 女", 100)
    conn.close()
    print("create_list_end")
    
def search(query, num_pins):
    count = 0; #処理済みの数。デバッグ用に
    # First access
    url     = 'https://www.pinterest.jp/search/pins/'
    headers = {
        'connection': 'keep-alive'
    }
 
    search_response = requests.get(url, params={'q':query}, headers=headers, stream=False)
    soup            = bs4.BeautifulSoup(search_response.text.replace('\n',''), 'html5lib')
 
    data_json_string = soup.find('script', type='application/json') # extract json string
    data_json        = json.loads(data_json_string.string) # convert into dictionary type variable
    results          = data_json['tree']['children'][0]['data']['results']
#    results          = data_json['resouceDataCache'][0]['children'][0]['data']['results']
 
    image_info_list  = []
    for r in results:
        image_info = {}
        image_info['description'] = r['description']
        image_info['link']        = r['link']
        image_info['image_url']   = r['images']['orig']['url']
        image_info['id']          = r['id']
        save_db(image_info['id'], image_info['image_url'], image_info['description'], query)
        image_info_list.append(image_info)
        print("Keyword:"+query+"|"+str(count))
        count += 1
 
    # Second or later access to load additional pins that are responded as a JSON string
    url             = 'https://www.pinterest.jp/resource/BaseSearchResource/get/'
    bookmarks       = data_json['resourceDataCache'][0]['resource']['options']['bookmarks']
    experiment_hash = data_json['context']['triggerable_experiments_hash']
    last_cookies    = search_response.cookies
 
    while len(image_info_list) < num_pins:
 
        ## Preparing parameters, headers and cookies for the "get" request
        params = {
            'source_url':'/search/pins/?q={}'.format(query),
            'data':json.dumps({
                'options':{
                    'bookmarks':bookmarks,
                    'query':query,
                    'scope':'pins',
                    'page_size':200,
                    'field_set_key':'unauth_react'
                },
                'context':{}}),
            '_':str(int(time.time())*10*10*10)
        }
 
        headers = {
            'Host':'www.pinterest.jp',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept-Language':'ja,en-US;q=0.7,en;q=0.3',
            'X-Pinterest-AppState': 'background',
            'X-Pinterest-ExperimentHash': experiment_hash,
            'X-NEW-APP':'1',
            'X-APP-VERSION':'9b11f84',
            'X-Requested-With':'XMLHttpRequest',
            'Referer':'https://www.pinterest.jp',
            'cookie':json.dumps({
                '_auth':dict(last_cookies)['_auth'],
                'csrftoken':dict(last_cookies)['csrftoken'],
                '_pinterest_sess':dict(last_cookies)['_pinterest_sess']}),
            'connection':'keep-alive'
        }
 
        cookies = {
            '_auth':dict(last_cookies)['_auth'],
            'csrftoken':dict(last_cookies)['csrftoken'],
            '_pinterest_sess':dict(last_cookies)['_pinterest_sess'],
            'bei':'False',
            'logged_out':'True',
            'fba':'True',
            'sessionFunelEventLogged':'1'
        }
 
        search_response = requests.get(url, cookies=cookies, params=params, headers=headers, stream=False)
        data_json       = json.loads(search_response.text)
        results         = data_json['resource_response']['data']['results']
        
        bookmarks       = data_json['resource']['options']['bookmarks']
        experiment_hash = data_json['client_context']['triggerable_experiments_hash']
        last_cookies    = search_response.cookies
        if not results:
            print("Keyword:"+query+"_end")
            break
        for r in results:
            image_info = {}
            image_info['description'] = r['description']
            image_info['link']        = r['link']
            image_info['image_url']   = r['images']['orig']['url']
            image_info['id']          = r['id']
            save_db(image_info['id'], image_info['image_url'], image_info['description'], query)
            image_info_list.append(image_info)
            print("Keyword:"+query+"|"+str(count))
            count += 1
            
    return image_info_list
 
 
    
def save_db(id, image_url, description, search_word):
    sql = 'insert INTO "pinterest" ("save_id", "url", "status", "description", "search_word", "date")  values (?, ?, ?, ?, ?, ?)'
    c.execute(sql, (0, image_url, 0, description, search_word, datetime.now().strftime("%Y/%m/%d %H:%M:%S")))
    conn.commit()

if __name__ == '__main__':
    main()
 