import datetime
import random

from flask_login import UserMixin
from sqlalchemy import JSON, DateTime
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.sql import func

from tictactoe import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    sessions = db.relationship(
        "GameSession", backref="player", lazy=True, order_by="desc(GameSession.id)"
    )

    def __repr__(self):
        return f"User('{self.username}')"

    def games(self, date=None):
        games = Game.query.filter(
            GameSession.user_id == self.id, GameSession.id == Game.session_id
        ).order_by(Game.creation_time.desc())
        if date:
            p_day = date - datetime.timedelta(days=1)
            previous_day = datetime.datetime(
                year=p_day.year,
                month=p_day.month,
                day=p_day.day,
                hour=23,
                minute=59,
                second=59,
            )
            n_day = date + datetime.timedelta(days=1)
            next_day = datetime.datetime(
                year=n_day.year,
                month=n_day.month,
                day=n_day.day,
                hour=0,
                minute=0,
                second=0,
            )
            games = games.filter(
                Game.creation_time > previous_day, Game.creation_time < next_day
            )
        return games.all()

    def get_last_session_id(self):
        return self.sessions[-1].id

    def start_a_new_session(self):
        new_session = GameSession(user_id=self.id)
        db.session.add(new_session)
        db.session.commit()
        return new_session


class GameSession(db.Model):
    @staticmethod
    def get_random_level():
        return random.choice(range(1, 6))

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    wallet = db.Column(db.Integer, default=10, nullable=False)
    games = db.relationship(
        "Game", backref="session", lazy=True, order_by="desc(Game.id)"
    )
    level = db.Column(db.Integer, default=get_random_level, nullable=False)
    preferred_sign = db.Column(db.String(2), default="", nullable=False)

    @property
    def is_active(self):
        # TODO add condition of existing open game
        if self.able_to_start_new_game() or [
            game for game in self.games if not game.result
        ]:
            return True
        return False

    def board_string(self):
        return f"Session {self.id} | wallet: {self.wallet} | games: {len(self.games)} | level: {self.level} | sign: {self.preferred_sign if self.preferred_sign else 'random'}"

    def able_to_start_new_game(self):
        if (
            self.games
            and Game.query.filter_by(session_id=self.id, result=None).all()
            or self.wallet < 3
        ):
            return False
        return True

    def start_a_new_game(self):
        if self.able_to_start_new_game():
            self.wallet -= 3
            game_data = {"session_id": self.id, "level": self.level}
            if self.preferred_sign:
                game_data.update({"player_sign": self.preferred_sign})
            new_game = Game(**game_data)
            db.session.add(new_game)
            db.session.commit()
            return new_game


class Game(db.Model):
    @staticmethod
    def random_sign():
        return random.choice(["X", "O"])

    @staticmethod
    def get_empty_board():
        return {x + str(y): None for x in "abc" for y in range(1, 4)}

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("game_session.id"), nullable=False)
    result = db.Column(db.String[10], default=None, nullable=True)
    player_sign = db.Column(db.String[2], default=random_sign, nullable=False)
    starting_sign = db.Column(db.String[2], default=random_sign, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    board = db.Column("board", MutableDict.as_mutable(JSON), default=get_empty_board)
    history = db.Column("history", MutableList.as_mutable(JSON), default=list)
    creation_time = db.Column(DateTime(timezone=True), server_default=func.now())
    start_time = db.Column(DateTime(timezone=True), default=None)
    finish_time = db.Column(DateTime(timezone=True), default=None)

    def __repr__(self):
        return f"Game('{self.id}', '{self.session_id}', '{self.result}', '{self.player_sign}', '{self.level}')"

    def board_string(self):
        return f"Game {self.id} | your sign: {self.player_sign} | starting player: {self.starting_player} | level: {self.level}"

    @property
    def time_elapsed(self):
        if not self.start_time or not self.finish_time:
            return None
        return self.finish_time - self.start_time

    @property
    def ai_sign(self):
        return "X" if self.player_sign == "O" else "O"

    @property
    def starting_player(self):
        return "player" if self.starting_sign == self.player_sign else "opponent"

    @property
    def whose_turn(self):
        if self.check_result():
            return "-"
        return "player" if self.able_to_make_a_move() else "opponent"

    @property
    def empty_fields(self):
        return [field for field in self.board.keys() if self.board[field] is None]

    def get_field(self, field):
        return f'{self.board[field] or "."}'

    def able_to_make_a_move(self):
        if (
            self.check_result()
            or self.player_sign == self.starting_sign
            and len(self.empty_fields) % 2 == 0
            or self.player_sign != self.starting_sign
            and len(self.empty_fields) % 2 == 1
        ):
            return False
        return True

    def check_if_sign_won(self, sign, board=None):
        if not board:
            board = self.board
        winning_sign = None
        # straight rows and columns check
        for char in "abc123":
            if (
                len([key for key in board.keys() if char in key and board[key] == sign])
                == 3
            ):
                winning_sign = sign
        # cross lines check:
        for fields in [["a1", "b2", "c3"], ["a3", "b2", "c1"]]:
            if len([key for key in fields if board[key] == sign]) == 3:
                winning_sign = sign

        return winning_sign

    def check_result(self):
        if self.result:
            return self.result

        winning_sign = None
        for sign in ["X", "O"]:
            if self.board:
                if winning_sign := self.check_if_sign_won(sign):
                    break

        if winning_sign:
            if winning_sign == self.player_sign:
                self.set_result("won")
            else:
                self.set_result("lost")

        elif None not in self.board.values():
            self.set_result("tied")
            return self.result

        return self.result

    def put_the_sign_on_the_field(self, field, sign, ai=False):
        if not self.start_time:
            self.start_time = func.now()
            db.session.commit()

        sign_put = False
        if sign == self.player_sign and not ai:
            if not self.able_to_make_a_move():
                return {
                    "sign_put": sign_put,
                    "continue": True if not self.result else False,
                }

        if not self.board[field]:
            self.board[field] = sign
            self.history.append({field: sign})
            db.session.commit()
            sign_put = True
        self.check_result()
        return {"sign_put": sign_put, "continue": True if not self.result else False}

    def make_move_as_ai(self):
        if self.result:
            return {
                "field": None,
                "sign": None,
                "continue": True if not self.result else False,
            }
        sign = "X" if self.player_sign == "O" else "O"
        field = None

        if self.level >= 4:
            # check for instant winning move
            if winning_move := self.check_if_there_is_winning_move(for_player=False):
                field = winning_move

        if self.level == 5 and not field:
            # check for instant winning move for player and block it
            if player_winning_move := self.check_if_there_is_winning_move(
                for_player=True
            ):
                field = player_winning_move

        if self.level >= 3 and not field:
            # put a sign in the middle
            if "b2" in self.empty_fields:
                field = "b2"

        if self.level >= 2 and not field:
            # put a sign in corner
            corners = [
                field
                for field in ["a1", "a3", "c1", "c3"]
                if field in self.empty_fields
            ]
            if corners:
                field = random.choice(corners)

        # make random move for level 1 or if nothing above is possible
        if not field:
            field = random.choice(self.empty_fields)

        self.put_the_sign_on_the_field(field, sign, ai=True)
        return {
            "field": field,
            "sign": sign,
            "continue": True if not self.result else False,
        }

    def set_result(self, result):
        self.result = result
        self.finish_time = func.now()
        if result == "won":
            GameSession.query.filter_by(id=self.session_id).one().wallet += 4
        db.session.commit()

    def check_if_there_is_winning_move(self, for_player=False):
        sign = self.player_sign if for_player else self.ai_sign
        for field in self.empty_fields:
            temp_board = self.board.copy()
            temp_board[field] = sign
            if self.check_if_sign_won(sign=sign, board=temp_board):
                return field
