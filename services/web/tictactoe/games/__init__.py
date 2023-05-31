from flask import Blueprint

games = Blueprint("games", __name__)

from . import events, routes  # noqa F401, E402
