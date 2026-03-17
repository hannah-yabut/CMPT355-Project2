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
from game_state import (
    create_game_state,
    game_state_legal_moves,
    game_state_next_state,
)
from move import Move, move_is_removal


THINKING_TIME = 9.0


class KonaneAgent:
    '''
    Implements the agent, this is the class' current behaviour: 
    - selects a move from available legal moves 
    - uses first legal move first 
    Built to extend with Alpha Bete pruning algorithm when implemented 
    '''
    def __init__(self, me: str, max_depth: int = 4) -> None:
        self.me = me.upper()
        self.opp = board_opponent(self.me)
        self.max_depth = max_depth
        self.start_time = 0.0

    def choose_move(self, board) -> Move:
        self.start_time = time.time()

        state = create_game_state(board, self.me)
        legal = game_state_legal_moves(state)

        if not legal:
            raise RuntimeError("No legal moves available.")

        ordered_moves = sorted(
            legal,
            key=lambda mv: self.quick_move_score(board, mv),
            reverse=True,
        )

        best_move = ordered_moves[0]
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf

        for move in ordered_moves:
            if self.time_up():
                break

            next_state = game_state_next_state(state, move)
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

    def alphabeta(self, state, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if self.time_up() or depth == 0:
            return self.evaluate(state.board)

        legal = game_state_legal_moves(state)

        if not legal:
            if state.player_to_move == self.me:
                return -10000
            return 10000

        if maximizing:
            value = -math.inf
            ordered = self.order_moves(state.board, legal, self.me, True)

            for move in ordered:
                next_state = game_state_next_state(state, move)
                value = max(value, self.alphabeta(next_state, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)

                if beta <= alpha:
                    break

            return value

        value = math.inf
        ordered = self.order_moves(state.board, legal, self.opp, False)

        for move in ordered:
            next_state = game_state_next_state(state, move)
            value = min(value, self.alphabeta(next_state, depth - 1, alpha, beta, True))
            beta = min(beta, value)

            if beta <= alpha:
                break

        return value

    def order_moves(self, board, moves: List[Move], player: str, reverse: bool) -> List[Move]:
        def score(move: Move) -> int:
            new_board = board_apply_move(board, move, player)
            my_moves = len(board_legal_moves(new_board, self.me))
            opp_moves = len(board_legal_moves(new_board, self.opp))
            return 4 * (my_moves - opp_moves) + self.move_distance(move)

        return sorted(moves, key=score, reverse=reverse)

    def quick_move_score(self, board, move: Move) -> int:
        new_board = board_apply_move(board, move, self.me)
        my_moves = len(board_legal_moves(new_board, self.me))
        opp_moves = len(board_legal_moves(new_board, self.opp))
        return 4 * (my_moves - opp_moves) + self.move_distance(move)

    def move_distance(self, move: Move) -> int:
        if move_is_removal(move):
            return 0

        r1, c1 = move.start
        r2, c2 = move.end
        return abs(r1 - r2) + abs(c1 - c2)

    def evaluate(self, board) -> int:
        my_moves = len(board_legal_moves(board, self.me))
        opp_moves = len(board_legal_moves(board, self.opp))
        my_pieces = board_count_pieces(board, self.me)
        opp_pieces = board_count_pieces(board, self.opp)

        return 10 * (my_moves - opp_moves) + 2 * (my_pieces - opp_pieces)

    def time_up(self) -> bool:
        return (time.time() - self.start_time) >= THINKING_TIME