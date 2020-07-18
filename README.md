```
            █████            
         ███     ███         
       ███         ███       
     ███             ███     
   ███                 ███   
  ██   ┌┬┐┌─┐┬─┐┌─┐┬ ┬   ██  
██     ││││ │├┬┘├─┘├─┤     ██
██     ┴ ┴└─┘┴└─┴  ┴ ┴     ██
███      _      ._ _      ███
  ███   (_)\/|_|| | |   ███  
    ███               ███    
       ███         ███       
v0.1      █████████  20200718
```
## Table of Contents
* [About](#about)
* [TL;DR: Quickstart Guide](#tldr-quickstart-guide)
* [Media Directories](#media-directories)
* [API Documentation](#api-documentation)
* [Reference](#reference)


## About
Morph Ovum is your free and open source community radio service.

* No sound card and no GUI required
* 3 audio sources (*all optional*):
  * Music (*e.g. smooth jazz*)
  * Ambience (*e.g. distant thunderstorms*)
  * Clips: Approximately every n minutes, play an audio clip (*e.g. "you're listening to morph ovum!"*)
* Provides a [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)-based API for real-time control
* HTTP streams your radio's audio
* Plays anything [VLC Media Player](https://www.videolan.org/vlc/) can play:
  * Your personal library
  * An [airsonic](https://github.com/airsonic/airsonic) playlist
  * An internet radio station
  * A YouTube playlist
  * ...


## TL;DR: Quickstart Guide
1. To start your Morph Ovum server, run
```
docker pull dud1337/morphovum
docker run -e TZ=Europe/Zurich -it -p 8138:8138 -p 8139:8139 \
  --mount type=bind,source="$(pwd)"/samples/music,target=/fm/music \
  --mount type=bind,source="$(pwd)"/samples/ambience/,target=/fm/ambience \
  --mount type=bind,source="$(pwd)"/samples/clips,target=/fm/clips \
  --mount type=bind,source="$(pwd)"/samples/playlists/,target=/fm/playlists/ \
  dud1337/morphovum
```
2. To listen, play `http://127.0.0.1:8138` in your preferred media player
```
mpv http://127.0.0.1:8138
```
3. To check the current music track
```
curl http://127.0.0.1:8139/music/current/track
{"msg": "ok!", "data": "Krangu - Scratchy Funk"}
```
4. To check the current ambience playlist
```
curl http://127.0.0.1:8139/ambience/current/playlist
{"msg": "ok!", "data": ["ambience/icmusic__thunderstorm_short.mp3", "ambience/lurpsis__lit_fireplace.mp3"]}
```

## Media Directories
**Docker**
```
  --mount type=bind,source=/path/to/your/music,target=/fm/music \ 
  --mount type=bind,source=/path/to/your/ambience,target=/fm/ambience \
  --mount type=bind,source=/path/to/your/clips,target=/fm/clips \
  --mount type=bind,source=/path/to/your/playlists,target=/fm/playlists/
```
**Python config.yaml**
```
audio_dirs:
  music     : /path/to/your/music
  ambience  : /path/to/your/ambience
  clips     : /path/to/your/clips
playlist_dir: /path/to/your/playlists
```

| Directory | Purpose |
| ------ | ------ |
| music | Stores your music collection |
| ambience | Stores your ambience collection |
| clips | Stores your clips |
| playlists | Stores your playlists usually consisting of files in `music` directory or network resources |


## API Documentation
The API listens by default on http://127.0.0.1:8139 if ran via the above docker commands.

**POST requests**

| Resource | Data | Function |
| ------ | ------ | ------|
| `/admin` | `password_hash` | Sent a SHA256 hash of the admin password to obtain an admin session |

**GET requests**

| Resource | Flags | Function |
| ------ | ------ | ------ |
| `/admin` | | Check if session has admin credentials |
| `/music/ls/<directory>` `/ambience/ls/<directory>`| | List the music files available in a subdirectory of the music or ambience directory |
| `/music/lsp/<file or directory>` `/ambience/lsp/<file or directory>` |  admin busy patience | Play music file or contents of a subdirectory of the ambience directory |
| `/music/lsc/<file or directory>` `/ambience/lsc/<file or directory>` | admin busy patience | Enqueue the file or contents of a subdirectory of the music or ambience directory |
| `/music/wp/<web resource>` `/ambience/wp/<web resource>` | admin busy patience | Play the web resource (*e.g. YouTube URL*) |
| `/music/current/track` `/ambience/current/track` | | Get the currently playing music or ambience track |
| `/music/current/playlist` `/ambience/current/playlist` | | Get the current music or ambience playlist |
| `/music/skip` `/ambience/skip` | admin busy patience | Goes to the next queued music or ambience track |
| `/music/toggle` `/ambience/toggle` | admin patience | Toggle playback of the music or ambience player |
| `/music/history` `/ambience/toggle` | | Return the last played music or ambience files (up to 100) |
| `/music/playlists` | | Show playlists available | 
| `/music/playlist/<playlist index or filename>` | admin patience | Plays an available playlist |
| `/clips/toggle` | admin | Toggle the playing of clips |
| `/clips/now` | admin patience | Schedule a clip to play immediately |

**Flags**

| Flag | Description |
| ------ | ------ |
| `admin` | Requires an admin cookie to be set |
| `patience` | Command is disallowed from being used too frequently (3 second rate limit) |
| `busy` | Makes the API busy until the task is complete |


## Reference
* **Sample Media Sources**
    1. Ambience
        * [icmusic - Thunderstorm 1](https://freesound.org/people/icmusic/sounds/37564/)
        * [lurpsis - Life Fireplace](https://freesound.org/people/lurpsis/sounds/444127/)
    2. Music
        * ...
    3. Clips
        * ...
* **Key Module Documentation**
    * [VLC api](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
    * [decorator](https://github.com/micheles/decorator/blob/master/docs/documentation.md)
    * [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)
* **Python Requirements** (*Obtained by docker container automatically. See `requirements.txt`*)
    * `decorator`
    * `flask_limiter`
    * `flask_restful`
    * `python-vlc`
    * `pyyaml`
    * `requests`
* **Files**
    * `src/config.yaml` - player instance configuration file
    * `src/main.py` - file to run to start Morph Ovum
    * `src/io_functions.py` - Handles user input
    * `src/player_backend.py` - defines audio players classes, threads, and their functions
    * `src/flask_resources.py` - generate Flask Resources from io functions
    * `requirements.txt` - required python modules to pip install
    * `Dockerfile` - prepares morph ovum container
    * `test/req_test.py` - For testing a few requests
    * `test/test_flask.py` - For testing certain flask things
* **Miscellaneous**
    * The name was <del>pilfered</del> inspired by [Heretic 2](https://heretic.fandom.com/wiki/Morph_Ovum_(Spell)).
