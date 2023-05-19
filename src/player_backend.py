######################################################################
#
#   AudioPlayers Functions
#   
#   1. Defines config.yaml loader & validation functions
#   2. Define functions for VLC library classes
#   3. Define nofication websockets server class
#   4. Define AudioPlayers class
#       4 VLC Instances
#           1 Streams the pulse audio virtual sink
#           3 Audio players that play to the virtual sink
#               1. Music
#               2. Ambience
#               3. Clips
#       1 ClipsThread
#   5. Define ClipsThread Thread
#       Manages clip playing times
#       
######################################################################
from __future__ import print_function
import vlc
#   "media list player is a layer of inconvenience that you're better off not using"
#               - anon, #VideoLAN:matrix.org #videolan at freenode or irc.videolan.org
import os
import re
import sys
import yaml
import datetime
import socket
import asyncio
import websockets
from threading import Thread
from time import sleep
from random import choice, normalvariate, shuffle

os.environ['PULSE_SINK'] = 'virtual'
Debug = True

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


######################################################################
#
#   1. Defines config.yaml loader & validation functions
#
######################################################################
def load_config(config_file='default-config.yaml'):
    '''loads config.yaml file
    checks and reports potential errors'''
    def check_missing(key, validator_conf, test_conf): 
        '''Checks for missing config keys'''
        if key not in test_conf:
            tmp_type = type(dict()) if 'default' not in validator_conf[key] else type(validator_conf[key]['default'])
            eprint('Error: Missing key ' + key + '. Requires ' + str(tmp_type))
            if 'validator' not in validator_conf[key]:
                for subkey in validator_conf[key]:
                    eprint('\tMissing subkey ' + subkey + ' => ' + key + '. Requires ' + str(type(validator_conf[key][subkey]['default'])))
            return True
        return False
    
    def check_type(key, validator_conf, test_conf):
        '''Checks for correct types'''
        if 'validator' in validator_conf[key]:
            tmp_type = type(validator_conf[key]['default'])
        else:
            tmp_type = type(validator_conf[key])

        if not tmp_type == type(test_conf[key]):
            eprint('Error: Bad type ' + key + '. Requires ' + str(type(validator_conf[key]['default'])) + ' not ' + str(type(test_conf[key])))
            if 'validator' not in validator_conf[key]:
                for subkey in validator_conf[key]:
                    eprint('Error: Missing subkey ' + subkey + ' => ' + key + '. Requires ' + str(type(validator_conf[key][subkey]['default'])))
            return True
        return False

    def check_password(password):
        '''Check password is long enough'''
        if len(password) < 8:
            eprint('Error: admin_password is required to be 8 more characters. Got ' + str(len(password)))
            return True
        return False

    def check_interface(interface):
        '''Check if interface is viable'''
        try:
            socket.inet_aton(interface)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
                test_socket.bind((interface, 0))
                return False
        except:
            eprint(f'Error: interface {interface} not useable')
            return True

    def check_port(port):
        '''Check port is in correct range and can be opened'''
        if port not in range(1, 2**16):
            eprint('Error: port ' + str(port) + ' not in range 1-65535')
            return True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', port))
            s.listen(1)
            s.close()
        except socket.error as serr:
            eprint('Error: could not open TCP port ' + str(port) + ' because ' + str(serr))
            return True
        return False

    def check_directory(directory):
        if not os.path.isdir(directory):
            eprint('Error: \'' + directory + '\' is not a directory')
            return True
        return False

    def check_mrl(mrl):
        return False

    def check_clip_mean(mean_minutes):
        if mean_minutes < 1:
           eprint('Error: clip_mean must be > 0. Got ' + str(mean_minutes))
           return True
        return False

    def check_clip_std_deviation(std_deviation_minutes):
        if std_deviation_minutes < 0:
            eprint('Error: clip_std_deviation must be >= 0. Got ' + str(std_deviation_minutes))
            return True
        return False

    validator_conf = {
        'admin_password':{
            'default'   :'hunter2',
            'validator' :check_password
        },
        'interface':{
            'default'   :'0.0.0.0',
            'validator' :check_interface
        },
        'stream_port':{
            'default'   :8138,
            'validator' :check_port
        },
        'io_port':{
            'default'   :8139,
            'validator' :check_port
        },
        'startup_players':
        {
            'music':{
                'default'   :True,
                'validator' :None
            },
            'ambience':{
                'default'   :True,
                'validator' :None
            },
            'clips':{
                'default'   :True,
                'validator' :None
            }
        },
        'audio_dirs':
        {
            'music':{
                'default'   :'/srv/music',
                'validator' :check_directory
            },
            'ambience':{
                'default'   :'/srv/ambience',
                'validator' :check_directory
            },
            'clips':{
                'default'   :'/srv/clips',
                'validator' :check_directory
            }
        },
        'playlist_dir':{
            'default'   :'samples/srv/playlists',
            'validator' :check_directory
        },
        'default_files':
        {
            'music':{
                'default'   :'/srv/music',
                'validator' :check_mrl
            },
            'ambience':{
                'default'   :'/srv/ambiece',
                'validator' :check_mrl
            }
        },
        'clip_timing':
        {
            'clip_mean':{
                'default'   :90,
                'validator' :check_clip_mean
            },
            'clip_std_deviation':{
                'default'   :15,
                'validator' :check_clip_std_deviation
            }
        }
    }

    with open(config_file) as conf:
        try:
            instance_conf = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print('Bad Config: ' + str(exc))
            sys.exit(1)

    def validate(key, validator_conf, test_conf):
        '''Validate a specific key'''
        if check_missing(key, validator_conf, test_conf):
            return True
        if check_type(key, validator_conf, test_conf):
            return True

        if 'validator' in validator_conf[key] and validator_conf[key]['validator']:
            return validator_conf[key]['validator'](test_conf[key])
        return False
   
    def validate_conf(validator_conf, instance_conf, parent_keys=[]):
        '''Validate enire config'''
        error = False
        for key in validator_conf:
            tmp_error = validate(key, validator_conf, instance_conf)
            error |= tmp_error
            if tmp_error:
                eprint('\tFor key: ' +  ' => '.join(parent_keys + [key]))
            if 'validator' not in validator_conf[key] and not tmp_error:
                parent_keys.append(key)
                error |= validate_conf(validator_conf[key], instance_conf[key], parent_keys=parent_keys)
        return error

    error = validate_conf(validator_conf, instance_conf)

    # hacky port checkin'
    if 'stream_port' in instance_conf and 'io_port' in instance_conf: 
        if instance_conf['stream_port'] == instance_conf['io_port']:
            eprint('Error: stream_port and io_port are both ' + str(instance_conf['stream_port']))
            error |= error

    if error:
        eprint('Bad Config: See above errors')
        sys.exit(1)
    else:
        return instance_conf


######################################################################
#
#   2. Define functions for VLC library classes
#
######################################################################
def fade_volume_players(players, new_vs, time=2):
    '''fades volume of a list of vlc.MediaPlayer instances
    sample input: [vlc.MediaPlayer(), vlc.MediaPlayer()], [50, 25], time = 3]
    Changes player one to 50% volume and player two to 25% over 3 seconds'''
    old_vs = [mp.audio_get_volume() for mp in players]

    for j in range(int(20 * time)):
        for i in range(len(players)):
            if new_vs[i] == old_vs[i]:
                pass
            elif new_vs[i] > old_vs[i]:
                players[i].audio_set_volume(int(
                    old_vs[i] + (new_vs[i] - old_vs[i])*(j/float(time*20 - 1))
                ))
            else:
                players[i].audio_set_volume(int(
                    old_vs[i] - (old_vs[i] - new_vs[i])*(j/float(time*20 - 1))
                ))
        sleep(0.05)

def media_get_song(media):
    '''returns as nice a string as possible for the current media'''
    def short_mrl(mrl_string):
        if re.search('^file://', mrl_string):
            return '/'.join(mrl_string.split('/')[-2::])
        else:
            return mrl_string

    meta_data = {
        'artist':   media.get_meta(vlc.Meta.Artist),
        'title':    media.get_meta(vlc.Meta.Title),
        'url':      media.get_meta(vlc.Meta.URL),
        'mrl':      short_mrl(media.get_mrl())
    }

    if meta_data['artist']:
        return meta_data['artist'] + ' - ' + meta_data['title']
    elif meta_data['url']:
        return meta_data['url']
    else:
        return meta_data['mrl']

def media_list_player_get_song(media_list_player):
    '''Return a nice string of current track information'''
    return media_get_song(media_list_player.get_media_player().get_media())

def media_list_clear(media_list):
    '''Removes all vlc.Media from a vlc.MediaList'''
    while media_list.count() > 0:
        media_list.remove_index(0)

def media_list_flatten(media_list):
    '''Opening a directoy with Media can lead to:
    MediaList -> Media -> MediaList
    This breaks total MediaList.count() and makes shuffling hard
    Flattening ensurces a MediaList is full of single-file Media'''
    list_of_media = []
    for media in media_list:
        if not media.is_parsed():
            media.parse()
        if media.subitems().count() > 0:
            for sub_media in media.subitems():
                list_of_media.append(sub_media)
        else:
            list_of_media.append(media)

    media_list_clear(media_list)
    for media in list_of_media:
        media_list.add_media(media)

def media_list_shuffle(media_list):
    '''Shuffles a vlc.MediaList'''
    media_list_flatten(media_list)
    shuffled_list = []
    
    shuffled_indexes = list(range(media_list.count()))
    shuffle(shuffled_indexes)
    for i in range(media_list.count()):
        shuffled_list.append(media_list[shuffled_indexes[i]])
    
    media_list_clear(media_list)
    for media in shuffled_list:
        media_list.add_media(media)

def modify_media_list(mrl, media_list, media_player, shuffle=True, append=False, switch_current=False):
    '''For setting a new playlist to a vlc.MediaList, or appending to it.
    Shuffle is enabled by default.'''
    if not append:
        media_list_clear(media_list)

    if os.path.isdir(mrl):
        list_of_media = [vlc.Media(audio_file) for audio_file in audio_file_dir_walk(mrl)]
    else:
        list_of_media = [vlc.Media(mrl)]

    for media in list_of_media:
        media_list.add_media(media)
    media_list_flatten(media_list)

    if shuffle:
        media_list_shuffle(media_list)

    if switch_current:
        media_player.play_item(choice(list_of_media))

def audio_file_dir_walk(directory, allowed_file_extensions={'mp3','wav'}):
    '''VLC 3  does not auto-expand directories in media isntances.
    This function walks recursively through directories to obtain all allowed
    audio files and creates a list of file locations'''
    # VLC doesn't auto-expand directories with Media instances.
    # Outputs list of files
    re_exp = '(?:\.'
    for ext in allowed_file_extensions:
        re_exp += ext + '|'
    re_exp = re_exp[:-1:]
    re_exp += ')$'

    music_file_list = []
    for file_or_directory in os.listdir(directory):
        i_path = os.path.join(directory, file_or_directory)
        if os.path.isfile(i_path):
            if re.search(re_exp, file_or_directory, re.IGNORECASE):
                music_file_list.append(i_path)
        elif os.path.isdir(i_path):
            music_file_list += audio_file_dir_walk(i_path)

    return music_file_list


######################################################################
#
#   3. Define nofication websockets server class
#
######################################################################
class NotificationWebsocketsServer:
    '''Creates a websocket server for clients to connect to and receive
    updates about media list changes. Allows not to have to poll for updates'''
    users = set()
    music_change = False
    ambience_change = False

    def __init__(self):
        new_loop = asyncio.new_event_loop()
        start_server = websockets.serve(self.handler, '0.0.0.0', 8140, loop=new_loop)
        t = Thread(target=self.start_loop, args=(new_loop, start_server))
        t.start()

    async def register(self, websocket):
        self.users.add(websocket)

    async def unregister(self, websocket):
        self.users.remove(websocket)

    async def handler(self, websocket, path):
        await self.register(websocket)
        await websocket.send('welcome')
        try:
            while not websocket.closed:
                await asyncio.sleep(1)
                if self.music_change:
                    self.music_change = False
                    await self.music_change_notify()
                if self.ambience_change:
                    self.ambience_change = False
                    await self.ambience_change_notify()
        finally:
            await websocket.close()
            await self.unregister(websocket)

    def start_loop(self, loop, server):
        loop.run_until_complete(server)
        loop.run_forever()

    async def music_change_notify(self):
        if self.users:
            for user in self.users:
                await user.send('music_changed')

    async def ambience_change_notify(self):
        if self.users:
            for user in self.users:
                await user.send('ambience_changed')


######################################################################
#
#   4. Define AudioPlayers Class
#
######################################################################
class AudioPlayers:
    '''A class of 4 audio players, their playlists
    1: Stream of virtual audio to 127.0.0.1:[streamport]
    2. Music stream to virtual audio
    3. Ambience stream to virtual audio
    4. Clips stream to virtual audio
    Clips are handled by a Clips thread instance.'''
    def __init__(self, config_data):
        # 0. Parameters
        self.config_data = config_data

        # 1. VLC instance and its players
        self.i = vlc.Instance('--quiet --no-video --sout-http-mime=audio/mpeg --no-http-forward-cookies')
        self.mp_vaudio = self.i.media_player_new()
        self.mp_music = self.i.media_list_player_new()
        self.mp_ambience = self.i.media_list_player_new()
        self.mp_clips = self.i.media_player_new()

        # 2. Playlists (MediaLists)
        self.ml_music = self.i.media_list_new()
        self.ml_ambience = self.i.media_list_new()
        self.mp_music.set_media_list(self.ml_music)
        self.mp_ambience.set_media_list(self.ml_ambience)

        # 3. Event managers (Song history & websocket notifications)
        self.notification_server = NotificationWebsocketsServer()
        self.em_music = self.mp_music.get_media_player().event_manager()
        self.history_music = []
        self.em_ambience = self.mp_ambience.get_media_player().event_manager()
        self.history_ambience = []

        def media_changed_event(event, self, music_or_ambience):
            '''callback function for event managers to store track history and notify websockets clients of track changes'''
            # update history
            mp = getattr(self, 'mp_' + music_or_ambience)
            history = getattr(self, 'history_' + music_or_ambience)
            if len(history) == 101:
                history = history[1::]
            history.append(media_list_player_get_song(mp))
            setattr(self, 'history_' + music_or_ambience, history)

            # set notificatoin server thread to notify
            if self.notification_server.users:
                setattr(self.notification_server, music_or_ambience + '_change', True)

        self.em_music.event_attach(vlc.EventType.MediaPlayerMediaChanged, media_changed_event, self, 'music')
        self.em_ambience.event_attach(vlc.EventType.MediaPlayerMediaChanged, media_changed_event, self, 'ambience')
        
        # 4. Clips need a special Thread
        self.clips_thread = Clips(self)
        self.clips_thread.start()

        # 5. Initialise and start the players
        self.initialise_players()
        self.start_players()

    def initialise_players(self):
        # vaudio
        transcode_cmd = 'sout=#transcode{vcodec=none,acodec=mp3,ab=320,channels=2,samplerate=44100}:'
        transcode_cmd += 'http{mux=mp3,dst=' + str(self.config_data['interface']) + ':' + str(self.config_data['stream_port']) + '}'
        
        full_cmd = [
            transcode_cmd,
            'sout-keep',
            'file-caching=1000'
        ]

        m_vaudio = self.i.media_new('pulse://virtual.monitor', *full_cmd)
        self.mp_vaudio.set_media(m_vaudio)
        self.mp_vaudio.audio_set_volume(100)

        # music
        if self.config_data['default_files']['music']:
           modify_media_list(self.config_data['default_files']['music'], self.ml_music, self.mp_music)
        else:
           modify_media_list(self.config_data['audio_dirs']['music'], self.ml_music, self.mp_music)
        self.mp_music.set_playback_mode(vlc.PlaybackMode.loop)
        self.mp_music.get_media_player().audio_set_volume(100)

        # ambience
        if self.config_data['default_files']['ambience']:
            modify_media_list(self.config_data['default_files']['ambience'], self.ml_ambience, self.mp_ambience)
        else:
            modify_media_list(self.config_data['audio_dirs']['ambience'], self.ml_ambience, self.mp_ambience)
        self.mp_ambience.set_playback_mode(vlc.PlaybackMode.loop)
        self.mp_ambience.get_media_player().audio_set_volume(75)

    def start_players(self):
        self.mp_vaudio.play()
        if self.config_data['startup_players']['music']:
            self.mp_music.play()
        if self.config_data['startup_players']['ambience']:
            self.mp_ambience.play()
        if self.config_data['startup_players']['clips']:
            self.toggle_clips()

    def toggle_clips(self, force_on=False, force_off=False):
        if force_on:
            self.clips_thread.clips_on = True
        elif force_off:
            self.clips_thread.clips_on = False
        else:
            self.clips_thread.clips_on = not self.clips_thread.clips_on

    def nice_quit(self):
        '''Exits threads safely. Fades out volume. Waits if a clip is currently playing.'''
        print('Quitting... Please wait')
        self.clips_thread.exit_program = True

        if self.clips_thread.clip_playing:
            print('waiting for clip to finish')
            while self.clips_thread.clip_playing:
                sleep(1)

        fade_volume_players(
            [self.mp_music.get_media_player(), self.mp_ambience.get_media_player()],
            [0, 0]
        )
        self.mp_vaudio.stop()
        self.mp_music.get_media_player().audio_set_volume(100)


######################################################################
#
#   5. Define ClipsThread Thread
#       Manages clip playing times
#
######################################################################
class Clips(Thread):
    '''Handles the intermittment playing of sound clips
    Fades down other players for 2 seconds, plays a randomly-selected clip, then fades
    the other plays back to their initial volume. If there is more than one clip 
    available, then no clip will be repeated twice in a row'''
    # Handles the intermittent playing of sound clips
    def __init__(self, parent):
        super(Clips, self).__init__()
        self.mp_clips = parent.mp_clips
        self.mp_music = parent.mp_music
        self.mp_ambience = parent.mp_ambience
        self.clip_timing = parent.config_data['clip_timing']
        self.clips_dir = parent.config_data['audio_dirs']['clips']
        
        self.clips_on = False
        self.clip_schedule = None       # or Datetime object
        self.last_played_clip = None    # prevent same clip twice in a row, if > 1
        self.exit_program = False
        self.clip_playing = False

    def schedule_clip(self):
        offset = datetime.timedelta(minutes=int(normalvariate(
            self.clip_timing['clip_mean'],
            self.clip_timing['clip_std_deviation']
        )))
        self.clip_schedule = datetime.datetime.today() + offset
        if Debug:
            print('Clip scheduled: ' + str(self.clip_schedule))

    def play_clip(self):
        # 0. Select random clip
        # Make sure it is not last played clip if there is more than one
        self.clip_playing = True
        clips = os.listdir(self.clips_dir)
        if len(clips) > 1 and self.last_played_clip:
            clips.remove(self.last_played_clip)

        random_clip = choice(clips)
        self.last_played_clip = random_clip

        # 1. Lower main players volume
        fade_volume_players(
            [self.mp_music.get_media_player(), self.mp_ambience.get_media_player()],
            [65, 45]
        )

        # 2. Play voiceclip
        # Wait for it to finish
        clip = self.mp_clips.get_instance().media_new(os.path.join(self.clips_dir, random_clip))
        self.mp_clips.set_media(clip)
        self.mp_clips.audio_set_volume(100)
        self.mp_clips.play()
        
        sleep(0.5)
        while self.mp_clips.is_playing():
            sleep(0.5)

        # 3. Return main players volume
        fade_volume_players(
            [self.mp_music.get_media_player(), self.mp_ambience.get_media_player()],
            [100, 75]
        )
        self.clip_schedule = None
        self.clip_playing = False

    def run(self):
        while True:
            if self.exit_program:
                return
            elif self.clips_on:
                if not self.clip_schedule:
                    self.schedule_clip()
                elif datetime.datetime.today() > self.clip_schedule:
                    self.play_clip()
            elif self.clip_schedule:
                self.clip_schedule = None
            sleep(1)
