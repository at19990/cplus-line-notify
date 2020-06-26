import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import numpy as np
import datetime
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dateutil.relativedelta import relativedelta
import lxml
import re
import redis


# manaba にブラウザからログインして情報取得
def login_wd(dt_now):
    # 現在の年度を取得
    fiscal_year = dt_now - relativedelta(months=1)
    fiscal_year = str(fiscal_year.year)

    USER = os.environ["ENV_CHUO_LIB_USER_ID"]
    PASS = os.environ["ENV_CHUO_LIB_PASSWORD"]

    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome-stable'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'


    # chrome の起動オプション
    opt = webdriver.ChromeOptions()
    opt.binary_location = GOOGLE_CHROME_PATH
    opt.add_argument('--no-sandbox')
    opt.add_argument('--headless')
    opt.add_argument('--disable-gpu')

    # selenium でブラウザを操作して取得
    driver = webdriver.Chrome(options=opt, executable_path= CHROMEDRIVER_PATH )
    driver.get("https://opac.library.chuo-u.ac.jp/")
    driver.implicitly_wait(3)
    driver.find_element_by_css_selector("a.libuse_riyou_login_button").click()
    driver.implicitly_wait(3)
    driver.find_element_by_name('userid').send_keys(USER)
    driver.implicitly_wait(3)
    driver.find_element_by_name('password').send_keys(PASS)
    driver.implicitly_wait(3)
    driver.find_element_by_xpath("//input[contains(@alt,'ログイン')]").click()
    driver.implicitly_wait(3)
    driver.get("https://ufinity.library.chuo-u.ac.jp/iwjs0002opc/lenlst.do")
    driver.implicitly_wait(3)
    html_source = driver.page_source
    driver.close()
    driver.quit()

    return html_source


# メッセージ生成
def create_message(dt_now, html_source):

    lend_df = pd.read_html(html_source)[0]

    lend_df["返却期限日"] = pd.to_datetime(lend_df["返却期限日"])
    lend_df["月"] = lend_df["返却期限日"].dt.month
    lend_df["日"] = lend_df["返却期限日"].dt.day
    lend_df2 = pd.concat([lend_df, lend_df['書誌事項'].str.extract(r'(^.+?(?=:|/))', expand=True)], axis=1).drop('書誌事項', axis=1)
    lend_df2.rename(columns={0: 'タイトル'}, inplace=True)


    lend_cond = "【貸出状況】\n"


    if len(lend_df2) != 0:
        for i in range(0, len(lend_df2)):
            lend_cond += "・{0} (~{1}/{2}) ".format(lend_df2.loc[i, 'タイトル'], lend_df2.loc[i, '月'], lend_df2.loc[i, '日'])
            lend_cond += "\n"
    else:
        lend_cond += "　ありません\n"

    # 日付テキストの生成
    dt_now = str(dt_now.month) + "/" + str(dt_now.day)

    message = "\n図書館の情報 ({0} 現在)\n\n{1}\nhttps://opac.library.chuo-u.ac.jp/".format(dt_now, lend_cond)

    return message


# LINE Notify に送信
def send_line(message):

    line_url = "https://notify-api.line.me/api/notify"
    line_token = os.environ["ENV_LINE_NOTIFY_TOKEN_CHUO_UNIV"]
    headers = {'Authorization': 'Bearer ' + line_token}

    payload = {'message': message}
    r = requests.post(line_url, headers=headers, params=payload,)


def main():

    #データベースに接続
    r = redis.from_url(os.environ["REDIS_URL"], db=0, decode_responses=True)

    dt_now = datetime.datetime.now() + datetime.timedelta(hours=9)
    html_source = login_wd(dt_now)
    message = create_message(dt_now, html_source)

    #前のメッセージと比較し、同じ場合は送らない
    message_except_date = re.sub('\(.+現在\)', '', message)

    prev_message =  r.get('prev_opac')
    prev_message_except_date = re.sub('\(.+現在\)', '', prev_message)
    r.set('prev_opac', message)


    if(message_except_date != prev_message_except_date):
        send_line(message)


if __name__ == "__main__":

    main()
