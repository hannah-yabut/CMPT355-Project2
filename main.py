import sys
from agent import KonaneAgent
from board import board_from_file, board_apply_move, board_legal_moves
from move import Move


def debug(msg: str) -> None:
    '''
    prints debug messages to stderr so they do not interfere with the driver
    comment out the print line if you do not want debug output
    '''
    # print(msg, file=sys.stderr, flush=True)
    pass

def parse_move(text: str) -> Move:
    '''
    Parses moves in the format used by the driver, such as:
      D5
      E5
      B5-D5
      H1-H5
    '''
    text = text.strip().upper()

    if not text:
        raise ValueError("Empty move string.")

    def square_to_pos(square: str): # chess notation 
        if len(square) < 2 or len(square) > 3:
            raise ValueError(f"Invalid square: {square}")

        col_char = square[0]
        row_str = square[1:]

        if col_char < "A" or col_char > "H":
            raise ValueError(f"Invalid column in square: {square}")

        if not row_str.isdigit():
            raise ValueError(f"Invalid row in square: {square}")

        row_num = int(row_str)
        if row_num < 1 or row_num > 8:
            raise ValueError(f"Invalid row number in square: {square}")

        col = ord(col_char) - ord("A")
        row = 8 - row_num   # row 8 is top => internal row 0

        return (row, col)
    
    # jump moves 
    if "-" in text:
        start_str, end_str = text.split("-", 1)
        start = square_to_pos(start_str)
        end = square_to_pos(end_str)
        return Move(start, end)
   
    # removal move 
    return Move(square_to_pos(text))


def main():
    '''
    handles communication with driver 
    '''
    if len(sys.argv) != 3:
        print("Usage: main.py boardfile player", file=sys.stderr)
        sys.exit(1)

    boardfile = sys.argv[1]
    player = sys.argv[2].upper()

    blackBoard, whiteBoard = board_from_file(boardfile)
    agent = KonaneAgent(player) # create agent 

    # first move: driver expects to move immediately 
    legal = board_legal_moves(blackBoard, whiteBoard, player)
    if not legal:
        debug("No legal opening move.")
        return

    my_move = agent.choose_move(blackBoard, whiteBoard) # choose output move 
    print(my_move, flush=True)

    # update our local board with our move
    blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, my_move)

    # keep playing until stdin closes or someone has no move
    while True:
        # Read opponent move from stdin
        line = sys.stdin.readline()

        # EOF means driver/opponent ended
        if not line:
            debug("EOF from driver.")
            break

        line = line.strip()
        if not line:
            continue

        try:
            opp_move = parse_move(line)
        except Exception as e:
            debug(f"Could not parse opponent move '{line}': {e}")
            break

        # apply opponent move to our local board
        try:
            blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, opp_move)
        except Exception as e:
            debug(f"Opponent move invalid on our local board '{line}': {e}")
            break

        # check if we still have a legal move
        legal = board_legal_moves(blackBoard, whiteBoard, player)
        if not legal:
            debug("No legal reply move available.")
            break

        # Choose and print our move 
        try:
            my_move = agent.choose_move(blackBoard, whiteBoard)
        except Exception as e:
            debug(f"Agent failed to choose move: {e}")
            break

        print(my_move, flush=True)

        # apply our own move locally
        try:
            blackBoard, whiteBoard = board_apply_move(blackBoard, whiteBoard, my_move)
        except Exception as e:
            debug(f"Our chosen move was invalid locally: {e}")
            break