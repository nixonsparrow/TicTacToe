from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from tictactoe.config import Config
from tictactoe.utils import socketio

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login_page"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app=app)
    bcrypt.init_app(app=app)
    login_manager.init_app(app=app)

    from tictactoe.errors.handlers import errors  # noqa F401
    from tictactoe.games.routes import games  # noqa F401
    from tictactoe.main.routes import main  # noqa F401
    from tictactoe.users.routes import users  # noqa F401

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(games)
    app.register_blueprint(errors)

    from tictactoe.template_filters import jinja_filters  # noqa F401

    for jinja_filter in jinja_filters:
        app.jinja_env.filters[jinja_filter.__name__] = jinja_filter

    socketio.init_app(app)

    return app
