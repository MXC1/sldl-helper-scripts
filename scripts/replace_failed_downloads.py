# This script helps to replace downloads that have failed and update the corresponding .m3u8 and .sldl files with the new file path.
# The script reads the CSV file containing the list of tracks that have failed to download through slsk-batchdl.
# It prompts the user to select a replacement file for each entry.
# It then copies the replacement file to the destination directory and updates any .m3u8 and .sldl files with the new file path.

import os
import csv
import shutil
from tkinter import Tk, filedialog
import pyperclip
import random

# Constants
destination_dir = "../tracks_and_playlists"
replaced_files_dir = os.path.join(destination_dir, "_replaced_files")

# Ensure the replaced_files directory exists
os.makedirs(replaced_files_dir, exist_ok=True)

# Suppress root Tk window
Tk().withdraw()

def select_replacement_file(artist, title):
    """Open a file browser to select a replacement file."""
    pyperclip.copy(f"{artist} {title}")
    print(f"Copied to clipboard: {artist} {title}")
    print(f"Opening file browser to select replacement for: {title}")
    return filedialog.askopenfilename(title=f"Select Replacement for: {artist} - {title}")

def process_m3u8_files(track_title, new_file_path):
    """Search and replace the failed track entry in .m3u8 files."""
    print(f"Searching for .m3u8 files to update track: {track_title}")
    for root, _, files in os.walk(destination_dir):
        for file in files:
            if file.endswith(".m3u8"):
                file_path = os.path.join(root, file)
                # print(f"Checking file: {file_path}")
                updated = False
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if track_title in line:
                            print(f"Replacing line in {file_path}: {line.strip()} with {new_file_path}")
                            f.write(new_file_path + "\n")
                            updated = True
                        else:
                            f.write(line)
                if not updated:
                    # print(f"No matching line found for track: {track_title} in {file_path}")
                    pass

def process_sldl_files(track_title, new_file_path):
    """Search and update the failed track entry in .sldl files."""
    print(f"Searching for .sldl files to update track: {track_title}")
    for root, _, files in os.walk(destination_dir):
        for file in files:
            if file.endswith(".sldl"):
                file_path = os.path.join(root, file)
                # print(f"Checking file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print(f"Error reading file: {file_path}. Trying 'latin1' encoding.")
                    with open(file_path, 'r', encoding='latin1') as f:
                        content = f.read()

                if track_title in content:
                    print(f"Found entry for {track_title} in {file_path}")
                    entries = content.split(';')
                    updated_entries = []
                    for entry in entries:
                        if track_title in entry:
                            print(f"Updating entry: {entry}")
                            parts = entry.split(',')
                            parts[-3:] = ['0', '3', '0']
                            updated_entries.append(','.join(parts))
                        else:
                            updated_entries.append(entry)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(';'.join(updated_entries))

def get_processing_order():
    """Prompt the user to select the processing order."""
    print("Select processing order for the CSV file:")
    print("1. Top-down")
    print("2. Bottom-up")
    print("3. Random")
    choice = input("Enter 1, 2, or 3: ")
    return choice

def main():
    print("Starting script...")
    input_file = "../failed_downloads.csv"
    if not input_file:
        print("No input file selected. Exiting.")
        return

    print(f"Selected input file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    order_choice = get_processing_order()
    if order_choice == '1':
        rows_to_process = rows
    elif order_choice == '2':
        rows_to_process = reversed(rows)
    elif order_choice == '3':
        rows_to_process = random.sample(rows, len(rows))
    else:
        print("Invalid choice. Exiting.")
        return

    try:
        for row in rows_to_process:
            track_title = row[1]
            track_artist = row[2]
            if not track_title:
                print("Empty track title found. Skipping row.")
                continue

            print(f"Processing track: {track_title}")
            replacement_file = select_replacement_file(track_artist, track_title)

            if not replacement_file:
                print(f"No file selected for {track_title}. Skipping.")
                continue

            print(f"Selected replacement file: {replacement_file}")
            # Copy the replacement file to the replaced_files directory
            dest_path = os.path.abspath(shutil.copy(replacement_file, replaced_files_dir))
            print(f"Copied to {dest_path}")

            # Update .m3u8 files
            process_m3u8_files(track_title, dest_path)

            # Update .sldl files
            process_sldl_files(track_title, dest_path)

            # Remove processed row from the list
            rows.remove(row)

            # Update the input file after each row is processed
            with open(input_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving progress and exiting...")
        # Save the remaining rows to the input file
        with open(input_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print("Progress saved. Exiting.")

if __name__ == "__main__":
    main()
