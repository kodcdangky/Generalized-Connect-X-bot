from random import choice

# m, n, k generalized game
ROWS = 8
COLS = 8
CONNECT = 4
DEPTH = 4


class ConfigurationError(Exception):
    pass


def _get_possible_moves(state: list) -> list:
    possible_moves = []
    for col in range(COLS):
        for row in reversed(range(ROWS)):
            if state[row][col] is None:
                possible_moves.append((row, col))
                break
    return possible_moves
get_possible_moves = _get_possible_moves


def _is_finished(state: list, last_turn: int, last_move: tuple[int, int]) -> int | bool:
    """
    Check if game is finished
    Since a game can only end after a move, and a player can only win from the last move made, checking the entire board
    is not needed, instead checking only lines made with the last move is necessary

    :param state: current state of the game
    :param last_turn: last player's turn
    :param last_move: (row, col) of last move
    :return: -1 or 1 for winner, 0 if tied, False if game isn't finished
    """
    def n_s():
        if row >= ROWS - CONNECT + 1:
            return False
        # return all(state[row][col] == state[row + i][col] for i in range(1, CONNECT))
        for i in range(1, CONNECT):
            if state[row][col] != state[row + i][col]:
                return False
        return True

    def w_e():
        for i in range(0, -CONNECT, -1):
            if col + i in range(COLS - CONNECT + 1):
                # if all(state[row][col + i] == state[row][col + j] for j in range(i + 1, i + CONNECT)):
                #     return True
                for j in range(i + 1, i + CONNECT):
                    if state[row][col + i] != state[row][col + j]:
                        break
                else:
                    return True
        return False

    def nw_se():
        for i in range(0, -CONNECT, -1):
            if col + i in range(COLS - CONNECT + 1) and row + i in range(ROWS - CONNECT + 1):
                # if all(state[row + i][col + i] == state[row + j][col + j] for j in range(i + 1, i + CONNECT)):
                #     return True
                for j in range(i + 1, i + CONNECT):
                    if state[row + i][col + i] != state[row + j][col + j]:
                        break
                else:
                    return True
        return False

    def sw_ne():
        for i in range(0, -CONNECT, -1):
            if col + i in range(COLS - CONNECT + 1) and row - i in range(CONNECT, ROWS):
                # if all(state[row - i][col + i] == state[row - j][col + j] for j in range(i + 1, i + CONNECT)):
                #     return True
                for j in range(i + 1, i + CONNECT):
                    if state[row - i][col + i] != state[row - j][col + j]:
                        break
                else:
                    return True
        return False

    row, col = last_move

    if n_s() or w_e() or nw_se() or sw_ne():
        return last_turn

    # if no winner was found, check if all cells are filled, if not, game is not finished
    for row in range(ROWS):
        if None in state[row]:
            return False

    # all cells are filled and no winner was found, therefore game is drawn
    return 2
is_finished = _is_finished


def _estimate_heuristic(state: list) -> int:
    """
    Estimate heuristic of a state based on the difference between how many lines are 1 away from completing for both sides

    :param state: current state of the game
    :return: sum of positive and negative player's heuristics
    """

    # at first, the heuristics for both players is 0
    heuristic = {-1: 0, 1: 0}

    # go through each column, from bottom to top
    for col in range(COLS):
        empty_in_col = 0

        for row in reversed(range(ROWS)):
            # check each empty cell to see if it's a candidate for winning for any players
            if state[row][col] is None:
                cell_fits = 0
                empty_in_col += 1

                for player in (-1, 1):
                    state[row][col] = player

                    # if cell is a candidate for winning for either player, that player's heuristic is updated by
                    # the player's id (-1 or 1) times (1 / lowest number of plies to reach that cell)
                    if is_finished(state, player, (row, col)) == player:
                        heuristic[player] += player / empty_in_col
                        cell_fits += 1

                    state[row][col] = None

                # if cell is a candidate for winning for both players, higher cells in the column won't be further
                # investigated as they can never be reached
                if cell_fits == 2:
                    break

    # players' heuristics have opposite signs, so their sum is returned
    return heuristic[-1] + heuristic[1]
estimate_heuristic = _estimate_heuristic


def _minimax_pruning(state: list, depth: int, turn: int, alpha: float = float('-inf'), beta: float = float('inf')) -> dict:
    """
    Depth-limited minimax with naive alpha-beta pruning

    All possible moves are added to a list along with their estimated/determined score.

    The list is then sorted in descending/ascending order by the scores based on whether it's the maximizing player or not,
    respectively.

    Afterwards, all the non-best options in the list are eliminated,
    then a move is chosen randomly among the ones remaining

    This ensures that when given a state that is commonly seen with multiple options that has the same score,
    e.g. the opening state, the bot doesn't make the same option every time
    """
    # return heuristic of state if it is the final depth
    if depth == 0:
        return {'score': estimate_heuristic(state), 'depth': 0}

    # save all possible moves in a list
    sorted_options = []

    # get list of possible moves, then sort by manhattan distance from center
    possible_moves = get_possible_moves(state)
    possible_moves.sort(key=lambda possible_move: abs(possible_move[0] - COLS / 2) + abs(possible_move[1] - ROWS / 2))

    # check each possible move
    for possible_move in possible_moves:
        # assume child state, then check if child state is a finished state
        state[possible_move[0]][possible_move[1]] = turn
        finished = is_finished(state, turn, possible_move)

        # if child state is finished state,
        # child state score is +infinity, or -infinity, depending on if winner is the maximizing player or not, respectively
        # or 0 if child state is a draw
        if finished is not False:
            option = {'move': possible_move, 'score': 0 if finished == 0 else finished * float('inf'), 'depth': depth - 1}

        # if child state is not a finished state, recur
        else:
            option = _minimax_pruning(state, depth - 1, -turn, alpha, beta)
            option['move'] = possible_move

        # return to parent state, ready for next child state
        state[possible_move[0]][possible_move[1]] = None

        # add this move and its score to list of options
        sorted_options.append(option)

        # update alpha or beta depending on if it's the maximizing player's turn or not
        # alpha: maximizing player's lower bound
        # beta:  minimizing player's upper bound
        if turn == 1:
            alpha = max(alpha, option['score'])
        else:
            beta = min(beta, option['score'])
        if beta < alpha:
            break

    # if it's the maximizing player, sort list of options in descending order by score, or vice versa
    sorted_options.sort(key=lambda option: option['score'], reverse=True if turn == 1 else False)

    best_score = sorted_options[0]['score']

    # if best score possible is a guaranteed loss, only choose among the longest paths (lowest depth)
    if best_score == -turn * float('inf'):
        # sort list of options by depth in ascending order
        sorted_options.sort(key=lambda option: option['depth'])

        # trim off all non-best options length-wise, if best path is not already the shortest path (highest depth)
        best_depth = sorted_options[0]['depth']
        if best_depth != DEPTH:
            for index, option in enumerate(sorted_options[1:]):
                if option['depth'] != best_depth:
                    sorted_options = sorted_options[:index + 1]
                    break

    # if best score possible is winnable, choose among the shortest paths (highest depth) to the best possible score
    else:
        # trim off all the non-best options score-wise
        for index, option in enumerate(sorted_options[1:]):
            if option['score'] != best_score:
                sorted_options = sorted_options[:index + 1]
                break

        # sort remaining list of options by depth in descending order
        sorted_options.sort(key=lambda option: option['depth'], reverse=True)

        # trim off all non-best options length-wise, if best path is not already the longest path (lowest depth)
        best_depth = sorted_options[0]['depth']
        if best_depth != 0:
            for index, option in enumerate(sorted_options[1:]):
                if option['depth'] != best_depth:
                    sorted_options = sorted_options[:index + 1]
                    break

    # select a random move from the remaining options and return
    move = choice(sorted_options)
    return move
minimax_pruning = _minimax_pruning


def _clean(state: list) -> str:
    """
    :param state: Current game state
    :return: A console renderred version of the game ready to be printed
    """

    to_be_printed = ''
    for row in range(ROWS):
        to_be_printed += '|'
        for col in range(COLS):
            match state[row][col]:
                case -1:
                    to_be_printed += ' o '
                case 1:
                    to_be_printed += ' x '
                case None:
                    to_be_printed += '   '
            to_be_printed += '|'
        to_be_printed += '\n'
    to_be_printed += '  '
    for col in range(COLS):
        to_be_printed += f'{col + 1}   '
    return to_be_printed
clean = _clean


def _get_rows():
    return ROWS
get_rows = _get_rows


def _get_columns():
    return COLS
get_columns = _get_columns


def _get_connection():
    return CONNECT
get_connection = _get_connection

def _get_depth():
    return DEPTH
get_depth = _get_depth
