# Uses Selenium to scrape a SoundCloud playlist and save the track information to a CSV file.
# The CSV file is later used to download the tracks using slsk-batchdl.
# This is necessary because slsk-batchdl does not support SoundCloud URLs directly, but it does support csv files.

import sys
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time
from log_error_to_file import log_error_to_file

# Path to your WebDriver (update with the correct path for your system)
CHROME_DRIVER_PATH = r"C:\Program Files\Google\chromedriver-win64\chromedriver.exe"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Log levels: DEBUG, INFO, WARNING, ERROR
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def scrape_soundcloud_playlist(url, output_csv):
    """
    Scrapes a SoundCloud playlist and saves the track information to a CSV file.

    Args:
        url (str): The URL of the SoundCloud playlist.
        output_csv (str): The filename of the CSV file to save data.
    """
    try:
        logging.info("Initializing WebDriver.")
        # Set up the WebDriver
        service = Service(CHROME_DRIVER_PATH)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--mute-audio")  # Prevent SoundCloud starting playback
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=service, options=options)
        
        # import logging
        logger = logging.getLogger('urllib3.connectionpool')
        logger.setLevel(logging.INFO)

        logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        logger.setLevel(logging.WARNING)

        logging.info(f"Loading URL: {url}")
        # Load the URL
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely

        logging.debug("Retrieving page source.")
        # Get the page source after rendering JavaScript
        page_source = driver.page_source
        driver.quit()  # Close the browser

        logging.debug("Parsing page content.")
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find the playlist items
        playlist_items = soup.select('li.trackList__item')

        # Prepare the data
        data = []
        for item in playlist_items:
            artist_tag = item.select_one('.trackItem__username')
            track_tag = item.select_one('.trackItem__trackTitle')
            if artist_tag and track_tag:
                artist = artist_tag.text.strip()
                track = track_tag.text.strip()
                logging.debug(f"Found track: Artist = {artist}, Track = {track}")
                data.append([artist, track])

        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        # Save the data to a CSV file
        logging.info(f"Saving data to {output_csv}.")
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Artist', 'Track'])  # Write the header
            writer.writerows(data)  # Write the data

        logging.info(f"Data successfully saved to {output_csv}.")
    except Exception as e:
        error_message = f"An error occurred while scraping: {str(e)}"
        logging.error(error_message)
        log_error_to_file(__file__, error_message)
        raise  # Re-raise the exception for further handling

if __name__ == "__main__":
    try:
        # Check if the URL parameter is provided via `sys.argv`
        if len(sys.argv) < 2:
            logging.error("No URL parameter provided. Exiting.")
            sys.exit(1)

        # Get the URL and derive the CSV filename
        url = sys.argv[1]
        output_csv = "soundcloud_playlists/" + url.split("/")[-1] + ".csv"

        logging.info(f"Received URL: {url}")
        logging.info(f"Output CSV will be: {output_csv}")

        # Call the scraping function
        scrape_soundcloud_playlist(url, output_csv)
    except Exception as e:
        logging.error("Unhandled exception occurred. Exiting.")
        log_error_to_file(__file__, f"Unhandled exception: {str(e)}")
        sys.exit(1)
