作者  
ginjake
====


## Description
pinterestから画像を集め、整形する    
ディープランニング用に二次元の立ち絵画像が欲しく  
pinterestの画像がかなり良さそうだったので
Dockerとpythonの勉強も兼ねて作成

## 環境
Docker+python+sqliteを使用。  


## 実行
Dockerの場合、docker-compose upでconvertフォルダに画像が入る。  
Dockerではない場合、Dockerfileを見て必要なものをインストール。  

##各ファイルの説明
### get.py
pinterestからスクレイピングするコード  
実行のたびにDBの初期化を行う。
````
image_info_list = search("立ち絵 金髪", 取得件数)  
image_info_list = search("立ち絵 制服", 取得件数)  
````
のように使う。  
取得件数は200件ごとのため、350とかやっても400件取得する  
結果はsqliteでdatabase.dbに保存される 
 
### convert.py
画像を取得→センタリング,サイズ変更,変換→保存を行う。  
サイズや形式を変更したい場合は  
convert_imgの引数を変える  
convert_imgの中で、立ち絵として適さないのを外しているので  
サンプルの精度を高めたかったら適宜追加する  

DBを見て、未取得のものがあれば処理を行う。
get.pyを実行するとDBが初期化されるので注意

### get_convert.sh
get.pyとconvert.pyを実行するスクリプト  
大量に取得する際はget.pyとconvert.pyを別々に実行するほうが良いかも

## 参考
pinterestからスクレイピングする箇所については、下記ページのコードを改変して使っております。  
http://hassiweb-programming.blogspot.jp/2017/07/retrieve-pinterest-pins-by-python.html  