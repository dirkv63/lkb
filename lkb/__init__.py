# import os
from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from lib import my_env

bootstrap = Bootstrap()
db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'main.login'


def create_app(config_class=Config):
    """
    Create an application instance.

    :param config_class: Pointer to the configuration file.
    :return: the configured application object.
    """
    app = Flask(__name__)

    # import configuration
    app.config.from_object(config_class)

    # Configure Logger
    my_env.init_loghandler(__name__, app.config.get('LOGDIR'), app.config.get('LOGLEVEL'))

    # initialize extensions
    bootstrap.init_app(app)
    db.init_app(app)
    lm.init_app(app)

    # add Jinja Filters
    app.jinja_env.filters['datestamp'] = my_env.datestamp
    app.jinja_env.filters['reformat_body'] = my_env.reformat_body
    app.jinja_env.filters['children_sorted'] = my_env.children_sorted
    app.jinja_env.filters['fix_urls'] = my_env.altfix_urls

    # import blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # configure production logging of errors
    return app
