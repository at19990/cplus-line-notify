import datetime
import subprocess

def main():

    subprocess.call(["python","manaba_scraping.py"])
    subprocess.call(["python","opac_scraping.py"])
    subprocess.call(["python","cplus_scraping.py"])

if __name__ == "__main__":
    main()
