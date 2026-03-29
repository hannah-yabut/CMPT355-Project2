from typing import Tuple

from utils import coord_to_chess, chess_to_coord

class Move:
     # Stores a move with a start position and optional end position
    '''
    Defines Move object and helper functions do: 
    - make moves 
    - identifies opening moves 
    - converts moves to/from string format (eg: "D5" or "F5-D5" (for now at least))
    - Moves are represented as (row, col) 
    '''
    
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int] = None):
        '''
        makes a new Move from start to end. End may be omitted to indicate the first move
        in the game where one of the center pieces is removed.
        '''
        self.start = start
        self.end = end

    @classmethod
    def from_string(cls, move_str: str):
        #Creates a Move from a string representing the move
        move_str = move_str.strip().upper()

        if "-" in move_str: # String represents a jump
            parts = move_str.split("-", 1)
            src = chess_to_coord(parts[0])
            dst = chess_to_coord(parts[1])

            return cls(src, dst)
        
        else:
            return cls(chess_to_coord(move_str))


    def is_removal(self) -> bool:
        # returns True if there is no destination for this move
        return self.end is None
    
    def __str__(self):
        '''
        Returns the move using chess notation to denote the spaces.
        If the move is a removal, only one coordinate is returned, otherwise it is formatted A1-A3
        '''
        if self.is_removal():
            return coord_to_chess(self.start[0], self.start[1])
        
        return (
            coord_to_chess(self.start[0], self.start[1])
            + "-"
            + coord_to_chess(self.end[0], self.end[1]))