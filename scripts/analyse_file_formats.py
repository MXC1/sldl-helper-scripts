# This script analyses the audio file formats and bitrates in a given directory and provides a summary of the results.
# It uses the Mutagen library to extract audio file information such as format and bitrate.
# The script can be run from the command line with the directory path as the first argument or by entering the directory path when prompted.

import os
import sys
from mutagen import File
from mutagen.mp3 import MP3
from collections import defaultdict

# Dictionary to track file summaries
file_summary = defaultdict(int)

def get_audio_info(file_path):
    try:
        audio = File(file_path)
        if audio is None:
            return None
        
        file_info = {
            'format': audio.mime[0],  # The MIME type gives the format (e.g., audio/mp3, audio/flac)
            'bitrate': None
        }

        # If it's an MP3 file, use MP3-specific processing
        if isinstance(audio, MP3):
            bitrate = audio.info.bitrate // 1000  # Bitrate in kbps
            file_info['bitrate'] = f"{bitrate}kbps"
        elif audio.mime[0] == 'audio/flac':
            file_info['bitrate'] = "Lossless (FLAC)"

        return file_info
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def walk_directory(directory):
    for subdir, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            if file_path.lower().endswith(('.mp3', '.flac', '.wav', '.aac', '.ogg')):  # Add more formats as needed
                audio_info = get_audio_info(file_path)
                if audio_info:
                    # Update the summary
                    key = f"{audio_info['format']} - {audio_info['bitrate'] or 'Unknown Bitrate'}"
                    file_summary[key] += 1

def print_summary():
    print("\n--- Summary ---")
    total_files = sum(file_summary.values())
    print(f"Total files processed: {total_files}")
    print("\nBreakdown by format and bitrate:")
    for key, count in file_summary.items():
        print(f"{key}: {count}")
    print("-" * 50)

# Entry point
if __name__ == '__main__':
    # Check if the directory is passed as an argument
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Prompt the user for the directory
        directory = input("Enter the directory to process: ").strip()

    if os.path.isdir(directory):
        walk_directory(directory)
        print_summary()
    else:
        print("Invalid directory. Please check the path and try again.")
