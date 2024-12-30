# Logs failed downloads to a CSV file.
# Also removes the entry from the CSV file if the download was successful, so that it remains an up-to-date list of files that are missing.
# The CSV file can then later be used by `replace_failed_downloads.py` to import the failed download from elsewhere.

import sys
import csv
import os
import portalocker
import traceback
from datetime import datetime
from log_error_to_file import log_error_to_file

def log_debug(message):
    """Logs debug messages to the console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def process_download(file_details):
    try:
        # Extract details
        path = file_details.get('path', '')
        title = file_details.get('title', '')
        artist = file_details.get('artist', '')
        album = file_details.get('album', '')
        uri = file_details.get('uri', '')
        length = file_details.get('length', '')
        failure_reason = file_details.get('failure-reason', '')
        state = file_details.get('state', '')

        log_debug(f"Extracted details: {file_details}")

        # Path to the CSV log file
        failed_downloads_csv = '../failed_downloads.csv'

        # Create the file if it doesn't exist
        open(failed_downloads_csv, 'a', encoding='utf-8').close()

        # Open the file with portalocker to enforce cross-process locking
        with open(failed_downloads_csv, 'r+', newline='', encoding='utf-8') as f:
            # try:
                portalocker.lock(f, portalocker.LOCK_EX)  # Exclusive lock
                remove_successful_download_from_failed_downloads_csv(
                    f, state, title, artist, failed_downloads_csv
                )
                append_failed_download_if_not_already_in_file(
                    f, path, title, artist, album, uri, length, failure_reason, state, failed_downloads_csv
                )
            # finally:
            #     portalocker.unlock(f)  # Explicitly release lock in case of error
    except Exception as e:
        exception_details = traceback.format_exc()
        error_message = "File details:\n" + str(file_details) + "\n" + exception_details
        log_error_to_file(__file__, f"Error in log_failed_downloads: {error_message}")

        
def remove_successful_download_from_failed_downloads_csv(f,state,title,artist,failed_downloads_csv):
    # Read all rows into a list
    f.seek(0)
    reader = csv.reader(f)
    rows = list(reader)

    # Only filter and update rows if the current state is 'Downloaded' or 'Exists'
    if state in ['Downloaded', 'Exists']:
        updated_rows = [
            row for row in rows
            if not (row[1] == title and row[2] == artist)
        ]

        # Move file pointer to the beginning and truncate the file
        f.seek(0)
        f.truncate()

        # Write updated rows back to the file
        writer = csv.writer(f)
        writer.writerows(updated_rows)
        log_debug(f"Removed successful download from {failed_downloads_csv}")
        
def append_failed_download_if_not_already_in_file(f, path, title, artist, album, uri, length, failure_reason, state, failed_downloads_csv):
    f.seek(0)
    reader = csv.reader(f)

    # Check if the file already exists in the log
    file_exists = any(row[1] == title and row[2] == artist for row in reader)

    # If the file doesn't exist, append the details
    if not file_exists and state in ['Failed', 'NotFoundLastTime']:
        writer = csv.writer(f)
        writer.writerow([path, title, artist, album, uri, length, failure_reason, state])
        log_debug(f"Logged details to {failed_downloads_csv}")

    else:
        log_debug(f"Skipped logging for file: {path}, state: {state}")

if __name__ == "__main__":
    try:
        # Log the raw arguments for debugging
        log_debug(f"Raw arguments: {sys.argv}")

        # The file details are passed as arguments
        file_details = dict(zip(
            ['path', 'title', 'artist', 'album', 'uri', 'length', 'failure-reason', 'state'],
            sys.argv[1:]
        ))

        process_download(file_details)
    except Exception as e:
        log_error_to_file(__file__,f"Fatal error in main: {e}")
    finally:
        # input()
        pass  # No need for interactive input
