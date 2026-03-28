# utils.py - contains some general helper functions and constants.

from typing import Tuple

BOARD_SIZE = 8
#redid the print_board to accomodate 64 bit board -j
def print_board(blackBoard: int, whiteBoard: int) -> None:
    boards = [blackBoard, whiteBoard]
    board_print = ""
    for row in range(BOARD_SIZE):
        rowPrint = f""
        for col in range(BOARD_SIZE):
            shift = 1 << (row * 8 + col)
            if blackBoard & shift:
                rowPrint += "B "
            elif whiteBoard & shift:
                rowPrint += "W "
            else:
                rowPrint += "O "
        board_print += rowPrint + "\n"
    board_print += "\n"
    print(board_print)


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