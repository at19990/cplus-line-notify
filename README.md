# cplus-line-notify (beta版)   

<img src="https://user-images.githubusercontent.com/16556629/65378387-8995c100-dcf2-11e9-9aee-4eccc10600c1.JPG" width=300px>

  
## About  
Cplusの情報とmanabaの情報をLINEに通知するBotです (中央大学の学生向け)  
デフォルトでは月～土曜日にmanabaの通知 (課題・コースニュース・掲示板) ・日曜日にCplus (授業変更情報) の通知を行います   
もともと自分用に作ったもので、まだテストも十分でないbeta版なので安定的に動作するかは不明  
導入方法は下記を参照    
  
  
## 事前準備

### 1.LINE Notify

#### 1-1. LINE Notify を友達登録する  

アプリで __友達追加 > 公式アカウント > 検索キーワードに「Notify」と入れる__ と見つかるはず

#### 1-2. アクセストークンの取得  

[こちら](https://notify-bot.line.me/)のサイトからログインして、マイページに移動  
__アクセストークンを発行する > トークン名を指定 (例: Chuo-U) > 通知を送信するトークグループから「1:1」を選択する > 発行する__  
で発行されたアクセストークンを控えておく  
  
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
でこのリポジトリをローカルの適当な場所にコピーする  
  
## herokuへのデプロイ  

### 1. heroku へのログイン・アプリ作成  
コマンドから、
```  
# herokuにログイン
heroku login  
  
# アプリを作成  
# アプリ名は適当でよいが、ローカル(cplus-line-notify)と一致させると分かりやすい
heroku create <アプリ名>
```  
でアプリを作成  
  
### 2. ローカルとherokuの連携  
コマンドから、  
```
# cloneした cplus-line-notify の階層に移動  
cd <cplus-line-notifyのパス>  
  
# gitリポジトリに新規作成  
git init  
  
# ローカルとリモートをひもづけ  
heroku git:remote -a <アプリ名>
```  
で連携完了 

### 3. ビルドパックの設定  
ブラウザから、 [こちら](https://dashboard.heroku.com/apps) にアクセスして
作成したアプリを開き、__settings__ タブを開いて __Build packs__ を探す  
以下の2つのURLを    
- [https://github.com/heroku/heroku-buildpack-chromedriver.git](https://github.com/heroku/heroku-buildpack-chromedriver.git)  
- [https://github.com/heroku/heroku-buildpack-google-chrome.git](https://github.com/heroku/heroku-buildpack-google-chrome.git)  
  
__Add buildpack > Enter Buildpack URL にURLを入力 > Save Changes__  
  
からそれぞれセット
  

### 4. デプロイ  
コマンドから、
```
# バージョン管理の対象に追加
git add .  
  
# 変更内容をコミット (コメントは「first commit」など適当なもので可)
git commit -m "コメント"  
  
# herokuにデプロイ  
git push heroku master
```  
でデプロイ完了  
  
### 5. 環境変数の追加  
LINEのトークンやログインパスワードをソースコードに書くのは危険なので、環境変数で設定します  
コマンドから、  
```
# 中央大学統合認証のユーザーID  
heroku config:set ENV_CHUO_SSO_USER_ID="<ユーザーID>" --app "<アプリ名>"  
  
# 中央大学統合認証のパスワード  
heroku config:set ENV_CHUO_SSO_PASSWORD="<パスワード>" --app "<アプリ名>"  
  
# LINE Notify のトークン (事前準備の際に控えたもの)
heroku config:set ENV_LINE_NOTIFY_TOKEN_CHUO_UNIV="<トークン>" --app "<アプリ名>"
```
で設定  
  
また、設定した環境変数は `heroku config` から確認可能   
  
## テスト  
  
コマンドで、  
```
heroku run python main.py
```  
で動作確認できます  
  
## 定期実行の設定  
  
毎日決まった時間に動作するようにアドオンを設定します  

### クレジットカード登録  

この機能自体は無料ですが、アドオンを使うにはクレジットカード情報を登録する必要があります(Account settingsから登録できます)   

### 定期実行ジョブの追加  
  
 以下の記事を参考に、1日に1回定期実行するための設定を行ってください  
   
 
[Herokuでお天気Pythonの定期実行](https://qiita.com/seigo-pon/items/ca9951dac0b7fa29cce0#%E5%AE%9A%E6%9C%9F%E5%AE%9F%E8%A1%8C%E8%A8%AD%E5%AE%9A)
  
注意事項  
- 設定時間はUTCなので、日本時間 - 9時間 で考える必要があります  
- このプログラムでは、月～土曜日にmanabaの通知・日曜日にCplusの通知をそれぞれ配信することを想定しています  
→ 曜日も UTC で考える必要があるので、同じ曜日に動作させるには、実行時間を　9:00~14:00 (UTC) に設定する必要があります  
  
## 免責事項  

 本プログラムにおける情報取得に関しては、正確を期しておりますが、ユーザーがこれを用いて行う一切の行為、および、それにより生じた損害について、当方は責任を負いかねます
  
