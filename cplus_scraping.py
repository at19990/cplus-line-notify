import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import datetime
import csv
import os


# Cplusにログインして情報取得
def login_ss():

    # メールアドレスとパスワードの指定
    USER = os.environ["ENV_CHUO_SSO_USER_ID"]
    PASS = os.environ["ENV_CHUO_SSO_PASSWORD"]

    # セッションを開始
    session = requests.session()

    # ログイン情報
    login_info = {
       "clickcheck": 0,
       "login": USER,
       "mode": "Login",
       "passwd": PASS
    }

    # Cplusにログイン
    url_login = "https://www.ac04.tamacc.chuo-u.ac.jp/ActiveCampus/module/Login.php"
    res = session.post(url_login, data=login_info)
    res.raise_for_status() # エラーなら例外発生

    # 授業変更を取得 (履修科目のみ)
    url_cancelled = "https://www.ac04.tamacc.chuo-u.ac.jp/ActiveCampus//module/Kyuko.php"
    # 全学なら KyukoDaigakuAll.php
    # 学部全体なら KyukoDaigakuAll.php?mode=gakubu  に module 以下を書き換える
    res = session.get(url_cancelled)
    res.raise_for_status()

    return res.text


# csvに書き出し
def wr_csv(html):

    bsObj = BeautifulSoup(html, "html.parser")

    # テーブル要素を分割して書き出し
    table = bsObj.findAll("table", {"id":"portlet_container"})[0]
    rows = table.findAll("tr")

    with open("data_cplus.csv", "w", encoding='utf-8', newline="") as file:
        writer = csv.writer(file, delimiter=",")
        for row in rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                csvRow.append(cell.get_text())
            writer.writerow(csvRow)


# メッセージ生成
def create_message():

    # Dataframeとして読込 2行目までは余分な情報なのでスキップ
    df = pd.read_csv("data_cplus.csv", encoding="utf_8", skiprows=2)

    # dfの行数 or Empty で判定
    # 情報あり → forで整形
    # e.g.) "休講情報はありません"
    # e.g.) 9/20 [休講] [金曜 1時限] 情報法 変更後教室

    # 日付を整形
    df["日付"] = pd.to_datetime(df["日付"])
    df["月"] = df["日付"].dt.month
    df["日"] = df["日付"].dt.day

    # 現在時刻の取得・メッセージの宣言
    dt_now = datetime.datetime.now()
    dt_now = str(dt_now.month) + "/" + str(dt_now.day)
    message = "\nCplusの情報 (" + dt_now + " 現在)\n\n"

    # メッセージ追加 情報がないときには代替テキスト
    if len(df) == 0:
        message += "授業変更の通知はありません"
    else:
        for i in range(0, len(df)):
            # 教室変更のときにはフォーマットを変更・変更後の教室を表示
            if df.loc[i, "変更後教室"] == "-":
                message += "・{0}/{1}【{2}】 <{3}> {4}\n".format(df.loc[i, "月"], df.loc[i, "日"], df.loc[i, "区分"], df.loc[i, "曜日・時限"], df.loc[i, "科目名"])
            else:
                message += "・{0}/{1}【{2}】 <{3}> {4} (変更後: {5})\n".format(df.loc[i, "月"], df.loc[i, "日"], df.loc[i, "区分"], df.loc[i, "曜日・時限"], df.loc[i, "科目名"], df.loc[i, "変更後教室"])

    message += "\nhttps://cplus.chuo-u.ac.jp"

    return message


# LINE Notify に送信
def send_line(message):

    line_url = "https://notify-api.line.me/api/notify"
    line_token = os.environ["ENV_LINE_NOTIFY_TOKEN_CHUO_UNIV"]
    headers = {'Authorization': 'Bearer ' + line_token}

    payload = {'message': message}
    r = requests.post(line_url, headers=headers, params=payload,)


def main():

    html = login_ss()
    wr_csv(html)
    message = create_message()
    send_line(message)
    os.remove('data_cplus.csv') # 送信終了後にファイル削除


if __name__ == "__main__":

    main()
