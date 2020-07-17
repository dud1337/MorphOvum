# Morph Ovum

Morph Ovum is your free community radio service.

* No sound card and no GUI required; debian-based VPS is enough
* HTTP streams your radio's audio
* Plays anything [VLC Media Player](https://www.videolan.org/vlc/) can play
* Provides an API for real time interaction; based on [Flash-RESTful](https://flask-restful.readthedocs.io/en/latest/index.html)
* 3 audio sources:
  * Music (*e.g. smooth jazz*)
  * Ambience (*e.g. distant thunderstorms*)
  * Clips: Approximately every n minutes, play an audio clip (*e.g. "you're listening to morph ovum!"*)


## TL;DR: QuickStart Guide
```
docker pull dud1337/morphovum
docker run -e TZ=Europe/Zurich -it -p 8138:8138 -p 8139:8139 \
  --mount type=bind,source="$(pwd)"/samples/ambience/,t arget=/fm/ambience \
  --mount type=bind,source="$(pwd)"/samples/music,target=/fm/music \
  --mount type=bind,source="$(pwd)"/samples/clips,target=/fm/clips \
  --mount type=bind,source="$(pwd)"/samples/playlists/,target=/fm/playlists/ \
  dud1337/morphovum
```

### Resources:
* [VLC api](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [decorator](https://github.com/micheles/decorator/blob/master/docs/documentation.md)

### Requirements:
Obtained by docker container automatically. See `requirements.txt`
* `decorator`
* `flask_limiter`
* `flask_restful`
* `python-vlc`
* `pyyaml`
* `requests`

## Mini-Doc:
### Primary
* `src/config.yaml` - player instance config file
* `src/main.py` - file to run to start Morph Ovum
* `src/io_functions.py` - Handles user input
* `src/player_backend.py` - defines audio players classes, threads, and their functions
* `src/flask_resources.py` - generate Flask Resources from io functions

### Debug/testing
* `req_test.py` - For testing a few requests
* `test_flask.py` - For testing certain flask things

## Sample Media:
1. Ambience:
  * [icmusic - Thunderstorm 1](https://freesound.org/people/icmusic/sounds/37564/)
  * [lurpsis - Life Fireplace](https://freesound.org/people/lurpsis/sounds/444127/)
2. Music:
  * ...
3. Clips:
  * ...
