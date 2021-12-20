import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .models import db
from .api import api_blueprint

# from .commands import create_superadmin, create_superadmin_token


load_dotenv()


def create_app(testing=False):
    app = Flask('daily_users_api')

    config_path = os.getenv("DAILY_USERS_API_CONFIG_PATH", "daily_users_api.config.LocalConfig")
    app.config.from_object(config_path)

    if testing is True:
        app.config['TESTING'] = True

    CORS(app)

    # Init db extension
    db.init_app(app)

    app.register_blueprint(api_blueprint)

    # # Register general commands
    # app.cli.add_command(create_superadmin)
    # app.cli.add_command(create_superadmin_token)
    return app
