import os
import logging
import cities_parser as cp
import imh_website_scraper
import query_script.download_telegram_messages as download_telegram

SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(SCRIPT_DIR,'..',"data")
CITIES_DIR = os.path.join(SCRIPT_DIR,"telegram_files","raw_cities_files")

def main():
    # try:
    #     download_telegram.main_runner()
    # except Exception as e:
    #     print('Error at %s', 'telegram scraping', exc_info=e)

    try:
        for f in os.listdir(CITIES_DIR):
            path = os.path.join(CITIES_DIR, f)
            cities_parser = cp.CitiesFileParser(path, OUTPUT_DIR)
            cities_parser.run()
    except Exception as e:
        print('Error at %s', 'cities parsing')
    try:
        imh_website_scraper.main(OUTPUT_DIR)
    except Exception as e:
        print('Error at %s', 'ihm website scraping')



if __name__ == "__main__":
    main()
