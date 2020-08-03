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
v0.9      █████████  20200802
```
## Table of Contents
* [About](#about)
* [TL;DR: Quickstart Guide](#tldr-quickstart-guide)
* [Admin Functionality](#admin-functionality)
* [Media Directories](#media-directories)
* [API Documentation](#api-documentation)
* [Other](#other)
    * [Sample Media Sources](#sample-media-sources)
    * [Key Module Documentation](#key-module-documentation)
    * [Python Requirements](#python-requirements)
    * [File Purposes](#file-purposes)
    * [Miscellaneous](#miscellaneous)


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
0. Create a `docker-compose.yaml` file similar to
```
version: '3'
services:
	morphovum:
    	image: dud1337/morphovum
	    stdin_open: true
	    tty: true
	    ports:
			- '8138:8138'
			- '8139:8139'
#    	volumes:
#      		- /path/to/your/music:/fm/music
#      		- /path/to/your/ambience:/fm/ambience
#      		- /path/to/your/clips:/fm/clips
#      		- /path/to/your/playlists:/fm/playlists
    	environment:
      		- MORPH_OVUM_PASSWORD=changeme
      		- TZ="Europe/Zurich"
```
1. To start your Morph Ovum server run
```
docker-compose up
```
2. To listen play `http://127.0.0.1:8138` in your preferred media player
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
5. To log in as admin with the default password
```
printf 'changeme' | sha256sum
057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86  -
curl http://127.0.0.1/admin
{"msg": "you are not admin", "data": false}
curl -c /tmp/morphovum_cookie_test -d "password_hash=057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86" http://127.0.0.1:8139/admin
{"msg": "ok!"}
curl -b /tmp/morphovum_cookie_test http://127.0.0.1:8139/admin
{"msg": "ok! you are admin", "data": true}
```
6. To immediately play a YouTube link (note URL encoding `?` -> `%3f`)
```
curl -b /tmp/cookie http://127.0.0.1:8139/music/wp/https://www.youtube.com/watch%3fv=rquygdjf0d8
{"msg": "ok! music playing https://www.youtube.com/watch?v=rquygdjf0d8"}
```


## Admin Functionality
**Docker docker-compose.yaml**
```
    environment:
      - MORPH_OVUM_PASSWORD=changeme
```
**Python config.yaml**
```yaml
# 1. Administration.
# admin_password: Sets password for admin commands
# 
admin_password: changeme
```

To create an admin session the user sends a POST request to /admin resource on the API is sent with the SHA256 
hash of the set password. See the [API Documentation](#api-documentation) and [Quickstart Guide](#tldr-quickstart-guide) for usage details.


## Media Directories
**Docker docker-compose.yaml**
```
    volumes:
      - /path/to/your/music:/fm/music
      - /path/to/your/ambience:/fm/ambience
      - /path/to/your/clips:/fm/clips
      - /path/to/your/playlists:/fm/playlists
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
| ambience | Stores your ambience collection (*e.g. rainfall, rivers, wind, etcetera*) |
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
| `/admin` | | Check if session has admin permissions |
| `/music/ls/<directory>` `/ambience/ls/<directory>`| admin | List the music files available in a subdirectory of the music or ambience directory |
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


## Other
### Sample Media Sources
1. Ambience
    * [icmusic - Thunderstorm 1](https://freesound.org/people/icmusic/sounds/37564/)
    * [lurpsis - Life Fireplace](https://freesound.org/people/lurpsis/sounds/444127/)
2. Music
	* "Book of Blade", "Chilli-Dog Dilemma", and "Scratchy Funk" by Krangu
	* If you you'd like some of your music to be considered for sample Morph Ovum tracks, please create an issue
3. Clips
    * Created by [Viewtiful Media](https://www.fiverr.com/viewtifulmedia)

### Key Module Documentation
* [VLC api](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [decorator](https://github.com/micheles/decorator/blob/master/docs/documentation.md)
* [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)

### Python Requirements
Obtained by docker container automatically. See `requirements.txt`.
```
decorator
flask_limiter
flask_restful
python-vlc
pyyaml
requests
```

### File Purposes
| File | Purpose |
| ------ | ------ |
| `src/config.yaml` | Player instance configuration file |
| `src/main.py` | File to run to start Morph Ovum |
| `src/io_functions.py` | Handles user input |
| `src/player_backend.py` | Defines audio players classes, threads, and their functions |
| `src/flask_resources.py` | Generate Flask Resources from io functions |
| `requirements.txt` | Required python modules to pip install |
| `Dockerfile` | Prepares morph ovum container |
| `test/req_test.py` | For testing a few requests |
| `test/test_flask.py` | For testing certain flask things |

### Miscellaneous
* The name was <del>pilfered from</del> inspired by [Heretic 2](https://heretic.fandom.com/wiki/Morph_Ovum_(Spell)).
