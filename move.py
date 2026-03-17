from typing import Tuple


class Move:
     # Stores a move with a start position and optional end position
    '''
    Defines Move object and helper functions do: 
    - make moves 
    - identifies opening moves 
    - converts moves to/from string format (eg: "D5" or "F5-D5" (for now at least))
    - Moves are represeneted as (row, col) 
    '''
    pass


def init_move(move: Move, start: Tuple[int, int], end) -> None:
    move.start = start
    move.end = end


def create_move(start: Tuple[int, int], end) -> Move:
     # Stores a move with a start position and optional end position
    move = Move()
    init_move(move, start, end)
    return move


def move_is_removal(move: Move) -> bool:
    # removal move has no destination 
    return move.end is None


def move_to_string(move: Move) -> str:
    from board import board_index_to_square

    if move_is_removal(move):
        return board_index_to_square(move.start[0], move.start[1])

    return (
        board_index_to_square(move.start[0], move.start[1])
        + "-"
        + board_index_to_square(move.end[0], move.end[1])
    )


def move_from_string(text: str) -> Move:
      # Parse string input into a Move object
    from board import board_square_to_index

    cleaned = text.strip().upper()

    if "-" in cleaned:
        parts = cleaned.split("-", 1)
        src = board_square_to_index(parts[0])
        dst = board_square_to_index(parts[1])
        return create_move(src, dst)

    return create_move(board_square_to_index(cleaned), None)