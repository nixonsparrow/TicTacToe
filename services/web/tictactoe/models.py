import random

from flask_login import UserMixin
from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableDict, MutableList

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

    def get_last_session_id(self):
        return self.sessions[-1].id

    def start_a_new_session(self):
        new_session = GameSession(user_id=self.id)
        db.session.add(new_session)
        db.session.commit()
        return new_session


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
    board = db.Column("board", MutableDict.as_mutable(JSON), default=get_empty_board)
    history = db.Column("history", MutableList.as_mutable(JSON), default=list)

    def __repr__(self):
        return f"Game('{self.id}', '{self.session_id}', '{self.result}', '{self.player_sign}')"

    def board_string(self):
        return f"Game {self.id} | your sign: {self.player_sign} | starting player: {self.starting_player}"

    @property
    def starting_player(self):
        return "player" if self.starting_sign == self.player_sign else "opponent"

    @property
    def whose_turn(self):
        if self.check_result():
            return "-"
        return "player" if self.able_to_make_a_move() else "opponent"

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

    def check_result(self):
        if self.result:
            return self.result

        winning_sign = None
        for sign in ["X", "O"]:
            if self.board:
                # straight rows and columns check
                for char in "abc123":
                    if (
                        len(
                            [
                                key
                                for key in self.board.keys()
                                if char in key and self.board[key] == sign
                            ]
                        )
                        == 3
                    ):
                        winning_sign = sign
                # cross lines check:
                for fields in [["a1", "b2", "c3"], ["a3", "b2", "c1"]]:
                    if len([key for key in fields if self.board[key] == sign]) == 3:
                        winning_sign = sign

        if winning_sign:
            if winning_sign == self.player_sign:
                self.result = "won"
                GameSession.query.filter_by(id=self.session_id).one().wallet += 4
            else:
                self.result = "lost"
            db.session.commit()

        elif None not in self.board.values():
            self.result = "tied"
            db.session.commit()
            return self.result

        return self.result

    def put_the_sign_on_the_field(self, field, sign, ai=False):
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

    def make_move_as_ai(self, level=1):
        if self.result:
            return {
                "field": None,
                "sign": None,
                "continue": True if not self.result else False,
            }
        sign = "X" if self.player_sign == "O" else "O"
        if level == 1:
            field = random.choice(self.empty_fields)
            self.put_the_sign_on_the_field(field, sign, ai=True)
            return {
                "field": field,
                "sign": sign,
                "continue": True if not self.result else False,
            }

    @property
    def empty_fields(self):
        return [field for field in self.board.keys() if self.board[field] is None]


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    wallet = db.Column(db.Integer, default=10, nullable=False)
    games = db.relationship(
        "Game", backref="session", lazy=True, order_by="desc(Game.id)"
    )

    def board_string(self):
        return f"Session {self.id} | wallet: {self.wallet} | games: {len(self.games)}"

    def able_to_start_new_game(self):
        if (
            self.games
            and Game.query.filter_by(session_id=self.id, result=None).all()
            or self.wallet < 3
        ):
            # TODO change to False if not
            return False
        return True

    def start_a_new_game(self):
        if self.able_to_start_new_game():
            self.wallet -= 3
            new_game = Game(session_id=self.id)
            db.session.add(new_game)
            db.session.commit()
            return new_game
