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


# manaba にブラウザからログインして情報取得
def login_wd(dt_now):
    # 現在の年度を取得
    fiscal_year = dt_now - relativedelta(months=1)
    fiscal_year = str(fiscal_year.year)

    USER = os.environ["ENV_CHUO_SSO_USER_ID"]
    PASS = os.environ["ENV_CHUO_LIB_PASSWORD"]

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
    driver.get("http://www.library.chuo-u.ac.jp/opac/")
    driver.implicitly_wait(3)
    driver.find_element_by_css_selector(".nav_login a").click()
    driver.implicitly_wait(3)
    driver.find_element_by_name('U_ID').send_keys(USER)
    driver.implicitly_wait(3)
    driver.find_element_by_name('U_PW').send_keys(PASS)
    driver.implicitly_wait(3)
    driver.find_element_by_xpath("//input[contains(@alt,'ログイン')]").click()
    driver.implicitly_wait(3)
    driver.find_element_by_link_text("貸出予約状況照会").click()
    driver.implicitly_wait(3)
    html_source = driver.page_source
    driver.close()
    driver.quit()

    return html_source



# csv に書き出し
def wr_csv(html_source):

    bsObj = BeautifulSoup(html_source, "html.parser")

    # テーブル要素を分割して書き出し
    lend_table = bsObj.findAll("table", {"class":"lend_table"})[0]
    lend_rows = lend_table.findAll("tr")

    with open("data_opac_lend.csv", "w", encoding='utf-8', newline="") as file:
        writer = csv.writer(file, delimiter=",")
        for row in lend_rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                csvRow.append(cell.get_text().replace('\n', ''))
            writer.writerow(csvRow)

    # テーブル要素を分割して書き出し
    reservation_table = bsObj.findAll("table", {"class":"reservation_table"})[0]
    reservation_rows = reservation_table.findAll("tr")

    with open("data_opac_reservation.csv", "w", encoding='utf-8', newline="") as file:
        writer = csv.writer(file, delimiter=",")
        for row in reservation_rows:
            csvRow = []
            for cell in row.findAll(['td', 'th']):
                csvRow.append(cell.get_text().replace('\n', ''))
            writer.writerow(csvRow)


# メッセージ生成
def create_message(dt_now):

    lend_df = pd.read_csv("data_opac_lend.csv", encoding="utf_8", usecols=[6, 7, 9, 10])
    reservation_df = pd.read_csv("data_opac_reservation.csv", encoding="utf_8", usecols=[5, 6, 8, 9])

    lend_df["返却期限日"] = pd.to_datetime(lend_df["返却期限日"])
    lend_df["月"] = lend_df["返却期限日"].dt.month
    lend_df["日"] = lend_df["返却期限日"].dt.day
    lend_df2 = pd.concat([lend_df, lend_df['タイトル/著者/出版者/出版年'].str.split('/', expand=True)], axis=1).drop('タイトル/著者/出版者/出版年', axis=1)
    lend_df2.rename(columns={0: 'タイトル'}, inplace=True)
    lend_df2["延滞日数"].astype(np.int64)
    lend_df2["延長回数"].astype(np.int64)

    reservation_df["有効期限日"] = pd.to_datetime(reservation_df["有効期限日"])
    reservation_df["月"] = reservation_df["有効期限日"].dt.month
    reservation_df["日"] = reservation_df["有効期限日"].dt.day
    reservation_df2 = pd.concat([reservation_df, reservation_df['タイトル/著者/出版者/出版年'].str.split('/', expand=True)], axis=1).drop('タイトル/著者/出版者/出版年', axis=1)
    reservation_df2.rename(columns={0: 'タイトル'}, inplace=True)


    # print(lend_df2)

    # print(reservation_df2)

    lend_cond = "【貸出状況】\n"
    reservation_cond = "【予約状況】\n"

    # 10/5まで 「ああああああ」 延長済み 延滞中

    if len(lend_df2) != 0:
        for i in range(0, len(lend_df2)):
            lend_cond += "・{0} {1}/{2}まで ".format(lend_df2.loc[i, 'タイトル'], lend_df2.loc[i, '月'], lend_df2.loc[i, '日'])
            if lend_df2.loc[i, '延長回数'] > 0 and lend_df2.loc[i, '延滞日数'] > 0:
                lend_cond += " (延長済・延滞中)"
            elif lend_df2.loc[i, '延長回数'] > 0:
                lend_cond += " (延長済)"
            elif lend_df2.loc[i, '延滞日数'] > 0:
                lend_cond += " (延滞中)"
            lend_cond += "\n"
    else:
        lend_cond += "　ありません\n"

    if len(reservation_df2) != 0:
        for i in range(0, len(reservation_df2)):
            reservation_cond += "・{0} {1}/{2}まで ({3})\n".format(reservation_df2.loc[i, 'タイトル'], reservation_df2.loc[i, '月'], reservation_df2.loc[i, '日'], reservation_df2.loc[i, '資料状態'])
    else:
        reservation_cond += "　ありません\n"

    # 日付テキストの生成
    dt_now = str(dt_now.month) + "/" + str(dt_now.day)

    message = "\n図書館の情報 ({0} 現在)\n\n{1}\n{2}\nhttp://www.library.chuo-u.ac.jp/opac/".format(dt_now, lend_cond, reservation_cond)

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
    os.remove('data_opac_lend.csv') # 送信終了後にファイル削除
    os.remove('data_opac_reservation.csv')



if __name__ == "__main__":

    main()
