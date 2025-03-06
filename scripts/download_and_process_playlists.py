# Download and process Spotify and SoundCloud playlists using sldl and other scripts.
# This is the 'master' script that calls other scripts to download and process playlists.

import os
import subprocess
import csv
from log_error_to_file import log_error_to_file
from convert_soundcloud_to_csv import convert_soundcloud_to_csv
from rename_playlists import rename_playlists
from remux_to_mp3_320 import remux_to_mp3_320

def read_playlists_from_file(file_path):
    playlists = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                url = row[0].strip().strip('"')
                comment = row[1].strip().strip('"') if len(row) > 1 else None
                if comment:
                    playlists.append((url, comment))
                else:
                    playlists.append(url)
    return playlists

try:
    soundcloud_csv_paths = []

    # Read playlists from file
    playlists = read_playlists_from_file('../playlists.csv')
    total_playlists = len(playlists)

    # Process all playlists
    for index, item in enumerate(playlists):
        print(f"\n\nProcessing playlist {index + 1}/{total_playlists}")
        if isinstance(item, tuple):
            url, comment = item
            if "spotify.com" in url:
                print(f"Downloading Spotify playlist: {comment}")
                subprocess.run(["sldl", url], check=True)
        elif isinstance(item, str) and "soundcloud.com" in item:
            print(f"Processing SoundCloud playlist: {item}")
            convert_soundcloud_to_csv(item)

    # Find CSV files in the soundcloud_playlists directory
    soundcloud_csv_dir = "./soundcloud_playlists"
    if os.path.exists(soundcloud_csv_dir):
        for file_name in os.listdir(soundcloud_csv_dir):
            if file_name.endswith(".csv"):
                soundcloud_csv_paths.append(os.path.join(soundcloud_csv_dir, file_name))

    # Pass all CSV files from SoundCloud playlists to sldl
    for csv_path in soundcloud_csv_paths:
        print(f"Passing SoundCloud CSV to sldl: {csv_path}")
        subprocess.run(["sldl", "--desperate", "--strict-artist", csv_path], check=True)
        
    # Remove SoundCloud CSV files once finished with them
    for csv_path in soundcloud_csv_paths:
        os.remove(csv_path)

    # Rename Spotify playlists
    print("Renaming playlists...")
    rename_playlists("../tracks_and_playlists/")

    # Remux all files to mp3 320kbps
    print("Remuxing files to mp3 320kbps...")
    remux_to_mp3_320("../tracks_and_playlists/")

    print("All tasks completed!")

except subprocess.CalledProcessError as e:
    error_message = f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.\n{e.stderr}"
    log_error_to_file("download_and_process_playlists.py", error_message)
    print(f"An error occurred. Details written to the log file: {e}")

except Exception as e:
    error_message = str(e)
    log_error_to_file("download_and_process_playlists.py", error_message)
    print(f"An unexpected error occurred. Details written to the log file: {e}")
