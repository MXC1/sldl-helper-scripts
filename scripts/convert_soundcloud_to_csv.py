# Uses Selenium to scrape a SoundCloud playlist and save the track information to a CSV file.
# The CSV file is later used to download the tracks using slsk-batchdl.
# This is necessary because slsk-batchdl does not support SoundCloud URLs directly, but it does support csv files.

import sys
import os
import logging
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from log_error_to_file import log_error_to_file

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Log levels: DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def scroll_to_bottom(driver):
    """Scrolls to the bottom of the page to load all content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_soundcloud_playlist(url, output_csv):
    """Scrapes a SoundCloud playlist and saves the track information to a CSV file."""
    try:
        logging.info("Initializing WebDriver.")
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--mute-audio")  # Prevent SoundCloud starting playback
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=service, options=options)

        # Reduce noisy logs
        logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
        logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

        logging.info(f"Loading URL: {url}")
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely

        logging.debug("Scrolling to load all content.")
        scroll_to_bottom(driver)

        logging.debug("Retrieving page source.")
        page_source = driver.page_source
        driver.quit()

        logging.debug("Parsing page content.")
        soup = BeautifulSoup(page_source, 'html.parser')
        playlist_items = soup.select('li.trackList__item')

        data = []
        for item in playlist_items:
            artist_tag = item.select_one('.trackItem__username')
            track_tag = item.select_one('.trackItem__trackTitle')
            if artist_tag and track_tag:
                artist = artist_tag.text.strip()
                track = track_tag.text.strip()
                logging.debug(f"Found track: Artist = {artist}, Track = {track}")
                data.append([artist, track])

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        logging.info(f"Saving data to {output_csv}.")
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Artist', 'Track'])
            writer.writerows(data)

        logging.info(f"Data successfully saved to {output_csv}.")
    except Exception as e:
        error_message = f"An error occurred while scraping: {str(e)}"
        logging.error(error_message)
        log_error_to_file(__file__, error_message)
        raise

def convert_soundcloud_to_csv(url):
    try:
        output_csv = "soundcloud_playlists/" + url.split("/")[-1] + ".csv"
        logging.info(f"Received URL: {url}")
        logging.info(f"Output CSV will be: {output_csv}")
        scrape_soundcloud_playlist(url, output_csv)
        return output_csv
    except Exception as e:
        logging.error("Unhandled exception occurred. Exiting.")
        log_error_to_file(__file__, f"Unhandled exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Please enter the SoundCloud playlist URL: ")

    convert_soundcloud_to_csv(url)
