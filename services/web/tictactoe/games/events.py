from time import sleep

from tictactoe.models import Game

from .. import socketio


@socketio.on("start_the_game")
def start_the_game(data):
    game = Game.query.filter_by(id=data["game_id"]).one()
    ai_move = game.make_move_as_ai()
    socketio.emit(
        "fill_field",
        {"field": ai_move["field"], "sign": ai_move["sign"], "turn": game.whose_turn},
    )


@socketio.on("click_field")
def click_field(data):
    field = data["field"]
    game_id = data["game_id"]
    game = Game.query.filter_by(id=game_id).one()
    if game.result:
        socketio.emit("game_finished", {"result": game.result})
        return
    elif game.board[field]:
        socketio.emit("move_incorrect")
        return
    elif not game.able_to_make_a_move():
        socketio.emit("please_wait")
        return

    move_data = game.put_the_sign_on_the_field(field, game.player_sign)
    if move_data["sign_put"]:
        socketio.emit(
            "fill_field",
            {"field": data["field"], "sign": game.player_sign, "turn": game.whose_turn},
        )
        if move_data["continue"]:
            ai_move = game.make_move_as_ai()
            socketio.emit(
                "fill_field",
                {
                    "field": ai_move["field"],
                    "sign": ai_move["sign"],
                    "turn": game.whose_turn,
                },
            )
            if not ai_move["continue"]:
                socketio.emit("game_finished", {"result": game.result})
        else:
            socketio.emit("game_finished", {"result": game.result})

    elif move_data["continue"]:
        socketio.emit("move_incorrect")

    else:
        if game.result:
            socketio.emit("game_finished", {"result": game.result})
