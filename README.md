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
v1.2.3   █████████  20260209
```

https://github.com/dud1337/MorphOvum/assets/5631021/1dd0269d-1658-47c0-bee9-66c4977dfbdc

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
Morph Ovum is a free and open source community radio service.

* HTTP streams your radio's audio
* No sound card and no desktop environment required
* 3 audio sources (*all optional*):
  * Music (*e.g. smooth jazz*)
  * Ambience (*e.g. distant thunderstorms*)
  * Clips: Approximately every n minutes, play an audio clip (*e.g. "you're listening to morph ovum!"*)
* Provides a [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)-based API for real-time control
* Provides a websocket for frontends to avoid polling
* Plays anything [VLC Media Player](https://www.videolan.org/vlc/) can play:
  * Your personal library
  * An [airsonic](https://github.com/airsonic/airsonic) playlist
  * An internet radio station
  * YouTube videos (Sometimes there's an arms race and VLC can't)
  * ...


## TL;DR: Quickstart Guide
0. Create a `docker-compose.yaml` file similar to
```yaml
version: '3'
services:
    morphovum:
        image: dud1337/morphovum
        stdin_open: true
        tty: true
        ports:
            - '8080:8080'
#       volumes:
#           - /path/to/your/music:/fm/music
#           - /path/to/your/ambience:/fm/ambience
#           - /path/to/your/clips:/fm/clips
#           - /path/to/your/playlists:/fm/playlists
#           - /path/to/your/config_dir:/fm/conf
        environment:
        	- MORPH_OVUM_PASSWORD=changeme	# not used if config_dir is given
        	- TZ="Europe/Zurich"
```
1. To start your Morph Ovum server run
```
docker-compose up
```
2. To listen play `http://127.0.0.1:8080` in your preferred media player or browser
```
mpv http://127.0.0.1:8080
```
3. To check the current music track
```
curl http://127.0.0.1:8080/api/music/current/track
{"msg": "ok!", "data": "Krangu - Scratchy Funk"}
```
4. To check the current ambience playlist
```
curl http://127.0.0.1:8080/api/ambience/current/playlist
{"msg": "ok!", "data": ["ambience/icmusic__thunderstorm_short.mp3", "ambience/lurpsis__lit_fireplace.mp3"]}
```
5. To log in as admin with the default password
```
printf 'changeme' | sha256sum
057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86  -
curl http://127.0.0.1:8080/admin
{"msg": "you are not admin", "data": false}
curl -c /tmp/morphovum_cookie_test -d "password_hash=057ba03d6c44104863dc7361fe4578965d1887360f90a0895882e58a6248fc86" http://127.0.0.1:8080/api/admin
{"msg": "ok!"}
curl -b /tmp/morphovum_cookie_test http://127.0.0.1:8080/api/admin
{"msg": "ok! you are admin", "data": true}
```
6. To immediately play a YouTube link
```
curl -b /tmp/cookie http://127.0.0.1:8080/api/music/wp/ -d "url=https://www.youtube.com/watch%3fv=rquygdjf0d8"
{"msg": "ok! music playing https://www.youtube.com/watch?v=rquygdjf0d8"}
```

**Note:** All services are now consolidated behind nginx on port 8080. See [NGINX_ARCHITECTURE.md](NGINX_ARCHITECTURE.md) for details.


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
The API listens by default on http://127.0.0.1:8080/api if ran via the above docker commands (nginx routes `/api/*` requests to the internal Flask server on port 8139).

**POST requests**

| Resource | Argument | Flags | Function |
| ------ | ------ | ------ | ------ |
| `admin` | `password_hash` | | Sent a SHA256 hash of the admin password to obtain an admin session |
| `ambience/ls` | `directory` | `admin` | List the contents of a subdirectory in the ambience directory |
| `ambience/lsa` | `directory_or_file` | `admin` `busy` `patience` | Add and shuffle a file or the contents of a subdirectory in the ambience directory |
| `ambience/lsc` | `directory_or_file` | `admin` `busy` `patience` | Enqueue a file or the contents of a subdirectory in the music directory |
| `ambience/lsp` | `directory_or_file` | `admin` `busy` `patience` | Play a file or the contents of a subdirectory in the ambience directory |
| `ambience/wc` | `url` | `admin` `busy` `patience` | Enqueue the web resource in the ambience player |
| `ambience/wp` | `url` | `admin` `busy` `patience` | Play the web resource in the ambience player |
| `music/ls` | `directory` | `admin` | List the contents of a subdirectory in the music directory |
| `music/lsa` | `directory_or_file` | `admin` `busy` `patience` | Add and shuffle a file or the contents of a subdirectory in the music directory |
| `music/lsc` | `directory_or_file` | `admin` `busy` `patience` | Enqueue a file or the contents of a subdirectory in the music directory |
| `music/lsp` | `directory_or_file` | `admin` `busy` `patience` | Play a file or the contents of a subdirectory in the music directory |
| `music/wc` | `url` | `admin` `busy` `patience` | Enqueue the web resource in the music player |
| `music/wp` | `url` | `admin` `busy` `patience` | Play the web resource in the music player |
| `playlist/delete` | `playlist` | `admin` `patience` | Deletes a playlist from available playlists. An int n input will play the nth playlist |
| `playlist/lsp` | `playlist` | `admin` `patience` | Plays a playlist from available playlists. An int n input will play the nth playlist |
| `playlist/save` | `playlist` | `admin` `patience` | Save the current music playlist to the playlist's dir as an m3u |

**GET requests**

| Resource | Flags | Function |
| ------ | ------ | ------ |
| `ambience/currentplaylist` | | Return the currently playing ambience playlist |
| `ambience/currenttrack` | | Return the currently playing ambience track |
| `ambience/history` | | Returns up to 100 of the last played tracks for a player |
| `ambience/repeat` | `admin` `patience` | Toggle the repeat_mode of the music player |
| `ambience/skip` | `admin` `busy` `patience` | Skip the current ambience track |
| `ambience/toggle` | `admin` `patience` | Toggle the playing of the ambience player |
| `clips/now` | `admin` `patience` | Schedule a clip to be played now |
| `clips/toggle` | `admin` | Toggle the playing of clips |
| `help` | | Return the available commands and their arguments, if any |
| `music/currentplaylist` | | Return the currently playing music playlist |
| `music/currenttrack` | | Return the currently playing music track |
| `music/history` | | Returns the last music tracks played (max 100) |
| `music/repeat` | `admin` `patience` | Toggle the repeat_mode of the music player |
| `music/skip` | `admin` `busy` `patience` | Skip the currently playing music track |
| `music/toggle` | `admin` `patience` | Toggle the playing of the music player |
| `playlist/ls` | | Lists available playlists |

**Flags**

| Flag | Description |
| ------ | ------ |
| `admin` | Requires an admin cookie to be set |
| `patience` | Command is disallowed from being used too frequently (3 second rate limit) |
| `busy` | Makes the API busy until the task is complete |


## Other
### Local Development / Testing
For local development or testing without Docker:
```bash
# Install dependencies
pip install -r requirements.txt

# Run with sample media (included in repo)
cd src
python main.py -c ../dev-config.yaml
```
Then navigate to http://127.0.0.1:8139

**Note:** When running locally without Docker, the services run on their internal ports (8138 for stream, 8139 for UI/API, 8140 for websockets). The single-port nginx setup only applies to the Docker container.

### Sample Media Sources
1. Ambience
    * [icmusic - Thunderstorm 1](https://freesound.org/people/icmusic/sounds/37564/)
    * [lurpsis - Life Fireplace](https://freesound.org/people/lurpsis/sounds/444127/)
2. Music
	* "Book of Blade", "It's Chilli Dog Time!", and "Scratchy Funk" by [Krangu](https://krangu.bandcamp.com/releases)
	* If you'd like some of your music to be considered for sample Morph Ovum tracks, please create an issue
3. Clips
    * Created by [Viewtiful Media](https://www.fiverr.com/viewtifulmedia)

### Key Module Documentation
* [VLC api](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [decorator](https://github.com/micheles/decorator/blob/master/docs/documentation.md)
* [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)

### Python Requirements
Obtained by docker container automatically. See `requirements.txt`.
```
asyncio
decorator
flask_limiter
flask_restful
python-vlc
pyyaml
requests
websockets
```

### File Purposes
| File | Purpose |
| ------ | ------ |
| `Dockerfile` | Prepares morph ovum container with nginx and supervisor |
| `docker-compose.yaml` | Morph Ovum container instance configuration |
| `requirements.txt` | Required python modules to pip install |
| `/src/confs/nginx.conf` | Nginx reverse proxy configuration (consolidates 3 ports to 1) |
| `/src/confs/supervisord.conf` | Supervisor configuration to manage nginx, pulseaudio, and morphovum |
| `src/default-config.yaml` | Default player instance configuration file |
| `src/main.py` | File to run to start Morph Ovum |
| `src/io_functions.py` | Handles user input |
| `src/player_backend.py` | Defines audio players classes, threads, and their functions |
| `src/flask_resources.py` | Generate Flask Resources from io functions |
| `src/www/index.html` | Web UI main file |
| `src/www/main.js` | Web UI JavaScript |
| `src/www/main.css` | Web UI CSS |
| `src/www/api_data.json` | API metadata |
| `res/morph_ovum.ascii` | Morph Ovum ASCII art |
| `res/MorphOvum.gif` | Freeware Morph Ovum gif |
| `res/morph_ovum.vhosts` | Sample apache2 config |
| `scripts/doc_generation.py` | Print README.md documentation and create `api_data.json` |

### Miscellaneous
* The name was <del>pilfered from</del> inspired by [Heretic 2](https://heretic.fandom.com/wiki/Morph_Ovum_(Spell)).
