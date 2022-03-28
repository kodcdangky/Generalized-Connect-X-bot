from time import sleep

from basics import get_rows, get_columns, get_connection, get_depth, minimax_pruning, clean, is_finished, ConfigurationError

ROWS = get_rows()
COLS = get_columns()
CONNECT = get_connection()
DEPTH = get_depth()


def get_player_turn() -> int:
    while True:
        player = input('Are you playing as red or yellow? Red goes first\n'
                       '(Typing "r" or "y" is sufficient): ').lower()
        match player:
            case 'r' | 'red':
                return 1
            case 'y' | 'yellow':
                return -1


def get_player_move(state: list) -> int:
    while True:
        try:
            move = int(input(f'Choose between 1-{COLS} corresponding to the column you want to drop into: '))
            if move in range(1, COLS + 1) and state[0][move - 1] is None:
                return move
        except ValueError:
            pass


def play():
    # Check for invalid configurations
    if any(t is not int for t in (type(ROWS), type(COLS), type(CONNECT))):
        raise TypeError('Configuration constants have incorrect types')

    elif any(v < 1 for v in (ROWS, COLS, CONNECT)):
        raise ValueError('Configuration constants have incorrect values')

    elif CONNECT > ROWS and CONNECT > COLS:
        raise ConfigurationError('CONNECT is longer than both ROWS and COLS')

    while True:
        try:
            player = get_player_turn()
            print('For clarity, Red uses x for sprites, and Yellow uses o for sprites')
            sleep(3)
            print('--- NEW GAME ---')
            print()

            turn = 1
            state = [[None for _ in range(COLS)] for _ in range(ROWS)]
            print(clean(state))
            while True:
                if turn == player:
                    col = get_player_move(state) - 1
                    for row in reversed(range(ROWS)):
                        if state[row][col] is None:
                            move = row, col
                            state[row][col] = turn
                            break
                else:
                    option = minimax_pruning(state, DEPTH, turn)
                    move = option['move']
                    state[move[0]][move[1]] = turn

                print(f'{clean(state)}\n')

                finished = is_finished(state, turn, move)
                if finished is not False:
                    match finished:
                        case -1:
                            print('Yellow wins!\n')
                        case 1:
                            print('Red wins!\n')
                        case 0:
                            print('Draw')
                    break
                turn = -turn

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    play()
