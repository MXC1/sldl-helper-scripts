# Remuxes all files in a directory to 320kbps MP3 format.
# Also updates .m3u8 playlists and .sldl indexes with the new file extension.
# Usage: python remux_to_mp3_320.py <directory_path>
# If the directory path is not provided, the script will prompt the user to select a directory.

import os
import subprocess
import sys
import time
import shutil
from mutagen import File
from mutagen.mp3 import MP3
from collections import defaultdict
import traceback
import tempfile
from log_error_to_file import log_error_to_file

# Dictionary to track file summaries
file_summary = defaultdict(int)

def get_audio_info(file_path):
    try:
        audio = File(file_path)
        if audio is None:
            return None
        
        file_info = {
            'format': audio.mime[0] if hasattr(audio, 'mime') else 'unknown',
            'bitrate': None
        }

        # If it's an MP3 file, use MP3-specific processing
        if isinstance(audio, MP3):
            bitrate = audio.info.bitrate // 1000  # Bitrate in kbps
            file_info['bitrate'] = f"{bitrate}kbps"
        elif hasattr(audio, 'mime') and audio.mime[0] == 'audio/flac':
            file_info['bitrate'] = "Lossless (FLAC)"

        return file_info
    except Exception as e:
        exception_details = traceback.format_exc()
        error_message = "File path: " + file_path + "\n"
        error_message = f"Error processing {file_path}: {e}"
        print(error_message)
        log_error_to_file(__file__, error_message)
        return None

def update_m3u8_files(directory, old_file, new_file):
    """Update all .m3u8 files in the directory to replace old_file with new_file."""
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.m3u8'):
                playlist_path = os.path.join(subdir, file)
                try:
                    with open(playlist_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Check if the old_file is in the playlist
                    if any(old_file in line for line in lines):
                        # Replace old_file references with new_file
                        updated_lines = [
                            line.replace(old_file, new_file) for line in lines
                        ]
                        
                        # Write back the updated lines to the file
                        with open(playlist_path, 'w', encoding='utf-8') as f:
                            f.writelines(updated_lines)

                        print(f"Updated playlist: {playlist_path}")

                except Exception as e:
                    error_message = f"Error updating playlist {playlist_path}: {e}"
                    print(error_message)
                    log_error_to_file(__file__, error_message)

def update_sldl_files(directory, old_file, new_file):
    """Update all .sldl files in the directory to replace old_file with new_file."""
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.sldl'):
                sldl_path = os.path.join(subdir, file)
                try:
                    with open(sldl_path, 'r', encoding='utf-8') as f:
                        # Read the single line, which starts with '#SLDL:'
                        line = f.readline().strip()

                    # Check if the old_file is in the SLDL line (ignoring the '#SLDL:' prefix)
                    if old_file in line:
                        # Replace old_file references with new_file
                        updated_line = line.replace(old_file, new_file)

                        # Write back the updated line to the file
                        with open(sldl_path, 'w', encoding='utf-8') as f:
                            f.write(f"#SLDL:{updated_line}")

                        print(f"Updated SLDL file: {sldl_path}")

                except Exception as e:
                    error_message = f"Error updating SLDL file {sldl_path}: {e}"
                    print(error_message)
                    log_error_to_file(__file__, error_message)               


def remux_to_320kbps_mp3(source_path, destination_path, directory):
    try:
        # Ensure destination folder exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Generate temporary file name for processing
        temp_fd, temp_destination_path = tempfile.mkstemp(suffix=".mp3")
        os.close(temp_fd)  # Close the file descriptor immediately

        # ffmpeg command to remux to 320kbps MP3
        command = [
            'ffmpeg', '-y',  # Overwrite without prompting
            '-i', source_path,  # Input file
            '-b:a', '320k',  # Audio bitrate
            '-map_metadata', '0',  # Copy metadata
            '-vn',  # Exclude video (if any)
            temp_destination_path  # Output temporary file
        ]
        
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            # print(f"Subprocess finished with return code {result.returncode}")
            # print(f"Subprocess stdout: {result.stdout.decode()}")
            # print(f"Subprocess stderr: {result.stderr.decode()}")
        except subprocess.CalledProcessError as e:
            print(f"Subprocess failed with return code {e.returncode}")
            print(f"Subprocess stdout: {e.stdout.decode()}")
            print(f"Subprocess stderr: {e.stderr.decode()}")
            raise

        # Ensure the file handle is released
        time.sleep(1)

        try:
            shutil.move(temp_destination_path, destination_path)
            print(f"File moved from {temp_destination_path} to {destination_path}")
        except OSError as e:
            print(f"Error moving file: {e}")
            raise
        
        # Update .m3u8 playlists and .sldl indexes with the new file extension
        # old_file = os.path.relpath(source_path, directory)
        # new_file = os.path.relpath(destination_path, directory)
        old_file = os.path.relpath(source_path, directory)
        destination_path = os.path.relpath(destination_path, directory)
        print("old file: ", source_path)
        print("new file: ", destination_path)
        update_m3u8_files(directory, old_file, destination_path)
        update_sldl_files(directory, old_file, destination_path)
        
        # Remove the original file after remuxing
        os.remove(source_path)
    except Exception as e:
        print(f"Error remuxing {source_path}: {e}")
        raise

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

                    # Remux if not 320kbps MP3
                    if audio_info['format'] != 'audio/mp3' or audio_info['bitrate'] != '320kbps':
                        destination_path = os.path.splitext(file_path)[0] + '.mp3'
                        remux_to_320kbps_mp3(file_path, destination_path, directory)
                else:
                    log_error_to_file(__file__, f"Error processing {file_path}: Audio info not found.")

def print_summary():
    print("\n--- Summary ---")
    total_files = sum(file_summary.values())
    print(f"Total files processed: {total_files}")
    print("\nBreakdown by format and bitrate:")
    for key, count in file_summary.items():
        print(f"{key}: {count}")
    print("-" * 50)
    
def remux_to_mp3_320(directory):
    if os.path.isdir(directory):
        try:
            walk_directory(directory)
            print_summary()
        except Exception as e:
            error_message = f"Unhandled error during execution: {e}"
            print(error_message)
            log_error_to_file(__file__, error_message)
    else:
        error_message = f"Invalid directory. Please check the path and try again."
        print(error_message)
        log_error_to_file(__file__, error_message)

# Entry point
if __name__ == '__main__':
    # Check if the directory is passed as an argument
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Prompt the user for the directory
        directory = input("Enter the directory to process: ").strip()
        
    remux_to_mp3_320(directory)
