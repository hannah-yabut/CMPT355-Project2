from typing import List, Tuple

from move import Move, create_move, move_is_removal
''' 
Board is not based off bit representation yet becuse was still unsure on how we wanted to implement that on the board
'''


class Board:
    pass


BOARD_SIZE = 8
BOARD_EMPTY = "O"
BOARD_BLACK = "B"
BOARD_WHITE = "W"


def init_board(board: Board, grid: List[List[str]]) -> None:
    board.grid = grid


def create_board(grid: List[List[str]]) -> Board:
    board = Board()
    init_board(board, grid)
    return board


def board_from_file(filename: str) -> Board:
    with open(filename, "r", encoding="utf-8") as infile:
        rows = [line.strip().upper() for line in infile if line.strip()]

    if len(rows) != BOARD_SIZE:
        raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    for row in rows:
        if len(row) != BOARD_SIZE:
            raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    for row in rows:
        for cell in row:
            if cell != BOARD_BLACK and cell != BOARD_WHITE and cell != BOARD_EMPTY:
                raise ValueError("Board file may only contain B, W, or O.")

    grid = []
    for row in rows:
        grid.append(list(row))

    return create_board(grid)


def board_clone(board: Board) -> Board:
    new_grid = []
    for row in board.grid:
        new_grid.append(row[:])
    return create_board(new_grid)


def board_opponent(player: str) -> str:
    if player == BOARD_BLACK:
        return BOARD_WHITE
    return BOARD_BLACK


def board_square_to_index(square: str) -> Tuple[int, int]:
    """Convert chess notation to row, col where row 0 is the top board row."""
    square = square.strip().upper()
    col = ord(square[0]) - ord("A")
    rank = int(square[1:])
    row = BOARD_SIZE - rank
    return (row, col)


def board_index_to_square(row: int, col: int) -> str:
    file_char = chr(ord("A") + col)
    rank = BOARD_SIZE - row
    return f"{file_char}{rank}"


def board_in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def board_piece_at(board: Board, row: int, col: int) -> str:
    return board.grid[row][col]


def board_set_piece(board: Board, row: int, col: int, value: str) -> None:
    board.grid[row][col] = value


def board_count_pieces(board: Board, player: str) -> int:
    count = 0
    for row in board.grid:
        for cell in row:
            if cell == player:
                count += 1
    return count


def board_center_squares() -> List[Tuple[int, int]]:
    return [
        board_square_to_index("D5"),
        board_square_to_index("E5"),
        board_square_to_index("D4"),
        board_square_to_index("E4"),
    ]


def board_is_initial_removal_phase(board: Board, player: str) -> bool:
    return board_count_pieces(board, player) == 32


def board_legal_moves(board: Board, player: str) -> List[Move]:
    if board_is_initial_removal_phase(board, player):
        return board_legal_removals(board, player)
    return board_legal_jumps(board, player)


def board_legal_removals(board: Board, player: str) -> List[Move]:
    moves = []

    for row, col in board_center_squares():
        if board.grid[row][col] == player:
            moves.append(create_move((row, col), None))

    return moves


def board_legal_jumps(board: Board, player: str) -> List[Move]:
    enemy = board_opponent(player)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    moves = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board.grid[row][col] != player:
                continue

            for d_row, d_col in directions:
                distance = 1

                while True:
                    mid_row = row + d_row * (2 * distance - 1)
                    mid_col = col + d_col * (2 * distance - 1)
                    land_row = row + d_row * (2 * distance)
                    land_col = col + d_col * (2 * distance)

                    if not (board_in_bounds(mid_row, mid_col) and board_in_bounds(land_row, land_col)):
                        break

                    if board.grid[mid_row][mid_col] != enemy:
                        break

                    if board.grid[land_row][land_col] != BOARD_EMPTY:
                        break

                    moves.append(create_move((row, col), (land_row, land_col)))
                    distance += 1

    return moves


def board_apply_move(board: Board, move: Move, player: str) -> Board:
    new_board = board_clone(board)

    if move_is_removal(move):
        row, col = move.start

        if new_board.grid[row][col] != player:
            raise ValueError("Invalid removal move.")

        new_board.grid[row][col] = BOARD_EMPTY
        return new_board

    start_row, start_col = move.start
    end_row, end_col = move.end

    if new_board.grid[start_row][start_col] != player:
        raise ValueError("Invalid jump start square.")

    if start_row == end_row:
        d_row = 0
    elif end_row > start_row:
        d_row = 1
    else:
        d_row = -1

    if start_col == end_col:
        d_col = 0
    elif end_col > start_col:
        d_col = 1
    else:
        d_col = -1

    new_board.grid[start_row][start_col] = BOARD_EMPTY

    row = start_row
    col = start_col

    while (row, col) != (end_row, end_col):
        jumped_row = row + d_row
        jumped_col = col + d_col
        landing_row = row + 2 * d_row
        landing_col = col + 2 * d_col

        if not (board_in_bounds(jumped_row, jumped_col) and board_in_bounds(landing_row, landing_col)):
            raise ValueError("Jump leaves board bounds.")

        new_board.grid[jumped_row][jumped_col] = BOARD_EMPTY
        row = landing_row
        col = landing_col

    new_board.grid[end_row][end_col] = player
    return new_board


def board_has_any_moves(board: Board, player: str) -> bool:
    return len(board_legal_moves(board, player)) > 0