import datetime
import subprocess

def main():
    weekday = datetime.date.today().weekday()

    if weekday <= 5:  # 平日 + 土曜 に実行
        subprocess.call(["python","manaba_scraping.py"])
    elif weekday == 6: # 日曜のみ実行
        subprocess.call(["python","cplus_scraping.py"])

if __name__ == "__main__":
    main()
