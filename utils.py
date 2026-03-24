# utils.py - contains some general helper functions and constants.

from typing import Tuple

BOARD_SIZE = 8

def print_board(blackBoard: int, whiteBoard: int) -> None:
    boards = [blackBoard, whiteBoard]

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = (row + col) % 2 # 0 for black, 1 for white
            shift = (row * 4) + (col // 2)

            if (boards[color] >> shift) & 1:
                print("B " if color == 0 else "W ", end = "")

            else:
                print("O ", end = "")
        
        print()


def chess_to_coord(square: str) -> Tuple[int, int]:
    """Convert chess notation to row, col where 0, 0 is the top-left corner."""
    square = square.strip().upper()
    col = ord(square[0]) - ord("A")
    rank = int(square[1:])
    row = BOARD_SIZE - rank
    return (row, col)


def coord_to_chess(row: int, col: int) -> str:
    """Convert a row, col coordinate to chess notation where A8 is the top-left space."""
    file_char = chr(ord("A") + col)
    rank = BOARD_SIZE - row
    return f"{file_char}{rank}"