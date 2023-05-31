from functools import wraps

from flask import abort, redirect, render_template, url_for
from flask.views import MethodView
from flask_login import AnonymousUserMixin, current_user, login_required
from sqlalchemy.exc import NoResultFound

from tictactoe.models import Game, GameSession

from . import games


def session_of_user(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            game_session_user_id = (
                GameSession.query.filter_by(id=int(kwargs["sid"])).one().user_id
            )
        except NoResultFound:
            abort(404)

        if (
            not isinstance(current_user, AnonymousUserMixin)
            and current_user.id == game_session_user_id
        ):
            result = func(*args, **kwargs)
            return result

        abort(404)

    return decorated_view


class SessionListAPI(MethodView):
    decorators = [login_required]

    def get(self):
        sessions = GameSession.query.filter_by(user_id=current_user.id)
        return render_template(
            "sessions_list.html", title="Sessions list", sessions=sessions
        )

    def post(self):
        new_session = current_user.start_a_new_session()
        return redirect(url_for("games.game_session", sid=new_session.id))


class SessionAPI(MethodView):
    decorators = [login_required, session_of_user]

    def get(self, sid):
        game_session = GameSession.query.filter_by(id=sid).one()
        return render_template(
            "game_session.html", title="Games list", game_session=game_session
        )

    def post(self, sid):
        game_session = GameSession.query.filter_by(id=sid).one()
        new_game = game_session.start_a_new_game()
        return redirect(url_for("games.game", gid=new_game.id))


class GameAPI(MethodView):
    decorators = [login_required]

    def get(self, gid):
        return render_template(
            "game.html", title="Game", game=Game.query.filter_by(id=gid).one()
        )


games.add_url_rule("/sessions", view_func=SessionListAPI.as_view("sessions_list"))
games.add_url_rule("/sessions/<int:sid>", view_func=SessionAPI.as_view("game_session"))
games.add_url_rule("/game/<int:gid>", view_func=GameAPI.as_view("game"))
