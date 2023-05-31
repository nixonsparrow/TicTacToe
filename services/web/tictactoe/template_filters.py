def get_game_time(all_games, quickest=True):
    games = [game for game in all_games if game.time_elapsed]
    if games:
        if quickest:
            return min(games, key=lambda game: game.time_elapsed).time_elapsed
        return max(games, key=lambda game: game.time_elapsed).time_elapsed
    return ""


jinja_filters = [get_game_time]
