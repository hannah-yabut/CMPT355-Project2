#!/usr/bin/env python3

import math
import time
from typing import List

from board import (
    board_apply_move,
    board_count_pieces,
    board_legal_moves,
    board_opponent,
)
from game_state import GameState
from move import Move


THINKING_TIME = 9.0


class KonaneAgent:
    '''
    Implements the agent, this is the class' current behaviour: 
    - selects a move from available legal moves 
    - uses first legal move first 
    Built to extend with Alpha Beta pruning algorithm when implemented 
    '''
    def __init__(self, me: str, max_depth: int = 4) -> None:
        self.me = me.upper()
        self.opp = board_opponent(self.me)
        self.max_depth = max_depth
        self.start_time = 0.0

    def choose_move(self, blackBoard: int, whiteBoard: int) -> Move:
        self.start_time = time.time()

        state = GameState(blackBoard, whiteBoard, self.me)
        legal = state.get_legal_moves()

        if not legal:
            raise RuntimeError("No legal moves available.")

        ordered_moves = sorted(
            legal,
            key=lambda mv: self.quick_move_score(blackBoard, whiteBoard, mv),
            reverse=True,
        )

        best_move = ordered_moves[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf

        for move in ordered_moves:
            if self.time_up():
                break

            next_state = state.get_result_state(move)
            score = self.alphabeta(
                next_state,
                self.max_depth - 1,
                alpha,
                beta,
                False,
            )

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        return best_move

    def alphabeta(self, state: GameState, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if self.time_up() or depth == 0:
            return self.evaluate(state.black_board, state.white_board)

        legal = state.get_legal_moves()

        if not legal:
            if state.player_to_move == self.me:
                return -10000
            return 10000

        if maximizing:
            value = -math.inf
            ordered = self.order_moves(state.black_board, state.white_board, legal, self.me, True)

            for move in ordered:
                next_state = state.get_result_state(move)
                value = max(value, self.alphabeta(next_state, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)

                if beta <= alpha:
                    break

            return value

        value = math.inf
        ordered = self.order_moves(state.black_board, state.white_board, legal, self.opp, False)

        for move in ordered:
            next_state = state.get_result_state(move)
            value = min(value, self.alphabeta(next_state, depth - 1, alpha, beta, True))
            beta = min(beta, value)

            if beta <= alpha:
                break

        return value

    def order_moves(self, black: int, white: int, moves: List[Move],
                    player: str, reverse: bool) -> List[Move]:
        def score(move: Move) -> int:
            new_white, new_black = board_apply_move(black, white, move)
            my_moves = len(board_legal_moves(new_black, new_white, self.me))
            opp_moves = len(board_legal_moves(new_black, new_white, self.opp))
            return 4 * (my_moves - opp_moves) + self.move_distance(move)

        return sorted(moves, key=score, reverse=reverse)

    def quick_move_score(self, black: int, white: int, move: Move) -> int:
        new_black, new_white = board_apply_move(black, white, move)
        my_moves = len(board_legal_moves(new_black, new_white, self.me))
        opp_moves = len(board_legal_moves(new_black, new_white, self.opp))
        return 4 * (my_moves - opp_moves) + self.move_distance(move)

    def move_distance(self, move: Move) -> int:
        if move.is_removal():
            return 0

        r1, c1 = move.start
        r2, c2 = move.end
        return abs(r1 - r2) + abs(c1 - c2)

    def evaluate(self, black: int, white: int) -> int:
        my_moves = len(board_legal_moves(black, white, self.me))
        opp_moves = len(board_legal_moves(black, white, self.opp))
        my_pieces = board_count_pieces(black)
        opp_pieces = board_count_pieces(white)

        return 10 * (my_moves - opp_moves) + 2 * (my_pieces - opp_pieces)

    def time_up(self) -> bool:
        return (time.time() - self.start_time) >= THINKING_TIME