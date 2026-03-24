from typing import List

from board import board_apply_move, board_legal_moves, board_opponent
from move import Move


class GameState:
    '''
    Manages game state by: 
    - current board 
    - current player 
    - applying moves 
    - switching turns 
    '''
    
    def __init__(self, blackBoard: int, whiteBoard: int, player_to_move: str):
        """Creates a GameState from the initial data given."""

        self.black_board = blackBoard
        self.white_board = whiteBoard
        self.player_to_move = player_to_move

    def get_legal_moves(self) -> List[Move]:
        """Returns a list of all valid moves from this state."""

        return board_legal_moves(self.black_board, self.white_board, self.player_to_move)
    
    def get_result_state(self, move: Move) -> "GameState":
        """Returns a new GameState which is the result of making the given move from this state."""
        
        new_black, new_white = board_apply_move(self.black_board, self.white_board, move)
        next_player = board_opponent(self.player_to_move)

        return GameState(new_black, new_white, next_player)