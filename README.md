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
          █████████          
```

Morph Ovum is your free and open source community radio service.

* No sound card and no GUI required; a debian-based VPS is enough
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
  --mount type=bind,source="$(pwd)"/samples/ambience/,target=/fm/ambience \
  --mount type=bind,source="$(pwd)"/samples/music,target=/fm/music \
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

## API Reference
| Resource | Flags | Function |
| ------ | ------ | ------ |
| `/music/ls/<directory>` | | List the music files available in a subdirectory of the music directory |
| `/music/lsp/<file or directory>` | admin busy patience | Play the music file or contents of a subdirectory of the music directory |
| `/music/lsc/<file or directory>` | admin busy patience | Enqueue the music file or contents of a subdirectory of the music directory |
| `/music/wp/<web resource>` | admin busy patience | Play the web resource (*e.g. YouTube URL*) |
| `/music/current/track` | | Get the currently playing music track |
| `/music/current/playlist` | | Get the current music playlist |
| `/music/skip` | admin busy patience | Goes to the next queued music track |
| `/music/toggle` | admin patience | Toggle playback of the music player |
| `/music/history` | | Return the last played music (up to 100) |
| `/music/playlists` | | Show playlists available | 
| `/music/playlist/<playlist index or filename>` | admin patience | Plays an available playlist |
| `/ambience/ls/<directory>` | | List the ambience files available in a subdirectory of the ambience directory |
| `/ambience/lsp/<file or directory>` | admin busy patience | Play the ambience file or contents of a subdirectory of the ambience directory |
| `/ambience/lsc/<file or directory>` | admin busy patience | Enqueue the ambience file or contents of a subdirectory of the ambience directory |
| `/ambience/wp/<web resource>` | admin busy patience | Play the web resource (*e.g. YouTube URL*) |
| `/ambience/current/track` | | Get the currently playing ambience track |
| `/ambience/current/playlist` | | Get the current ambience playlist |
| `/ambience/skip` | admin busy patience | Goes to the next queued ambience track |
| `/ambience/toggle` | admin patience | Toggle playback of the ambience player |
| `/ambience/history` | | Return the last played ambience (up to 100) |
| `/clips/toggle` | admin | Toggle the playing of clips |
| `/clips/now` | admin patience | Schedule a clip to play immediately |


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
    * `src/config.yaml` - player instance config file
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
