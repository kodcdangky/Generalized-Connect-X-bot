from time import sleep, perf_counter

from logic import (
    ROWS,
    COLS,
    CONNECT,
    DEPTH,
    minimax_pruning,
    is_finished,
    ConfigurationError,
)


def play():
    # Check for invalid configurations
    if any(not isinstance(t, int) for t in (ROWS, COLS, CONNECT)):
        raise TypeError("Configuration constants have incorrect types")

    elif any(v < 1 for v in (ROWS, COLS, CONNECT)):
        raise ValueError("Configuration constants have incorrect values")

    elif CONNECT > ROWS and CONNECT > COLS:
        raise ConfigurationError("CONNECT is longer than both ROWS and COLS")

    while True:
        try:
            player = _get_player_turn()
            print("For clarity, Red uses x for sprites, and Yellow uses o for sprites")
            sleep(3)
            print("--- NEW GAME ---")
            print()

            turn = 1
            state: list[list[int | None]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
            print(_clean(state))
            while True:
                if turn == player:
                    col = _get_player_move(state) - 1
                    for row in reversed(range(ROWS)):
                        if state[row][col] is None:
                            move = row, col
                            state[row][col] = turn
                            break
                else:
                    before = perf_counter()
                    option = minimax_pruning(state, DEPTH, turn)
                    move = option["move"]
                    state[move[0]][move[1]] = turn
                    spent = perf_counter() - before
                    if spent < 0.5:
                        sleep(0.5 - spent)

                print(f"{_clean(state)}\n")

                finished = is_finished(state, move)
                if finished is not False:
                    match finished:
                        case -1:
                            print("Yellow wins!\n")
                        case 1:
                            print("Red wins!\n")
                        case 0:
                            print("Draw")
                    break
                turn = -turn

        except KeyboardInterrupt:
            break


def _get_player_turn() -> int:
    while True:
        player = input(
            "Are you playing as red or yellow? Red goes first\n"
            '(Typing "r" or "y" is sufficient): '
        ).lower()
        match player:
            case "r" | "red":
                return 1
            case "y" | "yellow":
                return -1


def _get_player_move(state: list) -> int:
    while True:
        try:
            move = int(
                input(
                    f"Choose between 1-{COLS} corresponding to the column you want to drop into: "
                )
            )
            if move in range(1, COLS + 1) and state[0][move - 1] is None:
                return move
        except ValueError:
            pass


def _clean(state: list[list[int | None]]) -> str:
    """
    :param state: Current game state
    :return: A console renderred version of the game ready to be printed
    """

    to_be_printed = ""
    for row in range(ROWS):
        to_be_printed += "|"
        for col in range(COLS):
            match state[row][col]:
                case -1:
                    to_be_printed += " o "
                case 1:
                    to_be_printed += " x "
                case None:
                    to_be_printed += "   "
            to_be_printed += "|"
        to_be_printed += "\n"
    to_be_printed += "  "
    for col in range(COLS):
        to_be_printed += f"{col + 1}   "
    return to_be_printed


if __name__ == "__main__":
    play()
