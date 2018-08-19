# third-party imports
from flask import Flask

# local imports
from config import app_config

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_object(app_config[config_name])


    from .questions import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    from .users import user_api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v2')

return app