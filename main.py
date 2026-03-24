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
from move import Move
from utils import print_board

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

    blackBoard, whiteBoard = board_from_file(board_file)
    agent = KonaneAgent(player)
    opponent = board_opponent(player)

    print_board(blackBoard, whiteBoard)

    my_move = agent.choose_move(blackBoard, whiteBoard)
    print("\nAgent chose: " + str(my_move), flush=True)
    blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, my_move)

    print()
    print_board(blackBoard, whiteBoard)
    print()

    for line in sys.stdin:
        opponent_text = line.strip()
        if not opponent_text:
            continue

        opponent_move = Move.from_string(opponent_text)
        blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, opponent_move)

        print()
        print_board(blackBoard, whiteBoard)
        print()

        if not board_has_any_moves(blackBoard, whiteBoard, player):
            print("Game over!")
            break

        my_move = agent.choose_move(blackBoard, whiteBoard)
        print("Agent chose: " + str(my_move), flush=True)
        blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, my_move)

        print()
        print_board(blackBoard, whiteBoard)
        print()

        if not board_has_any_moves(blackBoard, whiteBoard, opponent):
            print("Game over!")
            break


if __name__ == "__main__":
    main()