from typing import List

from move import Move
from utils import BOARD_SIZE

BOARD_EMPTY = "O"
BOARD_BLACK = "B"
BOARD_WHITE = "W"

# This lookup table contains (board, shift) tuples where board is the color of the board
# at that position (0 for black, 1 for white) and shift is an integer which can be used
# with a bitshift operation to reach the space at that row and column.
BOARD_LOOKUP = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# The same thing but inverse; converts a color index and bit shift into a row, column pair.
COORD_LOOKUP = [
    [None for _ in range(BOARD_SIZE ** 2 // 2)], 
    [None for _ in range(BOARD_SIZE ** 2 // 2)]
]

# Initialize the tables
for col in range(BOARD_SIZE):
    for row in range(BOARD_SIZE):
        color = ((col % 2) + (row % 2)) % 2 # 0 for black, 1 for white
        shift = row * 4 + col // 2  # The boards are opposite each other and each have 32 spaces

        BOARD_LOOKUP[row][col] = (color, shift)
        COORD_LOOKUP[color][shift] = (row, col)


def board_from_file(filename: str) -> tuple[int, int]:
    """Returns two integers which are bitboards representing the black and white spaces."""

    with open(filename, "r", encoding="utf-8") as infile:
        rows = [line.strip().upper() for line in infile if line.strip()]

    if len(rows) != BOARD_SIZE:
        raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    for row in rows:
        if len(row) != BOARD_SIZE:
            raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    blackBoard, whiteBoard = 0x00000000, 0x00000000

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell = rows[row][col]

            if cell != BOARD_BLACK and cell != BOARD_WHITE and cell != BOARD_EMPTY:
                raise ValueError("Board file may only contain B, W, or O.")
            
            else:
                state = 1 if (cell == BOARD_BLACK or cell == BOARD_WHITE) else 0    # 0 for empty
                color, index = BOARD_LOOKUP[row][col]

                if color == 0:
                    blackBoard |= state << index  # This won't SET a bit to 0, but it should already be 0 if empty.
                else:
                    whiteBoard |= state << index

    return blackBoard, whiteBoard


def board_opponent(player: str) -> str:
    if player == BOARD_BLACK:
        return BOARD_WHITE
    return BOARD_BLACK


def board_in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def board_piece_at(blackBoard: int, whiteBoard: int, row: int, col: int) -> str:
    """Returns the piece at row, col or O for empty."""
    color, shift = BOARD_LOOKUP[row][col]
    
    if color == 0 and ((blackBoard >> shift) & 1 == 1):
        return "B"
    
    elif color == 1 and ((whiteBoard >> shift) & 1 == 1):
        return "W"
    
    else:
        return "O"


def board_count_pieces(board: int) -> int:
    """
    Returns the number of pieces in the board. This should be ONE of the boards, not both colors.
    """
    return board.bit_count()


def board_is_initial_removal_phase(blackBoard: int, whiteBoard: int) -> bool:
    """
    If the game still has 64 pieces, the game is in the initial removal phase.
    Returns True if the board has 64 pieces.
    """
    total = board_count_pieces(blackBoard) + board_count_pieces(whiteBoard)

    return (total >= 64)    # Change this to 63 if it turns out both players get to remove 1


def board_legal_moves(blackBoard: int, whiteBoard: int, player: str) -> List[Move]:
    """
    Returns a List of legal Moves available to the specified player color given the board states.
    player should be either "B" for Black or "W" for White.
    """
    if board_is_initial_removal_phase(blackBoard, whiteBoard):
        return board_legal_removals(player)
    
    return board_legal_jumps(blackBoard, whiteBoard, player)


def board_legal_removals(player: str) -> List[Move]:
    """
    In this version of Konane, only the agent gets to remove a piece, so we don't need to check the board.
    The only valid pieces are in the middle 2x2 square. Returns a list containing these Moves.
    """
    color = 0 if player == "B" else 1

    # There are 4 pieces in a row and the middle squares are in rows 3 and 4 (starting from 0)
    # Black's middle piece is the second black piece in row 3 but for white it's the third so add 1.
    row1, col1 = COORD_LOOKUP[color][3 * 4 + 1 + color]

    # The same but for row 4, where black and white are opposite from above.
    row2 ,col2 = COORD_LOOKUP[color][4 * 4 + 2 - color]

    return [Move((row1, col1)), Move((row2, col2))]


def board_legal_jumps(blackBoard: int, whiteBoard: int, player: str) -> List[Move]:
    """
    Generates a list of all possible moves for the player (color) specified.
    Parameters:
        player: A single character; "B" for black, "W" for white
    Returns:
        List[Move]: A List of Move objects representing the possible moves
    """
    
    EVEN_ROWS = 0x0F0F0F0F
    ODD_ROWS = 0xF0F0F0F0

    if player == BOARD_BLACK:
        player_bits = blackBoard
        opp_bits = whiteBoard
        player_color = 0
        offset = 0

    else:
        player_bits = whiteBoard
        opp_bits = blackBoard
        player_color = 1
        offset = 1

    empty = ~player_bits & 0xFFFFFFFF

    # Landing shift, victim shift, mask, row delta, and column delta (amount they moved)
    # The masks prevent the edges from wrapping around when shifting left or right.
    directions = [
        (-4, 0xFFFFFFFF, -2, 0),    # Up
        (4, 0xFFFFFFFF, 2, 0),  # Down
        (-1, 0xEEEEEEEE, 0, -2),    # Left
        (1, 0x77777777, 0, 2)   # Right
    ]
    
    moves = []

    # Move the entire board at once and find valid moves
    for l_shift, mask, d_row, d_col in directions:
        # player_bits & mask checks the player's starting positions and prevents wraparound.
        # opp_bits >> shift checks if there's an opponent in the path.
        # empty >> (shift * 2) ensures there's an empty space on the other side.

        if d_col == -2: # Left jump
            # Even rows: Victim is at << (1 - offset)
            # Odd rows:  Victim is at << offset
            even_j = (player_bits & EVEN_ROWS & mask) & (opp_bits << (1 - offset)) & (empty << 1)
            odd_j = (player_bits & ODD_ROWS & mask) & (opp_bits << offset) & (empty << 1)
            jumpable_bits = even_j | odd_j

        elif d_col == 2: # Right jump
            # Even rows: Victim is at >> offset
            # Odd rows:  Victim is at >> (1 - offset)
            even_j = (player_bits & EVEN_ROWS & mask) & (opp_bits >> offset) & (empty >> 1)
            odd_j = (player_bits & ODD_ROWS & mask) & (opp_bits >> (1 - offset)) & (empty >> 1)
            jumpable_bits = even_j | odd_j
        
        else:   # Up and down jumps
            if l_shift >= 0:
                jumpable_bits = (player_bits & mask) & (opp_bits >> l_shift) & (empty >> l_shift * 2)
            
            else:
                l_shift = abs(l_shift)
                jumpable_bits = (player_bits & mask) & (opp_bits << l_shift) & (empty << l_shift * 2)
        
        # Process each possible move found
        while jumpable_bits:
            lowest_bit = jumpable_bits & -jumpable_bits
            idx = lowest_bit.bit_length() - 1   # Effectively gets the index that this bit was at in the binary representation

            s_row, s_col = COORD_LOOKUP[player_color][idx]
            moves.append(Move((s_row, s_col), (s_row + d_row, s_col + d_col)))

            jumpable_bits ^= lowest_bit # Remove the bit

    return moves


def board_apply_move(blackBoard: int, whiteBoard: int, move: Move) -> tuple[int, int]:
    """Tries applying the given move to the board and returns the new state."""

    boards = [blackBoard, whiteBoard]   # Pack for easy access

    s_row, s_col = move.start
    s_color, s_shift = BOARD_LOOKUP[s_row][s_col]

    # Check if the starting square is empty
    if (boards[s_color] >> s_shift) & 1 == 0:
        raise ValueError("Move has invalid starting position.")
    
    boards[s_color] &= ~(1 << s_shift)  # Remove the piece at the starting position

    # If we're just removing a piece from the middle, we're done.
    if move.is_removal():
        return boards[0], boards[1]

    # ----- JUMPING LOGIC -----
    e_row, e_col = move.end

    if e_row > BOARD_SIZE or e_col > BOARD_SIZE:
        raise ValueError("Jump leaves board bounds.")
    
    # Determine the direction of the jump to check for chains.
    if s_row == e_row:
        d_row = 0
    elif e_row > s_row:
        d_row = 1
    else:
        d_row = -1

    if s_col == e_col:
        d_col = 0
    elif e_col > s_col:
        d_col = 1
    else:
        d_col = -1

    v_color, v_shift = BOARD_LOOKUP[s_row + d_row][s_col + d_col]

    if (boards[v_color] >> v_shift) & 0:
        raise ValueError("There is no piece to jump over!")

    # Perform as many jumps in a straight line as possible.
    while True:
        boards[v_color] &= ~(1 << v_shift)  # Clear the space jumped over

        e_row += 2 * d_row
        e_col += 2 * d_col

        if e_row > 2 and e_col > 2 and e_row < BOARD_SIZE and e_col < BOARD_SIZE:
            v_color, v_shift = BOARD_LOOKUP[e_row - d_row][e_col - d_col]   # Check behind the jump

            if (boards[v_color] >> v_shift) & 1 == 0:    # No more chains are possible
                break

        else:
            break

    e_row -= 2 * d_row  # Undo the last move (an invalid jump terminates the loop)
    e_col -= 2 * d_col
    
    # Finally, put the moving piece where it landed
    e_color, e_shift = BOARD_LOOKUP[e_row][e_col]
    boards[e_color] |= 1 << e_shift

    return boards[0], boards[1]


def board_has_any_moves(blackBoard: int, whiteBoard: int, player: str) -> bool:
    if player == BOARD_BLACK:
        player_bits, opp_bits = blackBoard, whiteBoard
        offset = 0

    else:
        player_bits, opp_bits = whiteBoard, blackBoard
        offset = 1

    empty = ~player_bits & 0xFFFFFFFF

    # Check up / down. The boards are 32 bits so a shift of 4 bits is one row vertically.
    if player_bits & (opp_bits >> 4) & (empty >> 8): return True    # Down
    if player_bits & (opp_bits << 4) & (empty << 8): return True    # Up

    # Check left / right. Masks are necessary to ensure pieces don't wrap around to the next row.
    if (player_bits & 0x77777777) & (opp_bits >> offset) & (empty >> 1): return True
    if (player_bits & 0xEEEEEEEE) & (opp_bits << (1 - offset)) & (empty << 1): return True

    return False