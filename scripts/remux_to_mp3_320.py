# Remuxes all files in a directory to 320kbps MP3 format.
# Also updates .m3u8 playlists and .sldl indexes with the new file extension.
# Usage: python remux_to_mp3_320.py <directory_path>
# If the directory path is not provided, the script will prompt the user to select a directory.

import os
import subprocess
import sys
import re
from mutagen import File
from mutagen.mp3 import MP3
from collections import defaultdict
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
                    
def sanitize_filename(filename):
    # Define characters to remove or replace
    problematic_chars = r'[<>:"/\|?*;]'  # This regex includes semicolons, and other common problematic characters.
    sanitized_filename = re.sub(problematic_chars, '', filename)
    return sanitized_filename                    


def remux_to_320kbps_mp3(source_path, destination_path, directory):
    try:
        # Ensure destination folder exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        source_path = sanitize_filename(source_path)
        destination_path = sanitize_filename(destination_path)

        # Generate temporary file name for processing
        temp_destination_path = destination_path.rsplit('.', 1)
        temp_destination_path = f"{temp_destination_path[0]}_temp.{temp_destination_path[1]}"  # Add _temp to the filename
        
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
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
            print(f"Remuxed: {source_path} -> {temp_destination_path}")
            
            # Update .m3u8 playlists and .sldl indexes with the new file extension
            old_file = os.path.relpath(source_path, directory)
            new_file = os.path.relpath(temp_destination_path, directory)
            update_m3u8_files(directory, old_file, new_file)
            update_sldl_files(directory, old_file, new_file)
            
            # Replace the original file with the remuxed temporary file
            os.replace(temp_destination_path, destination_path)
            print(f"Replaced original file with remuxed file: {destination_path}")
            
            # Remove the original file after remuxing
            os.remove(source_path)
            print(f"Removed original file: {source_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"Subprocess error: {e}")
            log_error_to_file(__file__, f"Subprocess error: {e}")
        except UnicodeEncodeError as e:
            print(f"Encoding error: {e}")
            log_error_to_file(__file__, f"Encoding error: {e}")
        
    except Exception as e:
        error_message = f"Error remuxing {source_path}: {e}"
        print(error_message)
        log_error_to_file(__file__, error_message)

def walk_directory(directory):
    for subdir, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(subdir, file)
            if file_path.lower().endswith(('.mp3', '.flac', '.wav', '.aac', '.ogg')):  # Add more formats as needed
                audio_info = get_audio_info(file_path)
                if audio_info:
                    # print(f"File: {file_path}")
                    # print(f"Format: {audio_info['format']}")
                    # print(f"Bitrate: {audio_info['bitrate']}")
                    # print('-' * 50)
                    
                    # Update the summary
                    key = f"{audio_info['format']} - {audio_info['bitrate'] or 'Unknown Bitrate'}"
                    file_summary[key] += 1

                    # Remux if not 320kbps MP3
                    if audio_info['format'] != 'audio/mp3' or audio_info['bitrate'] != '320kbps':
                        destination_path = os.path.splitext(file_path)[0] + '.mp3'
                        remux_to_320kbps_mp3(file_path, destination_path, directory)

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
