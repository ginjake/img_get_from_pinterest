# coding:utf-8
import os, re, sys, time
import io
import urllib.request
import json
import bs4 # beautifulSoupe4
from PIL import Image   # 画像変換用モジュール
import sqlite3
from datetime import datetime
import platform
import re

# 成功時DBに入るメッセージ
SUCCESS = "success"
def main():
    global SUCCESS
    file_id = 1
    # sqlLiteに画像リストを格納するため、DBを定義
    dbname = 'database.db'
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    # convertが済んでいないところから開始
    sql = 'SELECT * FROM "pinterest" WHERE status= "0" ORDER BY "id" ASC'
    c.execute(sql)
    
    for row in c.fetchall():

        ## ファイルを連番にする処理。変換済みのうち、save_idの最大値を取得して+1。
        sql = 'SELECT MAX(save_id)+2 FROM pinterest WHERE status = "'+SUCCESS+'"'
        c.execute(sql)
        
        for save_id in c.fetchone():
            file_id = save_id
        if file_id is None:
            file_id = 1
        status = convert_img(row[2], file_id, "jpg", 200, str(row[4]))
        if status != SUCCESS:
            sql = 'UPDATE "pinterest" SET "status"="'+status+'"  WHERE ("id" =  '+str(row[0])+')'
        else:
            sql = 'UPDATE "pinterest" SET "status"="'+status+'" , "save_id"='+ str(file_id) +' WHERE ("id" =  '+str(row[0])+')'
        c.execute(sql)
        conn.commit()
        
    conn.close()
    print("end")

def convert_img(fileName, rename, format, save_size, description):
    global SUCCESS

    # ファイルオープン
    try:
        response = urllib.request.urlopen(fileName)
        file =io.BytesIO(response.read())
        origin = Image.open(file)
    except:
        print ('image can not load')
        return 'Load Error'
    
    origin_width, origin_height = origin.size
    
    if description.find('pixiv') > -1:
        return 'Pixivだから除外'
    
    # 横幅のほうが広い=立ち絵としての構図がおかしく、サンプルとして適さない
    if origin_width > origin_height:
        return 'Not suitable'
    # でかすぎ
    if origin_width > 1500:
        return 'width Too Big'
    if origin_height > 3000:
        return 'height Too Big'
    
    #中央揃えするための変数
    x_pos = 0 
    # 縮小比率と中央揃えの計算
    if origin_height > save_size:
        width = origin_width / (origin_height / save_size)
        height = save_size
        x_pos = int((origin_height - origin_width) / 2)
    else:
        width = origin_width
        height = origin_height
        
        
    # 色の比率で判定する
    white_pixel = 0
    black_pixel = 0
    # パレットモードの解除用に、判定用レイヤーに張り付け
    judge_layer = Image.new('RGBA', (origin_width, origin_height), (0, 0, 0, 0))
    judge_layer.paste(origin, (0, 0))
    for x in range(origin_width):
        for y in range(origin_height):
            pixel = judge_layer.getpixel((x, y))
            if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
                white_pixel += 1
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                black_pixel += 1
                
    # ピクセルの合計
    pixel_sum = origin_height*origin_width
    
    # 黒と白の比率
    percent_white_pixel = float(white_pixel)/pixel_sum * 100.0
    percent_black_pixel = float(black_pixel)/pixel_sum * 100.0

    if percent_white_pixel < 10 and percent_black_pixel < 10:
        return "背景判定"
    if percent_white_pixel > 70:
        return "白が多すぎる"
    if percent_black_pixel > 70:
        return "黒が多すぎる"
    
    # 中央に揃えるため新規レイヤーに張り付け
    layer = Image.new('RGBA', (origin_height, origin_height), (0, 0, 0, 0))
    layer.paste(origin, (x_pos, 0))
    
    # 透過を白に塗りつぶす用。
    canvas = Image.new('RGB', layer.size, (255, 255, 255))
    for x in range(origin_height):
        if x < x_pos:
            continue
        if x > x_pos+origin_width:
            continue
        for y in range(origin_height):
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

    file_num = rename
    resize.save("data/celebA/"+str('%06d' %(file_num))+"."+format, returnFormat(format), quality=100, optimize=True)
    
    mirror = resize.transpose(Image.FLIP_LEFT_RIGHT)
    
    file_num = file_num + 1
    mirror.save("data/celebA/"+str('%06d' %(file_num))+"."+format, returnFormat(format), quality=100, optimize=True)
    
    print(str('%06d' %(file_num))+"."+format+" 変換")
    return SUCCESS
            
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
 