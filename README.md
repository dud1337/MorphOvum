# Morph Ovum
==============

# TL;DR: QuitStart Guide
```
docker pull dud1337/morphovum
docker run -e TZ=Europe/Zurich -it -p 8138:8138 -p 8139:8139 \
  --mount type=bind,source="$(pwd)"/samples/ambience/,t arget=/fm/ambience \
  --mount type=bind,source="$(pwd)"/samples/music,target=/fm/music \
  --mount type=bind,source="$(pwd)"/samples/clips,target=/fm/clips \
  --mount type=bind,source="$(pwd)"/samples/playlists/,target=/fm/playlists/ \
  dud1337/morphovum
```

## Resources:
----------
* [VLC api](https://www.olivieraubert.net/vlc/python-ctypes/doc/)
* [decorator](https://github.com/micheles/decorator/blob/master/docs/documentation.md)

## Requirements:
-------------
Usually obtained in the docker instance. See `requirements.txt`
* `decorator`
* `flask_limiter`
* `flask_restful`
* `python-vlc`
* `pyyaml`
* `requests`

## To Do:
----------
0. Decide on a name for the software!
 1. Something descriptive and unique
 2. "web radio"

1. FOSS Example audio files
 1. ~3 songs (At least one of Matt's)
 2. 2 ambience (rain, fire) **[OK]**
 3. ~3 clips

2. Nicer layout of config.
 1. Ridiculous ASCII splash required

3. *config validation*
 1. MRL validation?
 2. Make interface validator stuff (open a port, see if it breaks?)

4. Unify comment style

5. Documentation

## Mini-Doc:
---------------
### Primary
* `src/config.yaml` - player instance config file
* `src/main.py` - main file to run
* `src/io_functions.py` - Handles user input
* `src/player_backend.py` - defines audio players classes, threads, and their functions
* `src/flask_resources.py` - generate Flask Resources from io functions

### Debug/testing
* `req_test.py` - For testing a few requests
* `test_flask.py` - For testing certain flask things

## Sample Media:
------------
1. Ambience:
 * [icmusic - Thunderstorm 1](https://freesound.org/people/icmusic/sounds/37564/)
 * [lurpsis - Life Fireplace](https://freesound.org/people/lurpsis/sounds/444127/)
2. Music:
 * ...
3. Clips:
 * ...
