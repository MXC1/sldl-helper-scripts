# You will need:
* [pip](https://pypi.org/project/pip/)
* [python](https://www.python.org/downloads/)
* Some technical knowledge

# Very brief steps to use:
1. Clone repository
2. Install dependencies with `pip install -r requirements.txt`
3. Download the ChromeDriver that matches your Chrome installation from https://developer.chrome.com/docs/chromedriver/downloads
4. Replace my list with your Spotify and SoundCloud playlist URLs in `/playlists.csv` (format below)
5. Run `/scripts/download_and_process_playlists.py`
6. ???
7. Profit

# Format of `/playlists.csv`:
* Spotify playlists require a URL and a name
* SoundCloud playlists just require a URL
* Both must be wrapped in "quotes"
```
"<spotify-playlist-url>", "<name-of-spotify-playlist>"
"<soundcloud-playlist-url"
...
```
e.g.
```
"https://open.spotify.com/playlist/0VBxbOqjsoNytf232VaQEp?si=ca0e2673bbc84231", "fun silly donk and hard dance"
"https://soundcloud.com/courtjester-uk/sets/donk-and-bits"
...
```

# The scripts do the following things:
* attempt to download the tracks from your list of playlists
* all files are only downloaded in 320kbps mp3 or better
* all files are remuxed to 320kbps mp3 for consistency and compatibility

* creates .m3u8 playlists with the same name as your Spotify/SoundCloud playlists

* failed downloads are stored in `/failed_downloads.csv`
* The `replace_failed_downloads.py` script will traverse through the list of failed downloads and open a file browser dialogue for you to import those missing files.
* Tracks will be removed from the failed_downloads list if they are successfully downloaded or if you successfully import them to your library using `replace_failed_downloads.py`
 
* errors are written to `/scripts/error_logs/YYYY-MM-DD_error_logs.txt`

# If you want to import your library directly into Rekordbox, then:
1. Install [MusicBee](https://www.getmusicbee.com/)
2. Point MusicBee to /tracks_and_playlists
3. In the MusicBee config, enable "Export library as iTunes XML file" or something similar
4. In Rekordbox settings, point the iTunes media library file to wherever MusicBee is saving your iTunes XML
5. Ta-da! Now Rekordbox recognises all your playlists with no extra effort to import.
6. Just make sure you open MusicBee after each run of `download_and_process_playlists.py` and press the Insert key so that it can refresh the library with any new tracks downloaded since the last run.

# Example structure of created files
(assuming one playlist called `playlist1` and one track called `Artist2 - Track3`:
```
/scripts
  /error_logs
    YYYY-MM-DD_error_logs.txt
  ...
/tracks_and_playlists
  /playlist1
    index.sldl
    playlist1.m3u8
  Artist2 - Track3.mp3
failed_downloads.csv
```

If you run into any issues or if anything I've written here is incorrect, please raise them as an issue on this repo with as much detail as possible.
