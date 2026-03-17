from typing import List

from board import Board, board_apply_move, board_legal_moves, board_opponent
from move import Move


class GameState:
    '''
    Manages game state by: 
    - current board 
    - current player 
    - applying moves 
    - switching turns 
    '''
    pass


def init_game_state(state: GameState, board: Board, player_to_move: str) -> None:
    state.board = board
    state.player_to_move = player_to_move


def create_game_state(board: Board, player_to_move: str) -> GameState:
    state = GameState()
    init_game_state(state, board, player_to_move)
    return state


def game_state_legal_moves(state: GameState) -> List[Move]:
    return board_legal_moves(state.board, state.player_to_move)


def game_state_next_state(state: GameState, move: Move) -> GameState:
    new_board = board_apply_move(state.board, move, state.player_to_move)
    next_player = board_opponent(state.player_to_move)
    return create_game_state(new_board, next_player)