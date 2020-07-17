import player_backend
import io_functions
import flask_resources
from flask import Flask
from flask_restful import Api
from string import ascii_uppercase, digits
from random import choice

config_data = player_backend.load_config()

app = Flask(__name__)
api = Api(app)

app.secret_key = ''.join(choice(ascii_uppercase + digits) for _ in range(100))

app.url_map.strict_slashes = False

players_instance = player_backend.AudioPlayers(config_data)
ih = io_functions.InputHandler(players_instance)

flask_resources.limiter.init_app(app)

flask_resources.bind_flask_resources(api, ih)
api.add_resource(
    flask_resources.Admin,
    '/admin',
    resource_class_kwargs={'password': config_data['admin_password']}
)

app.run(host=config_data['interface'], port=config_data['io_port'], debug=False)
players_instance.nice_quit()
