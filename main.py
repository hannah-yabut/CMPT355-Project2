import sys

from agent import KonaneAgent
from board import (
    BOARD_BLACK,
    BOARD_WHITE,
    board_apply_move,
    board_from_file,
    board_has_any_moves,
    board_opponent,
)
from move import move_from_string, move_to_string


def main() -> None:
    '''
    usage: python3 main.py <board_file> <B|W>
    - loads the board 
    - plays as Black or White (for right now)
    - outputs chosen moves
    - reads opponent (min) moves from input 
    '''
    if len(sys.argv) != 3:
        print("Usage: python3 main.py boardfile B|W", file=sys.stderr)
        raise SystemExit(1)

    board_file = sys.argv[1]
    player = sys.argv[2].upper()

    if player != BOARD_BLACK and player != BOARD_WHITE:
        print("Player must be B or W.", file=sys.stderr)
        raise SystemExit(1)

    board = board_from_file(board_file)
    agent = KonaneAgent(player)
    opponent = board_opponent(player)

    my_move = agent.choose_move(board)
    print(move_to_string(my_move), flush=True)
    board = board_apply_move(board, my_move, player)

    for line in sys.stdin:
        opponent_text = line.strip()
        if not opponent_text:
            continue

        opponent_move = move_from_string(opponent_text)
        board = board_apply_move(board, opponent_move, opponent)

        if not board_has_any_moves(board, player):
            break

        my_move = agent.choose_move(board)
        print(move_to_string(my_move), flush=True)
        board = board_apply_move(board, my_move, player)


if __name__ == "__main__":
    main()