######################################################################
#
#   IO Function Handler 
#
#   1. Creates decorators to make function flags:
#       Make function accessible via API (api)
#       Admin Only (admin)
#       Backend busy (busy)
#       Rate limiting (patience)
#   2. Defines the intput handler class
#       Takes an AudioPlayers class
#       Defines meta-functions
#       Defines functions to be used by the API
#
######################################################################
import os
import datetime
import player_backend
import decorator
import re
import requests
from inspect import getfullargspec

######################################################################
#
#   1. Creates decorators to make function flags:
#
######################################################################
@decorator.decorator
def busy(func, *args, **kwargs):
    '''Certain commands may take time. In order to avoid multiple
    high-cost commands issued at once, this sets the InputHandler
    to a "busy" state until the command is completed.'''
    io_instance = args[0]
    if io_instance.busy:
        return {'err':'Busy. Please try again'}
    else:
        io_instance.busy = True
        out = func(*args, **kwargs)
        io_instance.busy = False
        return out

def busy_flag(func):
    '''adds the is_busy_method attribute'''
    # Need to figure out a way to use decorator.decorator to do this
    func.is_busy_method = True
    return func

@decorator.decorator
def patience(func, *args, **kwargs):
    '''Disallow certain commands being spammed too frequently'''
    io_instance = args[0]
    timeout = 3
    now = datetime.datetime.today()

    diff = (now - io_instance.last_change).seconds

    if diff < timeout:
        return {'err':'Please wait ' + str(timeout - diff) + ' seconds'}
    else:
        io_instance.last_change = now 
        return func(*args, **kwargs)

def patience_flag(func):
    '''adds the is_patience_method attribute'''
    func.is_patience_method = True
    return func

def admin(func):
    '''adds the is_admin_method attribute'''
    func.is_admin_method = True
    return func

def api(func):
    '''adds is_api_method attribute'''
    func.is_api_method = True
    return func


######################################################################
#
#   2.  Defines the intput handler class
#
######################################################################
class InputHandler:
    '''The IO functions for the primary AudioPlayers class.
    A Flask RESTful API is defined based on the methods of this class
    if their name starts with 'api_'
    '''
    def __init__(self, audio_players):
        self.audio_players = audio_players
        self.last_change = datetime.datetime.today()
        self.busy = False
        self.last_chance = datetime.datetime.today()
        self.api_methods = None
        self.generate_help()

    def generate_help(self):
        '''Provides API commands and arguments, if any'''
        self.api_methods = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, 'is_api_method'):
                if len(getfullargspec(attr)[0]) > 1:
                    arg = getfullargspec(attr)[0][1]
                else:
                    arg = False

                self.api_methods[attr_name] = {
                    'description'   :attr.__doc__,
                    'arg'           :arg
                }

    def ls_funcs(self, directory, music_or_ambience, ls_type):
        '''Deals with listing, playing and appending playlists to various functions'''
        path = os.path.join(self.audio_players.config_data['audio_dirs'][music_or_ambience], directory)

        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)

        if not os.path.isdir(path):
            return {'err':'"' + directory + '" is not a directory'}
        if ls_type == 'ls':
            return {'msg':'ok! got conents of ' + directory + ' directory', 'data':sorted(os.listdir(path))}
        elif ls_type == 'lsp': 
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                switch_current=True
            )
            return {'msg':'ok! ' + music_or_ambience + ' set to: ' + directory}
        elif ls_type == 'lsc':
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                append=True,
                shuffle=False
            )
            return {'msg':'ok! ' + music_or_ambience + ' appended with: ' + directory}
        elif ls_type == 'lsa':
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                append=True,
            )
            return {'msg':'ok! ' + music_or_ambience + ' added and shuffled with: ' + directory}

    def wp_funcs(self, url, music_or_ambience, wp_type):
        '''Runs a series of checks, then appends + plays the web media to the playlist'''
        if not re.search('^https?://', url):
            return {'err':'url is missing protocol (http or https)'}

        if re.search('http(?:s?)://?(?:www\.)?youtu\.?be(?:\.com)?', url):
            if not re.search('http(?:s?)://(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]{11})(&(amp;)?[\w\=]*|$)', url):
                return {'err':'YouTube url ' + url + ' abnormal'}
        
        try:
            r = requests.get(url)
            if r.status_code != 200:
                return {'err':'url ' + url + ' returned status code ' + str(r.status_code)}
        except requests.exceptions.RequestException as e:
            return {'err':'GET request to url ' + url + ' failed with error message: ' + e}

        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)

        if wp_type == 'wp':
            player_backend.modify_media_list(
                url,
                ml,
                mp,
                switch_current=True
            )
            track = player_backend.media_list_player_get_song(mp)
            return {'msg':'ok! ' + music_or_ambience + ' playing: ' + track}

        elif wp_type == 'wc':
            player_backend.modify_media_list(
                url,
                ml,
                mp,
                append=True,
                shuffle=False
            )
            track = player_backend.media_list_player_get_song(mp)
            return {'msg':'ok! ' + music_or_ambience + ' enqeued with: ' + track}

    def current_funcs(self, music_or_ambience, track_or_playlist):
        '''Returns current song or list of media currently in a player's MediaList'''
        if track_or_playlist == 'track':
            mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
            track = player_backend.media_list_player_get_song(mp)

            return {'msg':'ok!', 'data':track}
        elif track_or_playlist == 'playlist':
            ml = getattr(self.audio_players, 'ml_' + music_or_ambience)
            output_data = []
            for media in ml:
                output_data.append(player_backend.media_get_song(media))
    
            return {'msg':'ok!', 'data':output_data}

    def skip_funcs(self, music_or_ambience):
        '''Skips (runs next()) on the current track of a player'''
        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)
        old_track = player_backend.media_list_player_get_song(mp)
        if ml.count() == 1:
            return {'err':'only one file in playlist: ' + old_track}
        mp.next()
        new_track = player_backend.media_list_player_get_song(mp)

        output = {
            'msg':'ok! ' + music_or_ambience + ' player skipped track: ' + old_track + ' \n now playing: ' + new_track,
            'data':{
                'old_track':old_track,
                'new_track':new_track
            }
        }
        return output

    def player_toggle(self, music_or_ambience):
        '''Toggles a player's playing status'''
        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        is_playing = mp.is_playing()
        if is_playing:
            mp.stop()
            status = 'stopped'
        else:
            mp.play()
            status = 'playing'
        return {'msg':'ok! ' + music_or_ambience + ' is ' + status}

    def history_funcs(self, music_or_ambience):
        '''Returns up to 100 of the last played tracks for a player'''
        history = getattr(self.audio_players, 'history_' + music_or_ambience)
        return {'msg':'ok! ' + str(len(history)) + ' tracks in history', 'data':history}

    #   API Definitions
    @api
    def help(self):
        '''Return the available commands and their arguments, if any'''
        return {'msg':'ok!', 'data':self.api_methods}

    @admin
    @api
    def music_ls(self, directory='.'):
        '''List the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory, 'music', 'ls')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_lsp(self, directory='.'):
        '''Play a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory, 'music', 'lsp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_lsc(self, directory='.'):
        '''Enqueue a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory, 'music', 'lsc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_lsa(self, directory='.'):
        '''Add and shuffle a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory, 'music', 'lsa')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_wp(self, url):
        '''Play the web resource in the music player'''
        return self.wp_funcs(url, 'music', 'wp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_wc(self, url):
        '''Enqueue the web resource in the music player'''
        return self.wp_funcs(url, 'music', 'wc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_skip(self):
        '''Skip the currently playing music track'''
        return self.skip_funcs('music')

    @admin
    @api
    @patience
    @patience_flag
    def music_toggle(self):
        '''Toggle the playing of the music player'''
        return self.player_toggle('music')

    @api
    def music_current_track(self):
        '''Return the currently playing music track'''
        return self.current_funcs('music', 'track')

    @api
    def music_current_playlist(self):
        '''Return the currently playing music playlist'''
        return self.current_funcs('music', 'playlist')

    @api
    def music_history(self):
        '''Returns the last music tracks played (max 100)'''
        return self.history_funcs('music')

    @api
    def music_playlists(self, playlist=''):
        '''Lists available playlists'''
        playlists = sorted(os.listdir(self.audio_players.config_data['playlist_dir']))
        return {'msg':'ok! returned ' + str(len(playlists)) + ' playlists', 'data':playlists}

    @admin
    @api
    @patience
    @patience_flag
    def music_playlist(self, playlist=''):
        '''Plays a playlist from available playlists. An int n input will play the nth playlist'''
        try:
            playlist_number = int(playlist)
            playlist = sorted(os.listdir(self.audio_players.config_data['playlist_dir']))[playlist_number]
            
        except:
            path = os.path.join(self.audio_players.config_data['playlist_dir'], playlist)

            if not os.path.isfile(path):
                return {'err':'"' + directory + '" is not a file'}
            else:
                player_backend.modify_media_list(path, self.audio_players.ml_music, self.audio_players.mp_music)
                return {'msg':'ok! music set to: ' + playlist}

    @admin
    @api
    def ambience_ls(self, directory='.'):
        '''List the contents of a subdirectory in the ambience directory'''
        return self.ls_funcs(directory, 'ambience', 'ls')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_lsp(self, directory='.'):
        '''Play a file or the contents of a subdirectory in the ambience directory'''
        return self.ls_funcs(directory, 'ambience', 'lsp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_lsc(self, directory='.'):
        '''Enqueue a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory, 'ambience', 'lsc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_lsa(self, directory='.'):
        '''Add and shuffle a file or the contents of a subdirectory in the ambience directory'''
        return self.ls_funcs(directory, 'ambience', 'lsa')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_wp(self, url):
        '''Play the web resource in the ambience player'''
        return self.wp_funcs(url, 'ambience', 'wp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_wc(self, url):
        '''Enqueue the web resource in the ambience player'''
        return self.wp_funcs(url, 'ambience', 'wc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_skip(self):
        '''Skip the current ambience track'''
        return self.skip_funcs('ambience')

    @admin
    @api
    @patience
    @patience_flag
    def ambience_toggle(self):
        '''Toggle the playing of the ambience player'''
        return self.player_toggle('ambience')

    @api
    def ambience_current_track(self):
        '''Return the currently playing ambience track'''
        return self.current_funcs('ambience', 'track')

    @api
    def ambience_current_playlist(self):
        '''Return the currently playing ambience playlist'''
        return self.current_funcs('ambience', 'playlist')

    @api
    def ambience_history(self):
        '''Returns up to 100 of the last played tracks for a player'''
        return self.history_funcs('ambience')

    @admin
    @api
    def clips_toggle(self): 
        '''Toggle the playing of clips'''
        self.audio_players.toggle_clips()
        on_off = 'on' if self.audio_players.clips_thread.clips_on else 'off'
        return {'msg':'ok! clips turned ' + on_off}

    @admin
    @api
    @patience
    @patience_flag
    def clips_now(self):
        '''Schedule a clip to be played now'''
        if not self.audio_players.clips_thread.clips_on:
            return {'err':'clips not enabled. try /clips/toggle first'}

        now = datetime.datetime.today()
        self.audio_players.clips_thread.clip_schedule = now
        return {'msg':'ok! clip scheduled for ' + str(now)}
