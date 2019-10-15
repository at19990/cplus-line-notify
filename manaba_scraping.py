import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import datetime
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dateutil.relativedelta import relativedelta
import re


# manaba にブラウザからログインして情報取得
def login_wd(dt_now):
    # 現在の年度を取得
    fiscal_year = dt_now - relativedelta(months=1)
    fiscal_year = str(fiscal_year.year)

    USER = os.environ["ENV_CHUO_SSO_USER_ID"]
    PASS = os.environ["ENV_CHUO_SSO_PASSWORD"]

    GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google-chrome-stable'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
    #GOOGLE_CHROME_PATH = os.environ['GOOGLE_CHROME_BIN']
    #CHROMEDRIVER_PATH = os.environ['GOOGLE_CHROME_SHIM']
    #driver_path = os.environ['GOOGLE_CHROME_SHIM']

    # chrome の起動オプション
    opt = webdriver.ChromeOptions()
    opt.binary_location = GOOGLE_CHROME_PATH
    opt.add_argument('--no-sandbox')
    opt.add_argument('--headless')
    opt.add_argument('--disable-gpu')

    # selenium でブラウザを操作して取得
    driver = webdriver.Chrome(options=opt, executable_path= CHROMEDRIVER_PATH )
    driver.get("http://www2.chuo-u.ac.jp/com/manaba/")
    driver.implicitly_wait(3)
    driver.find_element_by_tag_name("area").click()
    driver.implicitly_wait(3)
    driver.find_element_by_id('username_input').send_keys(USER)
    driver.implicitly_wait(3)
    driver.find_element_by_id('password_input').send_keys(PASS)
    driver.implicitly_wait(3)
    driver.find_element_by_css_selector(".form-button").click()
    driver.implicitly_wait(3)
    driver.get("https://room.chuo-u.ac.jp/ct/home___y"+ fiscal_year +"?chglistformat=list")
    driver.implicitly_wait(3)
    html_source = driver.page_source
    driver.close()
    driver.quit()

    return html_source


# csv に書き出し
def wr_csv(html_source):

    bsObj = BeautifulSoup(html_source, "html.parser")

    # テーブル要素を分割して書き出し
    table = bsObj.findAll("table", {"class":"courselist"})[0]
    rows = table.findAll("tr")

    with open("data_manaba.csv", "w", encoding='utf-8', newline="") as file:
        writer = csv.writer(file, delimiter=",")
        for row in rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                csvRow.append(cell.get_text().replace('\n', ''))
            # img の src 要素を書き出し → ファイル名で状態を判定
            for cell in row.findAll(['img']):
                csvRow.append(cell['src'])
            writer.writerow(csvRow)


# メッセージ生成
def create_message(dt_now):

    df = pd.read_csv("data_manaba.csv", encoding="utf_8", usecols=[0, 6, 7, 9], header=None, skiprows=1)

    course_assignment = "【課題】\n"
    course_news = "【コースニュース】\n"
    course_thread = "【掲示板】\n"

    for i in range(0, len(df)):
        #try:
            if df.loc[i, 7] != "/icon-coursedeadline-off.png": # 課題
                if df.loc[i, 0] != "infoss情報倫理": # infossは授業科目ではないが課題が表示され続けるため除外
                    course_assignment += "・" + re.sub(r" +", " ", df.loc[i, 0]) + "\n"
        #except KeyError:
            #pass

        #try:
            if df.loc[i, 6] == "/icon_coursenews_on.png": # コースニュース
                course_news += "・" + re.sub(r" +", " ", df.loc[i, 0]) + "\n"
        #except KeyError:
            #pass

        #try:
            if df.loc[i, 9] == "/icon_coursethread_on.png": # 掲示板
                course_thread += "・" + re.sub(r" +", " ", df.loc[i, 0]) + "\n"
        #except KeyError:
            #pass

    # 要素 1 つもがなければ代替テキスト
    if course_assignment == "【課題】\n":
        course_assignment += "　ありません\n"
    if course_news == "【コースニュース】\n":
        course_news += "　ありません\n"
    if course_thread == "【掲示板】\n":
        course_thread += "　ありません\n"

    # 日付テキストの生成
    dt_now = str(dt_now.month) + "/" + str(dt_now.day)

    message = "\nmanabaの情報 ({0} 現在)\n\n{1}\n{2}\n{3}\nhttps://room.chuo-u.ac.jp/ct/home".format(dt_now, course_assignment, course_news, course_thread)

    return message


# LINE Notify に送信
def send_line(message):

    line_url = "https://notify-api.line.me/api/notify"
    line_token = os.environ["ENV_LINE_NOTIFY_TOKEN_CHUO_UNIV"]
    headers = {'Authorization': 'Bearer ' + line_token}

    payload = {'message': message}
    r = requests.post(line_url, headers=headers, params=payload,)


def main():

    dt_now = datetime.datetime.now() + datetime.timedelta(hours=9)
    html_source = login_wd(dt_now)
    wr_csv(html_source)
    message = create_message(dt_now)
    send_line(message)
    os.remove('data_manaba.csv') # 送信終了後にファイル削除


if __name__ == "__main__":

    main()
