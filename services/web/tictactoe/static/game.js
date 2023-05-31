const socket = io({autoConnect: true});

function fieldClicked(game_id, field) {
    socket.emit("click_field", {"game_id": game_id, "field": field});
}

function startTheGame(game_id) {
    socket.emit("start_the_game", {"game_id": game_id});
    let start_button = document.getElementById("start_button");
    start_button.classList.add("hide");
}

socket.on("fill_field", function(data) {
    let field = document.getElementById(data["field"]);
    let whose_turn = document.getElementById("whose_turn");
    field.innerHTML = data["sign"]
    whose_turn.innerHTML = data["turn"]
})
socket.on("please_wait", function(data) {
    alert("Please wait for opponent to move.")
})
socket.on("move_incorrect", function(data) {
    alert("That move is not valid.")
})
socket.on("game_finished", function(data) {
    alert("Game has been " + data["result"] + ".")
})