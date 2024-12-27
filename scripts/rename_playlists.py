# Renames the _playlist.m3u8 files to the name of the parent directory.
# This is necessary because slsk-batchdl names all playlist files as _playlist.m3u8, which prevents automatic import into Rekordbox.

import os
import logging
import sys
from log_error_to_file import log_error_to_file

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process_m3u8_files(directory):
    try:
        # Walk through the directory recursively
        for root, dirs, files in os.walk(directory):
            # Filter the .m3u8 files in the current directory
            m3u8_files = [f for f in files if f.endswith('.m3u8')]

            # If there is a _playlist.m3u8 file
            if '_playlist.m3u8' in m3u8_files:
                # Remove other .m3u8 files in the current directory (except _playlist.m3u8)
                for f in m3u8_files:
                    if f != '_playlist.m3u8':
                        file_path = os.path.join(root, f)
                        os.remove(file_path)
                        logging.info(f"Deleted: {file_path}")

                # Rename _playlist.m3u8 to the name of the parent directory
                parent_dir = os.path.basename(root)
                new_name = os.path.join(root, f"{parent_dir}.m3u8")
                old_name = os.path.join(root, '_playlist.m3u8')
                os.rename(old_name, new_name)
                logging.info(f"Renamed: {old_name} -> {new_name}")
    
    except Exception as e:
        error_message = f"Exception occurred: {str(e)}"
        log_error_to_file(__file__, error_message)
        
def rename_playlists(top_level_directory):
    if os.path.isdir(top_level_directory):
        try:
            process_m3u8_files(top_level_directory)
        except Exception as e:
            error_message = f"Unhandled error during execution: {e}"
            logging.error(error_message)
            log_error_to_file(__file__, error_message)
    else:
        error_message = f"The provided path is not a valid directory: {top_level_directory}"
        logging.error(error_message)
        log_error_to_file(__file__, error_message)

# Provide this as an option for testing
if __name__ == "__main__":
    # Check if the directory is passed as an argument
    if len(sys.argv) > 1:
        top_level_directory = sys.argv[1]
    else:
        # Prompt the user for the directory
        top_level_directory = input("Please enter the top-level directory: ").strip()
        
    rename_playlists(top_level_directory)
