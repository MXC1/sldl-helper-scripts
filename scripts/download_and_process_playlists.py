# Download and process Spotify and SoundCloud playlists using sldl and other scripts.
# This is the 'master' script that calls other scripts to download and process playlists.

import os
import subprocess
from log_error_to_file import log_error_to_file
from convert_soundcloud_to_csv import convert_soundcloud_to_csv
from rename_playlists import rename_playlists
from remux_to_mp3_320 import remux_to_mp3_320

# List of Spotify playlists with their comments
spotify_playlists = [
    ("https://open.spotify.com/playlist/37QpaaUJL8vmNYj9ZBVyrg?si=c28f71da2b8c4abb", "MILO X OLLIE BDAY"),
    ("https://open.spotify.com/playlist/0VBxbOqjsoNytf232VaQEp?si=ca0e2673bbc84231", "fun silly donk and hard dance"),
    ("https://open.spotify.com/playlist/6eUtriAMWlmkjJK6I9ctga?si=90b213fc4922442c", "harder hard dance"),
    ("https://open.spotify.com/playlist/43VZ1EitjjLslv2oilhrt4?si=cf7c418b0e214972", "tek,speedbass,frenchcore"),
    ("https://open.spotify.com/playlist/1uXZ89ktDNsNc7At2iQbNR?si=efeb97175b6d443c", "hardcore.terrorcore.uptempo.crossbreed etc"),
    ("https://open.spotify.com/playlist/1xb2DyaDPm30OH8LTBRAfA?si=a0a94f60facd4ba8", "mutant bass"),
    ("https://open.spotify.com/playlist/1SLT6Rjxu7RR1VV8TyjXB9?si=e51cdde58ab64bca", "heavy tha"),
    ("https://open.spotify.com/playlist/183644Z4uc71GGvzyrmD7s?si=7b10eab2b8f945e5", "GUT PUNCH "),
    ("https://open.spotify.com/playlist/0cMUEsaouKDmIQfsbeuvoO?si=968d9a95a992457d", "loads of lovely liquid"),
    ("https://open.spotify.com/playlist/27x4FTzCJpwpeG5ZLQvHUW?si=933d359cc4694006", "heavy and dark dnb and neurofunk"),
    ("https://open.spotify.com/playlist/08ljGPqUA8tY43Dk3tD9aI?si=47876b6b198847ac", "lyrical, cheeky and junglish dnb"),
    ("https://open.spotify.com/playlist/2Rrcb5YMLG1k0SF95ywlPB?si=e9b7f82894794a85", "weird and steppy dnb"),
    ("https://open.spotify.com/playlist/4taKi46iMkjnN2RQyPa0Ok?si=1b412940067f458e", "minimal and darker dnb"),
    ("https://open.spotify.com/playlist/6jeyPiLM9Zncg63cbxsOwU?si=3a6fbdf2573b4202", "energetic and brighter dnb"),
    ("https://open.spotify.com/playlist/4CJFVpTZF4cZX0FT5P890k?si=3dcce98f020b48b6", "breaks and jungle"),
    ("https://open.spotify.com/playlist/51uBcZqOos8kcKRxWjuhLf?si=c446efc42abb4bd4", "groovy ridms"),
    ("https://open.spotify.com/playlist/6ErKxDeJ34V2LWZMe1Qlw9?si=74c2f4b4556b4c02", "Hip hop"),
    ("https://open.spotify.com/playlist/5gWTqII5w7OMadVH6Sq6gN?si=01b182b6e7374255", "Lounge boogie"),
    ("https://open.spotify.com/playlist/2KhRJU0xTIi7rWDvM1Ufgr?si=a45ca3d1c0f54b7d", "Lounge beats deep jazzy house"),
    ("https://open.spotify.com/playlist/4ovPvc9rDKk7GNnhxp6fzz?si=b3ab3678caf34a4d", "downtempo and trip hop"),
    ("https://open.spotify.com/playlist/50vepog2aaeNNOR5TBuADf?si=8165dddd79494a46", "pyjama techno"),
    ("https://open.spotify.com/playlist/7ER4s8OP5e9KUmLrzZh2AC?si=731e1021e89c44a8", "techno mate"),
    ("https://open.spotify.com/playlist/0bztHhAs83hrsZcP09o1ML?si=72389aa31f3c4a96", "party dance"),
    ("https://open.spotify.com/playlist/2Q7SuTa5zMKMDZzsipSPte?si=415942eabf1b4977", "NAUGHTY club bangers"),
    ("https://open.spotify.com/playlist/1gFinFMmtG0hjOWtb92xjn?si=2e238477e884436e", "dance (2020)"),
    ("https://open.spotify.com/playlist/3PTCbxOVhaVx37drmaeRiw?si=2e40d5b15cad49f8", "GOOD POP"),
    ("https://open.spotify.com/playlist/532g5BkLOwDxKmtbkWRcVf?si=1460fe81df5640c2", "Big beats are the best"),
    ("https://open.spotify.com/playlist/57Jq0XfkwXctFDGiV8xiNV?si=4fe3d8fcf5794cb7", "Rave"),
    ("https://open.spotify.com/playlist/37NAc1kCO8fkxiEGK49NHg?si=94fe49eec62d4c1f", "illuminaughty"),
    ("https://open.spotify.com/playlist/5yoao1NrfUo7HHqL1kJnEv?si=33a5d245ba254271", "middle eastern/tribal/percussion"),
    ("https://open.spotify.com/playlist/2OA8jQQjJ52pGwIk81Ouo0?si=2d70429eb9d44c5e", "garage and rnb and similar"),
    ("https://open.spotify.com/playlist/5u7vdlYbxtimytzMCo584h?si=39824cbd68e24138", "bassline, ghettotech, speed garage"),
    ("https://open.spotify.com/playlist/1m5tSMGiRF3NTIPUUrxQju?si=9b9ef36272bc49e0", "verify me (high energy 140)"),
    ("https://open.spotify.com/playlist/3nUoTOTfTremXqwP4qxQES?si=076e1c8eee5e4e92", "dubstep (2020)"),
    ("https://open.spotify.com/playlist/37moZqbjJvpLLZbUYp5asF?si=23973f6a957d44c5", "roll with the punches (low energy 140)"),
    ("https://open.spotify.com/playlist/7pV3HtW1VQBX7KhabcGveQ?si=bb7e9fbb61ac406f", "soundboy"),
    ("https://open.spotify.com/playlist/5yQGGROruLewBDaRLJ1MQg?si=005f816207184d1d", "modern dub  (2022)"),
    ("https://open.spotify.com/playlist/0cSOvEy00Jh68cVaB5Dzl5?si=0bb51aedacd24c8b", "reggae and rootsy dub (2022)"),
    ("https://open.spotify.com/playlist/78WPQqYzu9Py7fzGqk4MDJ?si=8913938f10184014", "fuzzy dungeon punch step"),
    ("https://open.spotify.com/playlist/2V2PsievnZxp9TBz9CDWzS?si=769d31c73e4b42fd", "IDM.Future Garage.Electronica"),
    ("https://open.spotify.com/playlist/5OZ6nyi8BRClYCpCt13a5j?si=99fb79e14cbb4ebd", "bluebells"),
    ("https://open.spotify.com/playlist/4eCSrhbfAjNF3AsIsegSRA?si=05e095b209684068", "bigger pop playlist")
    ("https://open.spotify.com/playlist/70sombx8BFNEKSwyFEpYbq?si=m5c8Ty8LSvuFE9UN8wExMg", "Chill dance.trance.oldskool rave")
]

# List of SoundCloud playlist URLs
soundcloud_playlists = [
    "https://soundcloud.com/courtjester-uk/sets/dnb-and-similar-moodiness",
    "https://soundcloud.com/courtjester-uk/sets/donk-and-bits",
    "https://soundcloud.com/courtjester-uk/sets/mutant-bass",
    "https://soundcloud.com/courtjester-uk/sets/tek-etc-not-on-spotify"
]

try:
    # Download all Spotify playlists
    for url, comment in spotify_playlists:
        print(f"Downloading Spotify playlist: {comment}")
        subprocess.run(["sldl", url], check=True)

    # Process all SoundCloud playlists
    soundcloud_csv_paths = []
    for sc_url in soundcloud_playlists:
        print(f"Processing SoundCloud playlist: {sc_url}")
        convert_soundcloud_to_csv(sc_url)

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
