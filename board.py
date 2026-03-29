from typing import List

from move import Move
from utils import BOARD_SIZE

BOARD_EMPTY = "O"
BOARD_BLACK = "B"
BOARD_WHITE = "W"
#added the following to be able to access easily
MASK64 = 0xFFFFFFFFFFFFFFFF
NOT_A_FILE = 0xFEFEFEFEFEFEFEFE
NOT_B_FILE = 0xFDFDFDFDFDFDFDFD
NOT_G_FILE = 0xBFBFBFBFBFBFBFBF
NOT_H_FILE = 0x7F7F7F7F7F7F7F7F
NOT_AB_FILE = NOT_A_FILE & NOT_B_FILE
NOT_GH_FILE = NOT_G_FILE & NOT_H_FILE
# getting rid of the board lookup -j



def board_from_file(filename: str) -> tuple[int, int]:
    """Returns two integers which are bitboards representing the black and white spaces."""

    with open(filename, "r", encoding="utf-8") as infile:
        rows = [line.strip().upper() for line in infile if line.strip()]

    if len(rows) != BOARD_SIZE:
        raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    for row in rows:
        if len(row) != BOARD_SIZE:
            raise ValueError("Board file must contain exactly 8 rows of 8 characters.")

    #changing this to starting as 0,0 -j
    #initializing the boards
    blackBoard, whiteBoard = 0,0

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell = rows[row][col]
            if cell != BOARD_BLACK and cell != BOARD_WHITE and cell != BOARD_EMPTY:
                raise ValueError("Board file may only contain B, W, or O.")
            else:
                # check B, then W, if neither it stays as 0 -j
                state = 1   
                index = row * 8 + col
                if cell == BOARD_BLACK:
                    blackBoard |= state << index  # This won't SET a bit to 0, but it should already be 0 if empty.
                elif cell == BOARD_WHITE:
                    whiteBoard |= state << index
                

    return blackBoard, whiteBoard

def board_opponent(player: str) -> str:
    if player == BOARD_BLACK:
        return BOARD_WHITE
    return BOARD_BLACK

#might try to implement mask here, not used anywhere else -j
def board_in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

#getting rid of board_piece_at, only used once for a print function

#both of the below work with the 64 bit board
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
    
    return (total >= 63)    # Change this to 63 if it turns out both players get to remove 1
    #changed it to 63! -j


def board_legal_moves(blackBoard: int, whiteBoard: int, player: str) -> List[Move]:
    """
    Returns a List of legal Moves available to the specified player color given the board states.
    player should be either "B" for Black or "W" for White.
    """
    if board_is_initial_removal_phase(blackBoard, whiteBoard):
        return board_legal_removals(player)
    
    return board_legal_jumps(blackBoard, whiteBoard, player)

#come back to this -j
def board_legal_removals(player: str) -> List[Move]:
    """
    In this version of Konane, only the agent gets to remove a piece, so we don't need to check the board.
    The only valid pieces are in the middle 2x2 square. Returns a list containing these Moves.
    """
    if player == BOARD_BLACK:
        #remove d5 or e4
        return [Move((3, 3)), Move((4, 4))]
        #remove e5 or d4
    else:
        return [Move((3, 4)), Move((4, 3))]


def board_legal_jumps(blackBoard: int, whiteBoard: int, player: str) -> List[Move]:
    """
    Generates a list of all possible moves for the player (color) specified.
    Parameters:
        player: A single character; "B" for black, "W" for white
    Returns:
        List[Move]: A List of Move objects representing the possible moves
    """
    if player == BOARD_BLACK:
        player_bits = blackBoard
        opp_bits = whiteBoard

    else:
        player_bits = whiteBoard
        opp_bits = blackBoard

    #updated for 64 bit, 
    empty = ~(player_bits | opp_bits) & MASK64

    # Landing shift, victim shift, mask, row delta, and column delta (amount they moved)
    # The masks prevent the edges from wrapping around when shifting left or right.
    
    #updating with 64 bit boards in mind
    #doubled the masks for 64 bits
    directions = [
        (-8, 0xFFFFFFFFFFFFFFFF, -2, 0),    # Up
        (8, 0xFFFFFFFFFFFFFFFF, 2, 0),  # Down
        (-1, NOT_AB_FILE, 0, -2),    # Left
        (1, NOT_GH_FILE, 0, 2)   # Right    
        ]
    
    moves = []

    

    # Move the entire board at once and find valid moves
    for l_shift, mask, d_row, d_col in directions:
        # player_bits & mask checks the player's starting positions and prevents wraparound.
        # opp_bits << offset checks if there's an opponent in the path.
        # empty << 1 ensures there's an empty space on the other side.
        # Odd and even rows have to be checked separately because of the alternating nature of the board
        # and the use of two separate, non-overlapping bitboards.
        #l_shift will be the shift value check for opponent board
        #d_row is for vertical checks
        #d_col is for horizontal checks
      
        #this actually takes care of all 4 cases
        #this takes care of down and right
        if l_shift > 0:
            jumpable_bits = (player_bits & mask) & (opp_bits >> l_shift) & (empty >> l_shift * 2)
        #this one takes care of left and up
        else:
            l_shift = abs(l_shift)
            jumpable_bits = (player_bits & mask) & (opp_bits << l_shift) & (empty << l_shift * 2)
        
        # Process each possible move found
        while jumpable_bits:
            lowest_bit = jumpable_bits & -jumpable_bits
            idx = lowest_bit.bit_length() - 1   # Effectively gets the index that this bit was at in the binary representation

            s_row = idx // 8
            s_col = idx % 8
            #landing first jump
            e_row = s_row + d_row
            e_col = s_col + d_col
            moves.append(Move((s_row, s_col), (s_row + d_row, s_col + d_col)))
            curr_e_row = e_row
            curr_e_col = e_col
            
            while True:
                # Calculate the coordinates of the NEXT opponent and NEXT landing square
                # d_row // 2 gives us the 1-square step size (-1, 0, or 1)
                next_opp_r = curr_e_row + (d_row // 2) 
                next_opp_c = curr_e_col + (d_col // 2)
                next_land_r = curr_e_row + d_row
                next_land_c = curr_e_col + d_col
                
                # 1. Are we falling off the board?
                if not (0 <= next_land_r < BOARD_SIZE and 0 <= next_land_c < BOARD_SIZE):
                    break
                    
                next_opp_idx = next_opp_r * 8 + next_opp_c
                next_land_idx = next_land_r * 8 + next_land_c
                
                # 2. Is there an opponent to jump, AND is the landing square empty?
                if (opp_bits & (1 << next_opp_idx)) and (empty & (1 << next_land_idx)):
                    curr_e_row = next_land_r
                    curr_e_col = next_land_c
                    
                    # Add this longer chain-jump as a valid legal move
                    moves.append(Move((s_row, s_col), (curr_e_row, curr_e_col)))
                else:
                    # Path is blocked, chain jump is over
                    break
            

            jumpable_bits ^= lowest_bit # Remove the bit

    return moves


def board_apply_move(blackBoard: int, whiteBoard: int, move: Move) -> tuple[int, int]:
    """Tries applying the given move to the board and returns the new state."""


    s_row, s_col = move.start
    #formula to get index
    s_idx = s_row * 8 + s_col
    
    #check if player/turn is blackboard or whiteboard
    if blackBoard & (1 << s_idx):
        playerBoard = blackBoard
        oppBoard = whiteBoard
        isBlackTurn = True
    elif whiteBoard & (1 << s_idx):
        playerBoard = whiteBoard
        oppBoard = blackBoard
        isBlackTurn = False
    else:
        raise ValueError("Move has invalid starting position.")


    
    playerBoard &= ~(1 << s_idx)  # Remove the piece at the starting position

    # If we're just removing a piece from the middle, we're done.
    if move.is_removal():
        return (playerBoard,oppBoard) if isBlackTurn else (oppBoard, playerBoard)

    # ----- JUMPING LOGIC -----
    e_row, e_col = move.end

    if e_row > BOARD_SIZE or e_col > BOARD_SIZE:
        raise ValueError("Jump leaves board bounds.")
    
    
    # Determine the direction of the jump to check for chains.

# Determine the step direction of the jump (-1, 0, or 1)
    d_row = 0 if s_row == e_row else (e_row - s_row) // abs(e_row - s_row)
    d_col = 0 if s_col == e_col else (e_col - s_col) // abs(e_col - s_col)
    curr_row, curr_col = s_row, s_col



    # Perform as many jumps in a straight line as possible.
    while (curr_col, curr_row) != (e_col, e_row):
        #opponent square values, to check if it can jump over
        v_row = curr_row + d_row
        v_col = curr_col + d_col
        v_idx = v_row * 8 + v_col

        if not oppBoard & (1 << v_idx):
            raise ValueError("There is no piece to jump over!")
        
        oppBoard &= ~(1 << v_idx)  # Clear the space jumped over

        curr_row += 2 * d_row
        curr_col += 2 * d_col

    
    # Finally, put the moving piece where it landed
    e_idx = e_row * 8 + e_col
    playerBoard |= (1 << e_idx)
    #return corresponding boards
    if isBlackTurn:
        return playerBoard, oppBoard
    else:
        return oppBoard, playerBoard


def board_has_any_moves(blackBoard: int, whiteBoard: int, player: str) -> bool:
    if player == BOARD_BLACK:
        player_bits, opp_bits = blackBoard, whiteBoard

    else:
        player_bits, opp_bits = whiteBoard, blackBoard

    empty = ~(player_bits | opp_bits) & MASK64
    # Check up / down. The boards are 64 bits so a shift of 8 bits is one row vertically.
    if player_bits & (opp_bits >> 8) & (empty >> 16): return True    # Down
    if player_bits & (opp_bits << 8) & (empty << 16): return True    # Up

    # Check left / right. Masks are necessary to ensure pieces don't wrap around to the next row.
    if (player_bits & NOT_GH_FILE) & (opp_bits >> 1) & (empty >> 2): return True
    if (player_bits & NOT_AB_FILE) & (opp_bits << 1) & (empty << 2): return True

    return False