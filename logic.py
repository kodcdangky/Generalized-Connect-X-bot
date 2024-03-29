from enum import Enum
from random import choice

# m, n, k generalized game
ROWS = 8
COLS = 8
CONNECT = 4
DEPTH = 4


class State(Enum):
    RED = 1
    YELLOW = -1
    TIED = 0
    UNFINISHED = 0

    def __neg__(self):
        if self == State.RED:
            return State.YELLOW
        elif self == State.YELLOW:
            return State.RED
        else:
            raise ValueError(
                f"Illegal negation of {__class__.__name__} enum: Negation of {self} is not allowed"
            )

    def __bool__(self):
        return self != State.UNFINISHED


class ConfigError(Exception):
    pass


def is_finished(state: list[list[State]], last_move: tuple[int, int]) -> State:
    """
    Check if game is finished
    Since a game can only end after a move, and a player can only win from the last move made, checking the entire board
    is not needed, instead checking only lines made with the last move is necessary

    Returns the corresponding State enum for the game state
    """
    def n_s():
        return (
            row in range(ROWS - CONNECT + 1)
            and len(set(state[row + i][col] for i in range(CONNECT))) == 1
        )

    def w_e():
        return any(
            (
                col + i in range(COLS - CONNECT + 1)
                and len(set(state[row][col + i:col + i + CONNECT])) == 1
            )
            for i in range(0, -CONNECT, -1)
        )

    def nw_se():
        return any(
            (
                row + i in range(ROWS - CONNECT + 1)
                and col + i in range(COLS - CONNECT + 1)
                and len(set(state[row + j][col + j] for j in range(i, i + CONNECT))) == 1
            )
            for i in range(0, -CONNECT, -1)
        )

    def sw_ne():
        return any(
            (
                row - i in range(CONNECT, ROWS)
                and col + i in range(COLS - CONNECT + 1)
                and len(set(state[row - j][col + j] for j in range(i, i + CONNECT))) == 1
            )
            for i in range(0, -CONNECT, -1)
        )

    row, col = last_move

    if any((n_s(), w_e(), nw_se(), sw_ne())):
        return state[row][col]

    # if no winner was found, check if all top row cells are filled, if not, game is not finished
    if State.UNFINISHED in state[0]:
        return State.UNFINISHED

    # all cells are filled and no winner was found, therefore game is drawn
    return State.TIED


def minimax_pruning(
    state: list[list[State]],
    depth: int,
    turn: State,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
) -> dict:
    """
    Depth-limited minimax with naive alpha-beta pruning

    All possible moves are added to a list along with their estimated/determined score.

    Afterwards, all the non-best options in the list are eliminated,
    then a move is chosen randomly among the ones remaining

    This ensures that when given a state that is commonly seen with multiple options that has the same score,
    e.g. the opening state, the bot doesn't make the same option every time
    """
    # return heuristic of state if it is the final depth
    if depth == 0:
        return {"score": _estimate_heuristic(state), "depth": 0}

    # save all possible options in a list
    options: list[dict[str, tuple[int, int] | float | int]] = []

    # get list of possible moves, then sort by manhattan distance from center
    possible_moves = _get_possible_moves(state)
    possible_moves.sort(
        key=lambda move: abs(move[0] - ROWS / 2) + abs(move[1] - COLS / 2)
    )

    # check each possible move
    for row, col in possible_moves:
        # assume child state, then check if child state is a finished state
        state[row][col] = turn
        finished = is_finished(state, (row, col))

        # if child state is finished state,
        # child state score is +infinity, or -infinity, depending on if winner is the maximizing player or not, respectively,
        # or 0 if child state is a draw
        if finished:
            option = {
                "move": (row, col),
                "score": 0 if finished == State.TIED else finished.value * float("inf"),
                "depth": depth - 1,
            }

        # if child state is not a finished state, recur
        else:
            option = minimax_pruning(state, depth - 1, -turn, alpha, beta)
            option["move"] = row, col

        # return to parent state, ready for next child state
        state[row][col] = State.UNFINISHED

        # add this move and its score to list of options
        options.append(option)

        # update alpha or beta depending on if it's the maximizing player's turn or not
        # alpha: maximizing player's lower bound
        # beta:  minimizing player's upper bound
        if turn == State.RED:
            alpha = max(alpha, option["score"])
        else:
            beta = min(beta, option["score"])
        if beta < alpha:
            break

    # Pick out the best score (minimizing or maximizing) for the current player
    best_score_func = max if turn == State.RED else min
    best_score = best_score_func(map(lambda option: option["score"], options))

    # if best score possible is a guaranteed loss, only choose among the longest paths (lowest depth)
    if best_score == (-turn).value * float("inf"):
        best_depth = min(map(lambda option: option["depth"], options))
        options = list(
            filter(lambda option: option["depth"] == best_depth, options)
        )

    # if best score possible is winnable, choose among the shortest paths (highest depth) to the best possible score
    else:
        best_options_by_score = tuple(
            filter(lambda option: option["score"] == best_score, options)
        )
        best_depth = max(
            map(lambda option: option["depth"], best_options_by_score)
        )
        options = list(
            filter(
                lambda option: option["depth"] == best_depth,
                best_options_by_score
            )
        )

    # select a random move from the remaining options and return
    return choice(options)


def _get_possible_moves(state: list[list[State]]) -> list[tuple[int, int]]:
    possible_moves = []
    for col in range(COLS):
        for row in reversed(range(ROWS)):
            if not state[row][col]:
                possible_moves.append((row, col))
                break
    return possible_moves


def _estimate_heuristic(state: list[list[State]]) -> float:
    """
    Estimate heuristic of a game state based on the difference between how many lines are 1 away from completing for both sides

    Returns the sum of positive and negative player's heuristics
    """

    # at first, the heuristics for both players is 0
    heuristic = {State.RED: 0.0, State.YELLOW: 0.0}

    # go through each column, from bottom to top
    for col in range(COLS):
        empty_in_col = 0

        for row in reversed(range(ROWS)):
            # check each empty cell to see if it's a candidate for winning for any players
            if not state[row][col]:
                cell_fits = 0
                empty_in_col += 1

                for player in (State.YELLOW, State.RED):
                    state[row][col] = player

                    # if cell is a candidate for winning for either player, that player's heuristic is updated by
                    # the player's value (-1 or 1) times (1 / lowest number of plies to reach that cell)
                    if is_finished(state, (row, col)) == player:
                        heuristic[player] += player.value / empty_in_col
                        cell_fits += 1

                    state[row][col] = State.UNFINISHED

                # if cell is a candidate for winning for both players, higher cells in the column won't be further
                # investigated as they can never be reached
                if cell_fits == 2:
                    break

    # players' heuristics have opposite signs, so their sum is returned
    return heuristic[State.RED] + heuristic[State.YELLOW]
