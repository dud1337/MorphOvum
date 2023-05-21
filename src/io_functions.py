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
import vlc

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
        return {'msg':'Busy. Please try again', 'err':True, 'data':None}
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
        return {'msg':'Please wait ' + str(timeout - diff) + ' seconds', 'err':True, 'data':None}
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

    def make_output_data(self, msg, err=False, data=None):
        return {'err':err, 'msg':msg, 'data':data}

    def ls_funcs(self, directory, music_or_ambience, ls_type):
        '''Deals with listing, playing, cuing and appending files or directories to various players'''
        base_dir = self.audio_players.config_data['audio_dirs'][music_or_ambience]
        path = os.path.join(base_dir, directory)

        if os.path.commonprefix((os.path.realpath(path), base_dir)) != base_dir:
            return self.make_output_data('directory traversal detected', err=True)

        if not os.path.exists(path):
            return self.make_output_data('no file or directory named "' + directory + '"', err=True)

        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)

        if ls_type == 'lsp':
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                switch_current=True
            )
            return self.make_output_data('' + music_or_ambience + ' set to: ' + directory)
        elif ls_type == 'lsc':
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                append=True,
                shuffle=False
            )
            return self.make_output_data(music_or_ambience + ' appended with: ' + directory)
        elif ls_type == 'lsa':
            player_backend.modify_media_list(
                path,
                ml,
                mp,
                append=True,
            )
            return self.make_output_data(music_or_ambience + ' added and shuffled with: ' + directory)
        elif ls_type == 'ls':
            if not os.path.isdir(path):
                return self.make_output_data('"' + directory + '" is not a directory', err=True)

            dir_contents = sorted(os.listdir(path))
            return self.make_output_data(' '.join(dir_contents), data=dir_contents)


    def wp_funcs(self, url, music_or_ambience, wp_type):
        '''Runs a series of checks, then appends + plays the web media to the playlist'''
        if not re.search('^https?://', url):
            return self.make_output_data('url is missing protocol (http or https)', err=True)

        if re.search('http(?:s?)://?(?:www\.)?youtu\.?be(?:\.com)?', url):
            if not re.search('http(?:s?)://(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]{11})((amp;)?[\w\=]*|$)', url):
                return self.make_output_data('YouTube url "' + url + '" abnormal', err=True)

        try:
            r = requests.get(url)
            if r.status_code != 200:
                return self.make_output_data('url ' + url + ' returned status code ' + str(r.status_code), err=True)
        except requests.exceptions.RequestException as e:
            return self.make_output_data('GET request to url ' + url + ' failed with error message: ' + str(e), err=True)

        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)

        if wp_type == 'wp':
            if player_backend.check_mrl(url):
                return self.make_output_data(f'Error: VLC cannot play {url}. Not added.')
            player_backend.modify_media_list(
                url,
                ml,
                mp,
                switch_current=True
            )
            track = player_backend.media_list_player_get_song(mp)
            return self.make_output_data(music_or_ambience + ' playing: ' + track)

        elif wp_type == 'wc':
            if player_backend.check_mrl(url):
                return self.make_output_data(f'Error: VLC cannot play {url}. Not added.')
            player_backend.modify_media_list(
                url,
                ml,
                mp,
                append=True,
                shuffle=False
            )
            return self.make_output_data(music_or_ambience + ' enqeued with: ' + url)

    def current_funcs(self, music_or_ambience, track_or_playlist):
        '''Returns current song or list of media currently in a player's MediaList'''
        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        is_playing = mp.is_playing()

        if track_or_playlist == 'track':
            mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
            track = player_backend.media_list_player_get_song(mp)

            return self.make_output_data(track, data={'track':track, 'is_playing':is_playing})
        elif track_or_playlist == 'playlist':
            ml = getattr(self.audio_players, 'ml_' + music_or_ambience)
            output_data = []
            for media in ml:
                output_data.append(player_backend.media_get_song(media))

            return self.make_output_data(' '.join(output_data), data={'playlist':output_data, 'is_playing':is_playing})

    def skip_funcs(self, music_or_ambience):
        '''Skips (runs next()) on the current track of a player'''
        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        ml = getattr(self.audio_players, 'ml_' + music_or_ambience)
        old_track = player_backend.media_list_player_get_song(mp)
        if ml.count() == 1:
            return self.make_output_data('only one file in playlist: ' + old_track, err=True)
        mp.next()
        new_track = player_backend.media_list_player_get_song(mp)

        return self.make_output_data(music_or_ambience + ' player skipped track: ' + old_track + ' \n now playing: ' + new_track, data={'old_track':old_track, 'new_track':new_track})

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
        return self.make_output_data(f'{music_or_ambience} is {status}')

    def repeat_toggle(self, music_or_ambience):
        '''Toggles a player's single-track repeat status'''
        mp = getattr(self.audio_players, 'mp_' + music_or_ambience)
        repeating = getattr(self.audio_players, f'{music_or_ambience}_repeat')
        if not repeating:
            mp.set_playback_mode(vlc.PlaybackMode.repeat)
            setattr(self.audio_players, f'{music_or_ambience}_repeat', True)
            status = 'repeating current track'
        else:
            mp.set_playback_mode(vlc.PlaybackMode.loop)
            setattr(self.audio_players, f'{music_or_ambience}_repeat', False)
            status = 'repeating playlist'
        return self.make_output_data(f'{music_or_ambience} is now {status}')

    def history_funcs(self, music_or_ambience):
        '''Returns up to 100 of the last played tracks for a player'''
        history = getattr(self.audio_players, 'history_' + music_or_ambience)
        return self.make_output_data(str(len(history)) + ' tracks in history', data=history)

    #   API Definitions
    @api
    def help(self):
        '''Return the available commands and their arguments, if any'''
        return self.make_output_data(str(self.api_methods), data=self.api_methods)

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
    def music_lsp(self, directory_or_file='.'):
        '''Play a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory_or_file, 'music', 'lsp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_lsc(self, directory_or_file='.'):
        '''Enqueue a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory_or_file, 'music', 'lsc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def music_lsa(self, directory_or_file='.'):
        '''Add and shuffle a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory_or_file, 'music', 'lsa')

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

    @admin
    @api
    @patience
    @patience_flag
    def music_repeat(self):
        '''Toggle the repeat_mode of the music player'''
        return self.repeat_toggle('music')

    @api
    def music_currenttrack(self):
        '''Return the currently playing music track'''
        return self.current_funcs('music', 'track')

    @api
    def music_currentplaylist(self):
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
        return self.make_output_data('returned ' + str(len(playlists)) + ' playlists', data=playlists)

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
                return self.make_output_data('"' + path + '" is not a file', err=True)
            else:
                player_backend.modify_media_list(path, self.audio_players.ml_music, self.audio_players.mp_music)
                return self.make_output_data('ok! music set to: ' + playlist)

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
    def ambience_lsp(self, directory_or_file='.'):
        '''Play a file or the contents of a subdirectory in the ambience directory'''
        return self.ls_funcs(directory_or_file, 'ambience', 'lsp')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_lsc(self, directory_or_file='.'):
        '''Enqueue a file or the contents of a subdirectory in the music directory'''
        return self.ls_funcs(directory_or_file, 'ambience', 'lsc')

    @admin
    @api
    @busy
    @busy_flag
    @patience
    @patience_flag
    def ambience_lsa(self, directory_or_file='.'):
        '''Add and shuffle a file or the contents of a subdirectory in the ambience directory'''
        return self.ls_funcs(directory_or_file, 'ambience', 'lsa')

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

    @admin
    @api
    @patience
    @patience_flag
    def ambience_repeat(self):
        '''Toggle the repeat_mode of the music player'''
        return self.repeat_toggle('ambience')

    @api
    def ambience_currenttrack(self):
        '''Return the currently playing ambience track'''
        return self.current_funcs('ambience', 'track')

    @api
    def ambience_currentplaylist(self):
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
        return self.make_output_data('ok! clips turned ' + on_off)

    @admin
    @api
    @patience
    @patience_flag
    def clips_now(self):
        '''Schedule a clip to be played now'''
        if not self.audio_players.clips_thread.clips_on:
            return self.make_output_data('clips not enabled. try /clips/toggle first', err=True)

        now = datetime.datetime.today()
        self.audio_players.clips_thread.clip_schedule = now
        return self.make_output_data('clip scheduled for ' + str(now)[:-7:])
