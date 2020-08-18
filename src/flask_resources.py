######################################################################
#
#   Flask Resource Generation
#
#   1. Defines admin login process & Creates admin API resource
#   2. Provides function to create multiple API resources from InputHandler class methods
#   3. Provides function to bind API resources to a flask API
#   4. Define Web UI resources
#
######################################################################
from flask import session, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, reqparse
from inspect import getfullargspec
from hashlib import sha256
from functools import partial
import datetime

limiter = Limiter(key_func=get_remote_address)


######################################################################
#
#   1. Defines admin login process & Creates admin API resource
#
######################################################################
def admin_check(func=None, *args, **kwargs):
    '''wraps (via partial) @admin functions in io_functions'''
    if 'admin' in session:
        return func(*args, **kwargs)
    else:
        return {'err':'requires admin privileges'}

class Admin(Resource):
    '''Handles admin authentication via POST and `password_hash` parameter.
    Checks if session is admin with GET'''
    decorators = [limiter.limit('10 per minute', methods=['POST'])]
    def __init__(self, password):
        super(Admin, self).__init__()
        self.hashed_pw = sha256(password.encode('utf-8')).hexdigest()

    def post(self):
        '''Handles admin login'''
        parser = reqparse.RequestParser()
        parser.add_argument(
            'password_hash',
            dest='password_hash',
            location='form',
            required=True,
            help='The admin passwords SHA256 hash'
        )
        args = parser.parse_args()
        if args.password_hash == self.hashed_pw:
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


######################################################################
#
#   2. Provides function to create multiple API resources from InputHandler class methods
#
######################################################################
def rest_resource_generate(func_name, func, class_instance):
    '''Generate REST resources for an io function
    input: music_lsp
    output: 'MusicLsp', ['/music/lsp', '/music/lsp/']
    '''
    class_name = ''
    for segment in func_name.split('_'):
        class_name += segment[0].upper() + segment[1::]

    rest_url_resources = []
    rest_res = '/' + func_name.replace('_','/')
    rest_url_resources.append(rest_res)

    arg_list = getfullargspec(getattr(class_instance.__class__, func_name))[0]
    arg_list.remove('self')

    if arg_list:
        def post_handler():
            parser = reqparse.RequestParser()
            for arg in arg_list:
                parser.add_argument(
                    arg,
                    dest=arg,
                    location='form',
                    required=True,
                    help=arg
                )
            args = parser.parse_args()
            
            return func(**args)

        if hasattr(func, 'is_admin_method'):
            post_func = partial(admin_check, func=post_handler)
        else:
            post_func = post_handler
        rest_resource_class = type(
            class_name,
            (Resource,),
            dict(post=post_func)
        )
    else:
        if hasattr(func, 'is_admin_method'):
            post_func = partial(admin_check, func=func)
        else:
            post_func = func
        rest_resource_class = type(
            class_name,
            (Resource,),
            dict(get=post_func)
        )

    return rest_resource_class, rest_url_resources


######################################################################
#
#   3. Provides function to bind API resources to a flask API
#
######################################################################
def bind_flask_resources(flask_api, class_instance):
    '''Generate Flask RESTful API via methods of InputHandler'''
    for attr_name in dir(class_instance):
        attr = getattr(class_instance, attr_name)
        if hasattr(attr, 'is_api_method'): 
            tmp_class, rest_url_resources = rest_resource_generate(attr_name, attr, class_instance)
           
            flask_api.add_resource(tmp_class, *rest_url_resources)


######################################################################
#
#   4. Define Web UI resources
#
######################################################################
def web_ui_adder(api):
    api.add_resource(WebUI_index, '/')
    api.add_resource(WebUI_cp_index, '/command_panel.html')
    api.add_resource(WebUI_cp_js, '/command_panel.js')
    api.add_resource(WebUI_cp_css, '/command_panel.css')
    api.add_resource(WebUI_json, '/api_data.json')
    api.add_resource(WebUI_favicon, '/favicon.ico')

class WebUI_index(Resource):
    def get(self):
        with open('./www/index.html') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'text/html'
        return response

class WebUI_cp_index(Resource):
    def get(self):
        with open('./www/command_panel.html') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'text/html'
        return response

class WebUI_cp_js(Resource):
    def get(self):
        with open('./www/command_panel.js') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'application/javascript'
        return response

class WebUI_cp_css(Resource):
    def get(self):
        with open('./www/command_panel.css') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'text/css'
        return response

class WebUI_json(Resource):
    def get(self):
        with open('./www/api_data.json') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'application/json'
        return response

class WebUI_favicon(Resource):
    def get(self):
        with open('./www/favicon.ico', 'rb') as f:
            response = make_response(f.read())
        response.headers['Content-Type'] = 'image/x-icon'
        return response
