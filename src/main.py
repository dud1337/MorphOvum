######################################################################
#
#       Morph Ovum Main
#
#       1. Imports config.yaml data
#       2. Creates Flask app
#       3. Creates AudioPlayers and InputHandler instances
#       4. Converts InputHandler API functions to Resources and binds them to Flask App
#       5. Binds Admin Resource to Flask App
#       6. Optionally binds Web UI Resources to Flask App
#       7. Runs the API
#
######################################################################
import player_backend
import io_functions
import flask_resources
import os
from flask import Flask, make_response
from flask_restful import Api
from string import ascii_uppercase, digits
from random import choice
from optparse import OptionParser

ascii_splash = r'''
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
'''


######################################################################
#
#   1. Import config.yaml() data
#
######################################################################
parser = OptionParser()
parser.add_option('-c', '--config', dest='config_file',
                          help='config yaml file to import', metavar='CONF')
(options, args) = parser.parse_args()

if options.config_file and os.path.isfile(options.config_file):
    config_data = player_backend.load_config(config_file=options.config_file)
else:
    config_data = player_backend.load_config()


######################################################################
#
#       2. Creates Flask app
#
######################################################################
app = Flask(__name__)
api = Api(app)
app.secret_key = ''.join(choice(ascii_uppercase + digits) for _ in range(100))
app.url_map.strict_slashes = False
#   Required to limits requests to admin panel
flask_resources.limiter.init_app(app)


######################################################################
#
#       3. Creates AudioPlayers and InputHandler instances
#
######################################################################
players_instance = player_backend.AudioPlayers(config_data)
ih = io_functions.InputHandler(players_instance)


######################################################################
#
#       4. Converts InputHandler API functions to Resources and binds them to Flask App
#
######################################################################
flask_resources.bind_flask_resources(api, ih)


######################################################################
#
#       5. Binds Admin Resource to Flask App
#
######################################################################
api.add_resource(
    flask_resources.Admin,
    '/api/admin',
    resource_class_kwargs={'password': config_data['admin_password']}
)


######################################################################
#
#       6. Optionally binds Web UI Resources to Flask App
#
######################################################################
if config_data['web_ui']:
    flask_resources.web_ui_adder(api)


######################################################################
#
#       7. Runs the API
#
######################################################################
print(ascii_splash)
app.run(host=config_data['interface'], port=config_data['io_port'], debug=False)
#   Safe exit to end processes correctly
players_instance.nice_quit()
