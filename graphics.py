from time import perf_counter, sleep

import pygame as pg

from logic import ROWS, COLS, CONNECT, DEPTH, minimax_pruning, is_finished, ConfigError, State

FPS = 30
WHITE = (170, 170, 170)
BLACK = (0, 0, 0)
RED = (173, 19, 19)
YELLOW = (174, 174, 0)
ASPECT_RATIO = (4, 3)
FONT = "Candara"


def main():
    # Check for invalid configurations
    if any(not isinstance(t, int) for t in (ROWS, COLS, CONNECT)):
        raise TypeError("Configuration constants have incorrect types")

    elif any(v < 1 for v in (ROWS, COLS, CONNECT)):
        raise ValueError("Configuration constants have incorrect values")

    elif CONNECT > ROWS and CONNECT > COLS:
        raise ConfigError("CONNECT is longer than both ROWS and COLS")

    # Initialize pygame stuff
    pg.init()
    window_width = pg.display.Info().current_w * 3 // 5
    window_height = window_width * ASPECT_RATIO[1] // ASPECT_RATIO[0]
    window = pg.display.set_mode((window_width, window_height))
    pg.display.set_caption(f"{ROWS}x{COLS} Connect {CONNECT}")

    clock = pg.time.Clock()

    menu_font_size = window_width // 6

    # default option
    player = State.RED

    menu_active = True
    game_active = False
    window_active = True

    bground = pg.Surface((window.get_width() / 10 * 9, window.get_height()))
    bground_rect = bground.get_rect(
        centerx=window.get_width() / 2, centery=window.get_height() / 2
    )

    while window_active:
        if menu_active:
            # Background
            font = pg.font.SysFont(FONT, menu_font_size)
            bground.fill(WHITE)

            # Prompt for going first
            first_prompt = font.render("Go first?", True, BLACK)
            first_prompt_rect = first_prompt.get_rect(
                centerx=bground.get_width() / 2, centery=bground.get_height() / 5
            )

            # Yes/No option
            yes = font.render("Yes", True, BLACK)
            yes_rect = yes.get_rect(
                centerx=bground.get_width() / 4, centery=bground.get_height() / 5 * 3
            )

            no = font.render("No", True, BLACK)
            no_rect = no.get_rect(
                centerx=bground.get_width() / 4 * 3, centery=bground.get_height() / 5 * 3
            )

            # Initial cursor
            cursor = font.render("^", True, BLACK)
            cursor_yes_rect = cursor.get_rect(
                centerx=bground.get_width() / 4, top=yes_rect.bottom  # + (yes.get_height() / 10)
            )
            cursor_no_rect = cursor.get_rect(
                centerx=bground.get_width() / 4 * 3, top=no_rect.bottom  # + (no.get_height() / 10)
            )

            # Draw text on background, then background on window
            bground.blit(first_prompt, first_prompt_rect)
            bground.blit(yes, yes_rect)
            bground.blit(no, no_rect)
            bground.blit(cursor, cursor_yes_rect)
            window.blit(bground, bground_rect)
            pg.display.update()

            # Prep cursor eraser
            eraser = pg.Surface(cursor.get_size())
            eraser.fill(WHITE)

            while menu_active:
                clock.tick(FPS)
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        menu_active = False
                        break
                    if event.type == pg.KEYUP:
                        match event.key:
                            case pg.K_RIGHT:  # Moving from Yes to No
                                # Can setup some sound here later
                                if player == State.RED:
                                    # change player
                                    player = -player

                                    # move cursor
                                    bground.blit(eraser, cursor_yes_rect)
                                    bground.blit(cursor, cursor_no_rect)
                            case pg.K_LEFT:
                                # Sound?
                                if player == State.YELLOW:  # Moving from No to Yes
                                    # change player
                                    player = -player

                                    # move cursor
                                    bground.blit(eraser, cursor_no_rect)
                                    bground.blit(cursor, cursor_yes_rect)
                            case pg.K_RETURN:
                                menu_active = False
                                game_active = True
                                break
                            case pg.K_ESCAPE:
                                menu_active = False
                                window_active = False
                                break
                window.blit(bground, bground_rect)
                pg.display.update()

        if game_active:
            # set initial turn, initial cursor choice and game state
            turn = State.RED
            choice = 0
            finished = State.UNFINISHED
            state: list[list[State]] = [
                [State.UNFINISHED for _ in range(COLS)] for _ in range(ROWS)
            ]

            # draw initial board
            board_side = bground.get_height() * 3 / 4
            board = pg.Surface((board_side + 2, board_side + 2))
            board.fill(WHITE)
            board_rect = board.get_rect(topleft=(0, 0))
            for row in range(ROWS):
                pg.draw.line(
                    board,
                    BLACK,
                    (0, board_side / ROWS * (row + 1)),
                    (board_side, board_side / ROWS * (row + 1)),
                    3,
                )
            for col in range(COLS):
                pg.draw.line(
                    board,
                    BLACK,
                    (board_side / COLS * (col + 1), 0),
                    (board_side / COLS * (col + 1), board_side),
                    3,
                )

            # Thickens horizontal outer border
            pg.draw.line(board, BLACK, (0, board.get_height()),
                         (board.get_width(), board.get_height()), 3)
            pg.draw.line(board, BLACK, (0, 0), (board.get_width(), 0), 3)

            # Thickens vertical outer border
            pg.draw.line(board, BLACK, (board.get_width(), 0),
                         (board.get_width(), board.get_height()), 3)
            pg.draw.line(board, BLACK, (0, 0), (0, board.get_height()), 3)

            bground.fill(WHITE)
            bground.blit(board, board_rect)

            font = pg.font.SysFont(FONT, int(menu_font_size / 1.8))
            # draw initial cursor position
            cursor = font.render("^", True, BLACK)
            cursor_rect = cursor.get_rect(
                midtop=(board_side / ROWS / 2, board.get_height() + 10)
            )
            bground.blit(cursor, cursor_rect)

            window.blit(bground, bground_rect)
            pg.display.update()

            status = pg.Surface(
                (bground.get_width() - board.get_width(), board.get_height())
            )
            status_rect = status.get_rect(
                centerx=(bground.get_width() + board.get_width()) / 2,
                centery=board.get_height() / 2,
            )

            while game_active:
                clock.tick(FPS)

                # delete old status message
                eraser = pg.Surface(status.get_size())
                eraser.fill(WHITE)
                bground.blit(eraser, status_rect)

                if not finished:
                    # update status to indicate whose turn is it
                    status = _wrapped_text(
                        "Your turn" if turn == player else "Thinking ...",
                        font,
                        WHITE,
                        BLACK,
                        bground.get_width() - board.get_width() - 10,
                    )
                else:
                    # update status to indicate game has ended and show result
                    status = _wrapped_text(
                        "Draw" if finished == State.TIED else "You win!" if finished == player else "Bot wins!",
                        font,
                        WHITE,
                        BLACK if finished == State.TIED else RED if finished == State.RED else YELLOW,
                        bground.get_width() - board.get_width() - 10,
                    )

                    eraser = pg.Surface(cursor.get_size())
                    eraser.fill(WHITE)
                    bground.blit(eraser, cursor_rect)

                    rematch_prompt = _wrapped_text(
                        "Press Esc to quit, or any key to rematch",
                        pg.font.SysFont(FONT, int(menu_font_size / 2.2)),
                        WHITE,
                        BLACK,
                        bground.get_width()
                    )
                    rematch_prompt_rect = rematch_prompt.get_rect(
                        centerx=bground.get_width() / 2,
                        centery=(bground.get_height() + board.get_height()) / 2
                    )
                    bground.blit(rematch_prompt, rematch_prompt_rect)

                status_rect = status.get_rect(
                    centerx=(bground.get_width() + board.get_width()) / 2,
                    centery=board.get_height() / 2,
                )
                bground.blit(status, status_rect)
                window.blit(bground, bground_rect)
                pg.display.update()

                if finished:
                    # if game has ended, any clicks will close game
                    while game_active:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                game_active = False
                                window_active = False
                            if event.type == pg.KEYUP:
                                match event.key:
                                    case pg.K_ESCAPE:
                                        game_active = False
                                        window_active = False
                                    case _:
                                        game_active = False
                                        menu_active = True

                if not game_active:
                    break

                # bot's turn
                if turn != player:
                    # Update game state
                    before = perf_counter()
                    row, col = minimax_pruning(state, DEPTH, turn)["move"]
                    state[row][col] = turn
                    turn = player

                    # Draw bot's cell
                    cell = pg.Surface(
                        (board_side / COLS - 3, board_side / ROWS - 3)
                    )
                    cell.fill(RED if player == State.YELLOW else YELLOW)
                    cell_rect = cell.get_rect(
                        centerx=board_side / COLS * (col + 0.5),
                        centery=board_side / ROWS * (row + 0.5),
                    )
                    board.blit(cell, cell_rect)
                    bground.blit(board, board_rect)

                    # Bot's turn last a minimum of 0.5s
                    time_spent = perf_counter() - before
                    if time_spent < 0.5:
                        sleep(0.5 - time_spent)

                    finished = is_finished(state, (row, col))

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        game_active = False
                        break
                    if event.type == pg.KEYUP:
                        match event.key:
                            case pg.K_LEFT:
                                if choice > 0:
                                    # change column choice
                                    choice -= 1

                                    # move cursor
                                    eraser = pg.Surface(cursor.get_size())
                                    eraser.fill(WHITE)
                                    bground.blit(eraser, cursor_rect)

                                    cursor_rect = cursor.get_rect(
                                        centerx=board.get_width() / COLS * (choice + 0.5),
                                        top=board.get_height() + 10,
                                    )
                                    bground.blit(cursor, cursor_rect)
                            case pg.K_RIGHT:
                                if choice < COLS - 1:
                                    # change column choice
                                    choice += 1

                                    # move cursor
                                    eraser = pg.Surface(cursor.get_size())
                                    eraser.fill(WHITE)
                                    bground.blit(eraser, cursor_rect)

                                    cursor_rect = cursor.get_rect(
                                        centerx=board.get_width() / COLS * (choice + 0.5),
                                        top=board.get_height() + 10,
                                    )
                                    bground.blit(cursor, cursor_rect)
                            case pg.K_RETURN:
                                # Register player's choice only during player's turn
                                if turn == player:
                                    for row in reversed(range(ROWS)):
                                        if not state[row][choice]:
                                            # Update game state
                                            state[row][choice] = player
                                            turn = -turn

                                            # Draw player's cell
                                            cell = pg.Surface(
                                                (board_side / COLS - 3,
                                                    board_side / ROWS - 3)
                                            )
                                            cell.fill(RED if player == State.RED
                                                      else YELLOW)
                                            cell_rect = cell.get_rect(
                                                center=(board_side / COLS * (choice + 0.5),
                                                        board_side / ROWS * (row + 0.5))
                                            )
                                            board.blit(cell, cell_rect)
                                            bground.blit(board, board_rect)

                                            # check if game over
                                            finished = is_finished(
                                                state, (row, choice))
                                            break
                            case pg.K_ESCAPE:
                                game_active = False
                                window_active = False
                                break

                window.blit(bground, bground_rect)
                pg.display.update()

    pg.quit()


def _wrapped_text(
    text: str,
    font: pg.font.Font,
    bground_color: tuple[int, int, int],
    text_color: tuple[int, int, int],
    allowed_width: int,
) -> pg.Surface:
    """Returns a surface which contains wrapped text, ready to be blit-ed on other surfaces"""
    words = text.split()
    words.reverse()

    lines: list[str] = []
    while words:
        line = []
        while words:
            line.append(words.pop())
            line_width, _ = font.size(" ".join(line + words[-1:]))
            if line_width > allowed_width:
                break
        lines.append(" ".join(line))

    surface_width = surface_height = 0
    for line in lines:
        line_width, line_height = font.size(line)
        surface_width = max(surface_width, line_width)
        surface_height += line_height

    surface = pg.Surface((surface_width, surface_height))
    surface.fill(bground_color)
    line_top = 0
    for line in lines:
        line_surface = font.render(line, True, text_color, bground_color)
        line_rect = line_surface.get_rect(midtop=(surface_width / 2, line_top))
        surface.blit(line_surface, line_rect)

        line_top += font.get_linesize()

    return surface


if __name__ == "__main__":
    main()
