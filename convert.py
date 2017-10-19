# coding:utf-8
import os, re, sys, time
import io
from urllib import urlopen
import requests
import json
import bs4 # beautifulSoupe4
from PIL import Image   # 画像変換用モジュール
import sqlite3
from datetime import datetime

def main():
    # sqlLiteに画像リストを格納するため、DBを定義
    dbname = 'database.db'
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    
    # convertが済んでいないところから開始
    sql = 'SELECT * FROM "pinterest" WHERE convert_flg= 0 ORDER BY "id" ASC'
    c.execute(sql)

    for row in c.fetchall():
        convert_img(row[2], str(row[0]), "jpg", 200)
        print row[0]
        sql = 'UPDATE "pinterest" SET "convert_flg"=1 WHERE ("id" =  '+str(row[0])+')'
        c.execute(sql)
        conn.commit()
    conn.close()

def convert_img(fileName, rename, format, save_size):

    # ファイルオープン
    file =io.BytesIO(urlopen(fileName).read())
    origin = Image.open(file)
    origin_width, origin_height = origin.size
    
    # 横幅のほうが広い=立ち絵としての構図がおかしく、サンプルとして適さない
    if origin_width > origin_height:
        return
    
    #中央揃えするための変数
    x_pos = 0 
    
    # 縮小比率と中央揃えの計算
    if origin_height > save_size:
        width = origin_width / (origin_height / save_size)
        height = save_size
        x_pos = (origin_height - origin_width) / 2
    else:
        width = origin_width
        height = origin_height
        
    # 中央に揃えるのと、パレットモードの解除を兼ねて新規レイヤーに張り付け
    layer = Image.new('RGBA', (origin_height, origin_height), (0, 0, 0, 0))
    layer.paste(origin, (x_pos, 0))
    
    # 透過を白に塗りつぶす用。
    canvas = Image.new('RGB', layer.size, (255, 255, 255))
    for x in xrange(origin_height):
        if x < x_pos:
            continue
        if x > x_pos+origin_width:
            continue
        for y in xrange(origin_height):
            pixel = layer.getpixel((x, y))
            # 透過なら白に塗りつぶし
            if pixel[3] == 0 :
                canvas.putpixel((x, y), (255, 255, 255))
            else:
            # 透過以外なら、用意した画像にピクセルを書き込み
                canvas.putpixel((x, y), (pixel[0], pixel[1], pixel[2]))
            
    # ファイル名の拡張子より前を取得し, フォーマット後のファイル名に変更
    fileName = re.search("(?<!\.)\w+", fileName).group(0) + "." + format    
    resize = canvas.resize((save_size, save_size), Image.BICUBIC)
    # 画像の保存
    resize.save("convert/"+rename+"."+format, returnFormat(format), quality=100, optimize=True)
            
            
# returnFormat()
# 渡されたフォーマットを大文字で返す
#
def returnFormat(format):
    if format == "bmp":
        return "BMP"
    elif format == "jpg":
        return "JPEG"
    elif format == "png":
        return "PNG"
    elif format == "gif":
        return "GIF"
    else:
        print(format + " は対応していません。")
        sys.exit()
        
if __name__ == '__main__':
    main()
 