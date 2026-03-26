from board import *
from move import Move
from game_state import GameState
from agent import KonaneAgent
from utils import print_board, chess_to_coord, coord_to_chess

def print_separator(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_move_module() -> None:
    print_separator("TEST 1: MOVE MODULE")

    m1 = Move((3, 3), None)
    print("Created removal move:")
    print(" start =", m1.start)
    print(" end   =", m1.end)
    print(" is removal =", m1.is_removal())
    print(" string =", str(m1))

    m2 = Move.from_string("F5-D5")
    print("\nParsed jump move from string 'F5-D5':")
    print(" start =", m2.start)
    print(" end   =", m2.end)
    print(" is removal =", m2.is_removal())
    print(" string =", str(m2))


def test_board_module(board_file: str) -> None:
    print_separator("TEST 2: BOARD MODULE")

    black, white = board_from_file(board_file)

    print("Loaded board:")
    print_board(black, white)

    print("\nPiece counts:")
    print(" Black =", board_count_pieces(black))
    print(" White =", board_count_pieces(white))

    print("\nCoordinate conversion checks:")
    print(" D5 ->", chess_to_coord("D5"))
    print(" (3,3) ->", coord_to_chess(3, 3))

    print("\nLegal moves for Black:")
    black_moves = board_legal_moves(black, white, BOARD_BLACK)
    for move in black_moves:
        print(" ", str(move))

    print("\nLegal moves for White:")
    white_moves = board_legal_moves(black, white, BOARD_WHITE)
    for move in white_moves:
        print(" ", str(move))

    print("\nHas any moves:")
    print(" Black =", board_has_any_moves(black, white, BOARD_BLACK))
    print(" White =", board_has_any_moves(black, white, BOARD_WHITE))

    if len(black_moves) > 0:
        first_move = black_moves[0]
        print("\nApplying first Black move:", str(first_move))
        new_black, new_white = board_apply_move(black, white, first_move)

        print("Board after move:")
        print_board(new_black, new_white)

        row, col = first_move.start
        #board_piece_at to remove
        '''print("\nSquare moved from now contains:", board_piece_at(new_black, new_white, row, col))'''
        print("Black count after move:", board_count_pieces(new_black))
        print("White count after move:", board_count_pieces(new_white))


def test_game_state_module(board_file: str) -> None:
    print_separator("TEST 3: GAME STATE MODULE")

    black, white = board_from_file(board_file)
    state = GameState(black, white, BOARD_BLACK)

    print("Current player:", state.player_to_move)

    moves = state.get_legal_moves()
    print("Legal moves:")
    for move in moves:
        print(" ", str(move))

    if len(moves) > 0:
        next_state = state.get_result_state(moves[0])
        print("\nAfter applying:", str(moves[0]))
        print("Next player:", next_state.player_to_move)
        print("Next board:")
        print_board(next_state.black_board, next_state.white_board)


def test_agent_module(board_file: str) -> None:
    print_separator("TEST 4: AGENT MODULE")

    black, white = board_from_file(board_file)

    print("Initial board:")
    print_board(black, white)

    agent_black = KonaneAgent(BOARD_BLACK)
    chosen_move = agent_black.choose_move(black, white)

    print("\nAgent playing Black chose move:")
    print(" ", str(chosen_move))

    new_black, new_white = board_apply_move(black, white, chosen_move)
    print("\nBoard after agent move:")
    print_board(new_black, new_white)

    print("\nPiece counts after agent move:")
    print(" Black =", board_count_pieces(new_black))
    print(" White =", board_count_pieces(new_white))


def main() -> None:
    board_file = "test_board.txt"

    print("Using test board file:", board_file)

    test_move_module()
    test_board_module(board_file)
    test_game_state_module(board_file)
    test_agent_module(board_file)

    print_separator("ALL TESTS COMPLETE")


if __name__ == "__main__":
    main()