# cplus-line-notify   


<img src="https://user-images.githubusercontent.com/16556629/65393388-e2c92780-ddba-11e9-8253-c98322df8785.JPG" height=400px>　　　<img src="https://user-images.githubusercontent.com/16556629/65393386-e066cd80-ddba-11e9-8a0a-116c8fc5cecd.JPG" height=400px>


## About  
Cplus・manaba・CHOIS (図書館)の情報をLINEに通知するBotです (中央大学の学生向け)  
1日のうち決まった時間にmanabaの通知 (課題の未提出・コースニュースの未読・掲示板の未読)・図書館の通知 (貸出状況)・Cplus (授業変更情報) の通知をチェックし、内容に前日から変更があった場合にのみメッセージを送信します  
(もともと自分用に作ったものなので、安定的に動作するかは不明な部分もありますが…)  
導入方法は下記を参照してください    

## Update  

### 更新予定

- 図書館の予約情報の取得に対応する予定

### 更新履歴  
- manabaの仕様変更により情報を取得できなくなっていたため、修正しました(20.10.05)  
- 図書館の通知で表示されるURLが誤っていたため、修正しました(20.6.26)  
- __図書館システムの変更に伴い、改修を実施しました(2020.5.8)__  
- Cplus の通知が動作しないバグを確認・調査中(19.12.23)  
- メッセージに入る余計な空白の連続を除去するようアップデート (19.10.15)  


## 事前準備

### 1.LINE Notify

#### 1-1. LINE Notify を友達登録する  

アプリで __友達追加 > 公式アカウント > 検索キーワードに「Notify」と入れる__ と見つかると思います

#### 1-2. アクセストークンの取得  

[こちら](https://notify-bot.line.me/)のサイトからログインして、マイページに移動し、
__アクセストークンを発行する > トークン名を指定 (例: Chuo-U) > 通知を送信するトークグループから「1:1」を選択する > 発行する__  
で発行されたアクセストークンを控えておいてください    

(通知を送信するトークグループは 「1:1」以外も設定できますが、ユーザーの履修科目に対応したデータが返ってくるため、個々人での設定を推奨)  

### 2.heroku

#### 2-1. アカウント作成(すでに持っている場合はパス)  

[こちら](https://jp.heroku.com/)から

#### 2-2. Heroku CLIのインストール  

[こちら](https://devcenter.heroku.com/articles/heroku-cli)から自身のマシンに合ったものをインストール  

### 3.GitHub  
コマンドから、  
```
git clone https://github.com/at19990/cplus-line-notify.git
```  
でこのリポジトリをローカルPCの適当な場所に複製します  

もし、gitをインストールしていない場合には[こちら](https://employment.en-japan.com/engineerhub/entry/2017/01/31/110000)を参考に導入してください

## herokuへのデプロイ  

### 1. heroku へのログイン・アプリ作成  
コマンドから、
```  
# herokuにログイン
heroku login  

# アプリを作成  
# アプリ名は適当でよいが、ローカル(cplus-line-notify)と一致させると分かりやすい
heroku create <<アプリ名>>
```  
でアプリを作成  

### 2. ローカルとherokuの連携  
コマンドから、  
```
# cloneした cplus-line-notify の階層に移動  
cd <<cplus-line-notifyのパス>>  

# gitリポジトリに新規作成  
git init  

# ローカルとリモートをひもづけ  
heroku git:remote -a <<アプリ名>>
```  
で連携完了

### 3. ビルドパックの設定  
ブラウザから、 [こちら](https://dashboard.heroku.com/apps) にアクセスして
作成したアプリを開き、__settings__ タブを開いて __Build packs__ を探し、  
以下の2つのURLを    
- [https://github.com/heroku/heroku-buildpack-chromedriver.git](https://github.com/heroku/heroku-buildpack-chromedriver.git)  
- [https://github.com/heroku/heroku-buildpack-google-chrome.git](https://github.com/heroku/heroku-buildpack-google-chrome.git)  

__Add buildpack > Enter Buildpack URL にURLを入力 > Save Changes__  

からそれぞれセットします  


### 4. デプロイ  
コマンドから、
```
# バージョン管理の対象に追加
git add -A    

# 変更内容をコミット (コメントは「first commit」など適当なもので可)
git commit -m "<<コメント>>"  

# herokuにデプロイ  
git push heroku master
```  
でデプロイ完了  

### 5. 環境変数の追加  
LINEのトークンやログインパスワードをソースコードに書くのは危険なので、環境変数で設定します  
コマンドから、  
```
# 中央大学統合認証のユーザーID  
heroku config:set ENV_CHUO_SSO_USER_ID="<<ユーザーID>>" --app "<<アプリ名>>"  

# 中央大学統合認証のパスワード  
heroku config:set ENV_CHUO_SSO_PASSWORD="<<パスワード>>" --app "<<アプリ名>>"  

# CHOIS(図書館システム)のユーザーID  
heroku config:set ENV_CHUO_LIB_USER_ID="<<ユーザーID>>" --app "<<アプリ名>>"

# CHOISのパスワード  
heroku config:set ENV_CHUO_LIB_PASSWORD="<<パスワード>>" --app "<<アプリ名>>"

# LINE Notify のトークン (事前準備の際に控えたもの)
heroku config:set ENV_LINE_NOTIFY_TOKEN_CHUO_UNIV="<<トークン>>" --app "<<アプリ名>>"
```
で設定  

また、設定した環境変数は `heroku config` から確認可能です     


### 6.アドオンの追加  

アドオンの使用は無料ですが、クレジットカード情報を登録する必要があります(Account settingsから登録できます)   

登録が完了したら、コマンドから、  
```  
# データベースを利用するアドオン  
heroku addons:create heroku-redis:hobby-dev  

# 定期実行のためのアドオン  
heroku addons:create scheduler:standard  
```  
で追加します。    

#### 6-1. データベースの設定  

データベースの初期設定を行います。

```  
# データベースの管理画面を起動
heroku redis:cli  
```  

と入力して少し待ち、コマンド画面の左端に `>` と表示されたら、  

```  
# アプリ名を指定
> <<アプリ名>>

# 3つのデータを初期設定  
> set prev_manaba ""  
OK
> set prev_opac ""  
OK
> set prev_cplus ""  
OK
```  

3つとも `OK` と表示されたら `Ctrl + C` を押して管理画面を出ます。  

#### 6-2. 定期実行の設定  

定期実行のジョブを追加します  

以下の記事を参考に、1日に1回決まった時間に実行するための設定を行ってください  


[Herokuでお天気Pythonの定期実行](https://qiita.com/seigo-pon/items/ca9951dac0b7fa29cce0#%E5%AE%9A%E6%9C%9F%E5%AE%9F%E8%A1%8C%E8%A8%AD%E5%AE%9A)

注意事項  
- 設定時間はUTCなので、(通知を届けたい日本時間) - (9時間) で考える必要があります   
→ 通知の種類を決定する曜日や、メッセージに表示する日付に関しては、プログラム内で時差を計算して補正する仕様になっています


## テスト  

コマンドで、  
```
heroku run python main.py
```  
で動作確認できます  


## 免責事項  

 本プログラムにおける情報取得に関しては、正確を期しておりますが、ユーザーがこれを用いて行う一切の行為、および、それにより生じた損害について、当方は責任を負いかねます
