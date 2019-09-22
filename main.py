import datetime
import subprocess

def main():

    dt_now = datetime.datetime.today() + datetime.timedelta(hours=9)

    weekday = dt_now.weekday()

    if weekday <= 4:  # 平日に実行
        subprocess.call(["python","manaba_scraping.py"])
    elif weekday == 5: # 土曜のみ実行
        subprocess.call(["python","opac_scraping.py"])
    elif weekday == 6: # 日曜のみ実行
        subprocess.call(["python","cplus_scraping.py"])

if __name__ == "__main__":
    main()
