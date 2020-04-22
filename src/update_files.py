import os
import sys
import cities_parser as cp
import imh_website_scraper
import query_script.download_telegram_messages as download_telegram

CITIES_DIR = r"./telegram_files/raw_cities_files"
OUTPUT_DIR = r"../data/"


def main():
    download_telegram.main_runner()

    for f in os.listdir(CITIES_DIR):
        path = os.path.join(CITIES_DIR, f)
        cities_parser = cp.CitiesFileParser(path, OUTPUT_DIR)
        cities_parser.run()

    imh_website_scraper.main(OUTPUT_DIR)


if __name__ == "__main__":
    main()
