import os
import csv
import shutil
from tkinter import Tk, filedialog
import pyperclip

# Constants
destination_dir = "E:\\Music\\sldl\\tracks_and_playlists"

# Suppress root Tk window
Tk().withdraw()

# def select_input_file():
#     """Open a file browser to select the input file."""
#     print("Opening file browser to select input file...")
#     return filedialog.askopenfilename(title="Select the Input File")

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

def main():
    print("Starting script...")
    input_file = "E:\Music\sldl\failed_downloads.csv"
    if not input_file:
        print("No input file selected. Exiting.")
        return

    print(f"Selected input file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    try:
        for row in rows[:]:  # Iterate over a copy of the list
            track_title = row[1]
            track_artist = row[2]
            if not track_title:
                print("Empty track title found. Skipping row.")
                continue

            print(f"Processing track: {track_title}")
            replacement_file = select_replacement_file(track_artist,track_title)

            if not replacement_file:
                print(f"No file selected for {track_title}. Skipping.")
                continue

            print(f"Selected replacement file: {replacement_file}")
            # Copy the replacement file to the destination directory
            dest_path = shutil.copy(replacement_file, destination_dir)
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
