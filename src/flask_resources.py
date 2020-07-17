from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, reqparse
from inspect import getargspec
from hashlib import sha256
from functools import partial
import datetime

limiter = Limiter(key_func=get_remote_address)

def admin_check(func=None, *args, **kwargs):
    '''wraps (via partial) @admin functions in io_functions'''
    if 'admin' in session:
        return func(*args, **kwargs)
    else:
        return {'err':'requires admin privileges'}

class Admin(Resource):
    '''Handles admin authentication via POST and `password` parameter.
    Checks if session is admin with GET'''
    decorators = [limiter.limit('10 per minute', methods=['POST'])]
    def __init__(self, password):
        super(Admin, self).__init__()
        self.hashed_pw = sha256(password.encode('utf-8')).hexdigest()

    def post(self):
        '''Handles admin login'''
        parser = reqparse.RequestParser()
        parser.add_argument(
            'password',
            dest='password',
            location='form',
            required=True,
            help='The admin password'
        )
        args = parser.parse_args()
        if args.password == self.hashed_pw:
            session['admin'] = True
            return {'msg':'ok!'}
        else:
            return {'err':'incorrect password'}

    def get(self):
        '''Check if session has admin credentials'''
        if 'admin' in session:
            return {'msg':'ok! you are admin', 'data':True}
        else:
            return {'msg':'you are not admin', 'data':False}

def rest_resource_generate(func_name, class_instance):
    '''Generate REST resources for an io function
    input: music_lsp
    output: 'MusicLsp', ['/music/lsp', '/music/lsp/', '/music/lsp/<directory>', '/music/lsp/<directory>/']
    '''
    class_name = ''
    for segment in func_name.split('_'):
        class_name += segment[0].upper() + segment[1::]

    arg_list = getargspec(getattr(class_instance.__class__, func_name))[0]
    arg_list.remove('self')

    rest_url_resources = []
    rest_res = '/' + func_name.replace('_','/')
    rest_url_resources.append(rest_res)
    if arg_list:
        for arg in arg_list:
            rest_res += '/<path:' + arg + '>'
            rest_url_resources.append(rest_res)

    return class_name, rest_url_resources

def bind_flask_resources(flask_api, class_instance):
    '''Generate Flask RESTful API via methods of InputHandler'''
    for attr_name in dir(class_instance):
        attr = getattr(class_instance, attr_name)
        if hasattr(attr, 'is_api_method'): 
            class_name, rest_url_resources = rest_resource_generate(attr_name, class_instance)
           
            if hasattr(attr, 'is_admin_method'):
                tmp_class = type(
                    class_name,
                    (Resource,),
                    dict(get=partial(admin_check, func=attr))
                )
            else:
                tmp_class = type(
                    class_name,
                    (Resource,),
                    dict(get=attr)
                )
            flask_api.add_resource(tmp_class, *rest_url_resources)
