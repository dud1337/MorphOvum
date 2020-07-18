######################################################################
#
#       Morph Ovum Main
#
#       1. Imports config.yaml data
#       2. Creates Flask app
#       3. Creates AudioPlayers and InputHandler instances
#       4. Converts InputHandler API functions to Resources and binds them to Flask App
#       5. Binds Admin Resource to Flask App
#       6. Runs the API
#
######################################################################
import player_backend
import io_functions
import flask_resources
from flask import Flask
from flask_restful import Api
from string import ascii_uppercase, digits
from random import choice

ascii_splash = '''
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
    '/admin',
    resource_class_kwargs={'password': config_data['admin_password']}
)


######################################################################
#
#       6. Runs the API
#
######################################################################
print(ascii_splash)
app.run(host=config_data['interface'], port=config_data['io_port'], debug=False)
#   Safe exit to end processes correctly
players_instance.nice_quit()
