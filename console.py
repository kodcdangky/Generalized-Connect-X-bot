from time import sleep, perf_counter

from logic import ROWS, COLS, CONNECT, DEPTH, minimax_pruning, is_finished, ConfigError, State


def play():
    # Check for invalid configurations
    if any(not isinstance(t, int) for t in (ROWS, COLS, CONNECT)):
        raise TypeError("Configuration constants have incorrect types")

    elif any(v < 1 for v in (ROWS, COLS, CONNECT)):
        raise ValueError("Configuration constants have incorrect values")

    elif CONNECT > ROWS and CONNECT > COLS:
        raise ConfigError("CONNECT is longer than both ROWS and COLS")

    while True:
        try:
            player = _get_player_turn()
            print("For clarity, Red uses x for sprites, and Yellow uses o for sprites")
            sleep(3)
            print("--- NEW GAME ---")
            print()

            turn = State.RED
            state: list[list[State]] = [
                [State.UNFINISHED for _ in range(COLS)] for _ in range(ROWS)
            ]
            print(_clean(state))
            while True:
                if turn == player:
                    row, col = _get_player_move(state)
                    state[row][col] = turn
                else:
                    before = perf_counter()
                    option = minimax_pruning(state, DEPTH, turn)
                    row, col = option["move"]
                    state[row][col] = turn
                    spent = perf_counter() - before
                    if spent < 0.5:
                        sleep(0.5 - spent)

                print(f"{_clean(state)}\n")

                finished = is_finished(state, (row, col))
                if finished:
                    match finished:
                        case State.YELLOW:
                            print("Yellow wins!\n")
                        case State.RED:
                            print("Red wins!\n")
                        case State.TIED:
                            print("Draw")
                    break
                turn = -turn

        except KeyboardInterrupt:
            break


def _get_player_turn() -> State:
    while True:
        player = input(
            "Are you playing as red(r) or yellow(y)? Red goes first: "
        ).strip().lower()
        match player:
            case "r" | "red":
                return State.RED
            case "y" | "yellow":
                return State.YELLOW


def _get_player_move(state: list[list[State]]) -> tuple[int, int]:
    while True:
        try:
            move = int(
                input(
                    f"Choose between 1-{COLS} corresponding to the column you want to drop into: "
                )
            ) - 1
            if move in range(COLS) and not state[0][move]:
                for row in reversed(range(ROWS)):
                    if not state[row][move]:
                        return row, move
        except ValueError:
            pass


def _clean(state: list[list[State]]) -> str:
    """
    Returns a console renderred version of the game ready to be printed
    """
    to_be_printed = ""
    for row in range(ROWS):
        to_be_printed += "|"
        for col in range(COLS):
            match state[row][col]:
                case State.YELLOW:
                    to_be_printed += " o "
                case State.RED:
                    to_be_printed += " x "
                case State.TIED:
                    to_be_printed += "   "
            to_be_printed += "|"
        to_be_printed += "\n"
    to_be_printed += "  "
    for col in range(COLS):
        to_be_printed += f"{col + 1}   "
    return to_be_printed


if __name__ == "__main__":
    play()
