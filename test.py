from board import (
    BOARD_BLACK,
    BOARD_WHITE,
    BOARD_EMPTY,
    board_apply_move,
    board_count_pieces,
    board_from_file,
    board_has_any_moves,
    board_index_to_square,
    board_legal_moves,
    board_piece_at,
    board_square_to_index,
)
from move import create_move, move_from_string, move_is_removal, move_to_string
from game_state import create_game_state, game_state_legal_moves, game_state_next_state
from agent import KonaneAgent


def print_separator(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def print_board(board) -> None:
    for row in board.grid:
        print(" ".join(row))


def test_move_module() -> None:
    print_separator("TEST 1: MOVE MODULE")

    m1 = create_move((3, 3), None)
    print("Created removal move:")
    print(" start =", m1.start)
    print(" end   =", m1.end)
    print(" is removal =", move_is_removal(m1))
    print(" string =", move_to_string(m1))

    m2 = move_from_string("F5-D5")
    print("\nParsed jump move from string 'F5-D5':")
    print(" start =", m2.start)
    print(" end   =", m2.end)
    print(" is removal =", move_is_removal(m2))
    print(" string =", move_to_string(m2))


def test_board_module(board_file: str) -> None:
    print_separator("TEST 2: BOARD MODULE")

    board = board_from_file(board_file)

    print("Loaded board:")
    print_board(board)

    print("\nPiece counts:")
    print(" Black =", board_count_pieces(board, BOARD_BLACK))
    print(" White =", board_count_pieces(board, BOARD_WHITE))

    print("\nCoordinate conversion checks:")
    print(" D5 ->", board_square_to_index("D5"))
    print(" (3,3) ->", board_index_to_square(3, 3))

    print("\nLegal moves for Black:")
    black_moves = board_legal_moves(board, BOARD_BLACK)
    for move in black_moves:
        print(" ", move_to_string(move))

    print("\nLegal moves for White:")
    white_moves = board_legal_moves(board, BOARD_WHITE)
    for move in white_moves:
        print(" ", move_to_string(move))

    print("\nHas any moves:")
    print(" Black =", board_has_any_moves(board, BOARD_BLACK))
    print(" White =", board_has_any_moves(board, BOARD_WHITE))

    if len(black_moves) > 0:
        first_move = black_moves[0]
        print("\nApplying first Black move:", move_to_string(first_move))
        new_board = board_apply_move(board, first_move, BOARD_BLACK)

        print("Board after move:")
        print_board(new_board)

        row, col = first_move.start
        print("\nSquare moved from now contains:", board_piece_at(new_board, row, col))
        print("Black count after move:", board_count_pieces(new_board, BOARD_BLACK))
        print("White count after move:", board_count_pieces(new_board, BOARD_WHITE))


def test_game_state_module(board_file: str) -> None:
    print_separator("TEST 3: GAME STATE MODULE")

    board = board_from_file(board_file)
    state = create_game_state(board, BOARD_BLACK)

    print("Current player:", state.player_to_move)

    moves = game_state_legal_moves(state)
    print("Legal moves:")
    for move in moves:
        print(" ", move_to_string(move))

    if len(moves) > 0:
        next_state = game_state_next_state(state, moves[0])
        print("\nAfter applying:", move_to_string(moves[0]))
        print("Next player:", next_state.player_to_move)
        print("Next board:")
        print_board(next_state.board)


def test_agent_module(board_file: str) -> None:
    print_separator("TEST 4: AGENT MODULE")

    board = board_from_file(board_file)

    print("Initial board:")
    print_board(board)

    agent_black = KonaneAgent(BOARD_BLACK)
    chosen_move = agent_black.choose_move(board)

    print("\nAgent playing Black chose move:")
    print(" ", move_to_string(chosen_move))

    new_board = board_apply_move(board, chosen_move, BOARD_BLACK)
    print("\nBoard after agent move:")
    print_board(new_board)

    print("\nPiece counts after agent move:")
    print(" Black =", board_count_pieces(new_board, BOARD_BLACK))
    print(" White =", board_count_pieces(new_board, BOARD_WHITE))


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