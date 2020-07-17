from flask import Flask, session
from flask_restful import Api, Resource, reqparse
from functools import partial
import string
import random
import sys
import decorator

app = Flask(__name__)
api = Api(app)

app.url_map.strict_slashes = False

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50)) 

class Admin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'password',
            dest='password',
            location='form',
            required=True,
            help='The admin password'
        )
        args = parser.parse_args()
        if args.password == 'coolBUTT':
            session['admin'] = True
            return 'alllright'
        else:
            return 'fuck you'

    def get(self):
        if 'admin' in session:
            return 'You\'re admin'
        else:
            return 'You\'re just some punk'

api.add_resource(Admin, '/admin')

def test_func():
    return {'dog':1337}

def admin_check(func=None, *args, **kwargs):
    if 'admin' in session:
        return func(*args, **kwargs)
    else:
        return 'admin is not in session'

test_partial = partial(admin_check, func=test_func)
print('ok')

test_class = type(
    'test_class',
    (Resource,),
    {'get':test_partial}
)

api.add_resource(test_class, '/test')

app.run(host='127.0.0.1', port=8139, debug=False)
