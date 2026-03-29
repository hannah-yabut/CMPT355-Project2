#!/usr/bin/env python3

import math
import time
from typing import List, Tuple

# imports from board.py
from board import (
    board_legal_moves,
    board_opponent,
)
from game_state import GameState  # for search tree
from move import Move

# changed max thinking time in case of delay to make sure it's under 10s
# tested with a stopwatch
THINKING_TIME = 7.0


class KonaneAgent:
    '''
    class of the agent. uses iterative deepening + alpha-beta pruning
    '''

    def __init__(self, me: str, max_depth: int = 7) -> None:
        self.me = me.upper()  # stores max (us) color
        self.opp = board_opponent(self.me)  # stores min (opp) color
        self.max_depth = max_depth  # max search depth
        self.start_time = 0.0  # tracks time limit

    def choose_move(self, blackBoard: int, whiteBoard: int) -> Move:
        '''
        chooses the best move using iterative deepening search
        '''
        self.start_time = time.time()

        state = GameState(blackBoard, whiteBoard, self.me)
        legal = state.get_legal_moves()

        if not legal:
            raise RuntimeError("No legal moves available.")

        best_move = legal[0]

        # initial move ordering before search begins
        ordered_moves = self.order_moves(
            blackBoard,
            whiteBoard,
            legal,
            self.me,
            True,
        )

        depth = 1
        while depth <= self.max_depth and not self.time_up():
            current_best_move = None
            current_best_value = -math.inf
            alpha = -math.inf
            beta = math.inf

            # store scores so we can reorder moves for the next iteration
            move_scores = []

            for move in ordered_moves:
                if self.time_up():
                    break

                next_state = state.get_result_state(move)
                value = self.alphabeta(
                    next_state,
                    depth - 1,
                    alpha,
                    beta,
                    maximizing=(next_state.player_to_move == self.me),
                )

                move_scores.append((move, value))

                if value > current_best_value:
                    current_best_value = value
                    current_best_move = move

                alpha = max(alpha, current_best_value)

                # immediate winning move found
                if current_best_value >= 100000 and current_best_move is not None:
                    return current_best_move

            # only update best move and reorder if this depth finished in time
            if not self.time_up() and current_best_move is not None:
                best_move = current_best_move

                # best moves from this depth get searched first next depth
                move_scores.sort(key=lambda x: x[1], reverse=True)
                ordered_moves = [move for move, _ in move_scores]

            depth += 1

        return best_move

    def alphabeta(
        self,
        state: GameState,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
    ) -> float:
        '''
        alpha-beta pruning function search (based on textbook)
        '''
        if self.time_up():
            # if out of time, return heuristic eval
            return self.evaluate(state.black_board, state.white_board)

        legal = state.get_legal_moves()

        # remove state if no moves
        if not legal:
            if state.player_to_move == self.me:
                return -100000 + (self.max_depth - depth)
            return 100000 - (self.max_depth - depth)

        if depth == 0:
            # if depth limit is reached, make a decision
            return self.evaluate(state.black_board, state.white_board)

        ordered = self.order_moves(
            state.black_board,
            state.white_board,
            legal,
            state.player_to_move,
            maximizing,
        )

        if maximizing:
            # max player
            value = -math.inf
            for move in ordered:
                if self.time_up():
                    break

                next_state = state.get_result_state(move)
                value = max(
                    value,
                    self.alphabeta(next_state, depth - 1, alpha, beta, False),
                )
                alpha = max(alpha, value)

                # pruning statement
                if alpha >= beta:
                    break

            return value

        # min player
        value = math.inf
        for move in ordered:
            if self.time_up():
                break

            next_state = state.get_result_state(move)
            value = min(
                value,
                self.alphabeta(next_state, depth - 1, alpha, beta, True),
            )
            beta = min(beta, value)

            # prune step again
            if beta <= alpha:
                break

        return value

    def order_moves(
        self,
        black: int,
        white: int,
        moves: List[Move],
        player: str,
        reverse: bool,
    ) -> List[Move]:
        '''
        heuristic move ordering

        stronger ordering helps alpha-beta prune more effectively

        preference:
        1. moves that reduce opponent mobility
        2. longer jumps
        3. non-removal moves over removal moves
        '''

        def score(move: Move) -> int:
            # simulate move
            next_black, next_white = self.apply_move_for_ordering(
                black,
                white,
                move,
                player,
            )

            opponent = board_opponent(player)

            # fewer opponent replies is better
            opp_moves = len(board_legal_moves(next_black, next_white, opponent))

            # more replies for us next turn is also useful
            my_future_moves = len(board_legal_moves(next_black, next_white, player))

            jump_score = self.move_distance(move)
            removal_penalty = -8 if move.is_removal() else 0

            # higher score = better move
            return (
                80 * (-opp_moves)      # strongest factor: restrict opponent
                + 20 * my_future_moves  # reward future mobility
                + 3 * jump_score        # prefer longer jumps
                + removal_penalty
            )

        return sorted(moves, key=score, reverse=reverse)

    def apply_move_for_ordering(
        self,
        black: int,
        white: int,
        move: Move,
        player: str,
    ) -> Tuple[int, int]:
        '''
        lightweight helper for move ordering

        applies a move using GameState-compatible board logic
        '''
        state = GameState(black, white, player)
        next_state = state.get_result_state(move)
        return next_state.black_board, next_state.white_board

    def move_distance(self, move: Move) -> int:
        '''
        returns manhattan distance of move (for ordering moves)
        '''
        if move.is_removal():
            return 0

        r1, c1 = move.start
        r2, c2 = move.end
        return abs(r1 - r2) + abs(c1 - c2)

    def evaluate(self, black: int, white: int) -> int:
        '''
        heuristic evaluation function

        combines:
        - mobility difference
        - piece count difference
        - terminal win/loss detection
        '''
        my_moves = len(board_legal_moves(black, white, self.me))
        opp_moves = len(board_legal_moves(black, white, self.opp))

        if opp_moves == 0:
            return 100000
        if my_moves == 0:
            return -100000

        # piece counts
        black_count = black.bit_count()
        white_count = white.bit_count()

        if self.me == "B":
            my_pieces = black_count
            opp_pieces = white_count
        else:
            my_pieces = white_count
            opp_pieces = black_count

        mobility_score = 120 * (my_moves - opp_moves)
        piece_score = 15 * (my_pieces - opp_pieces)

        # extra reward for putting opponent in very tight positions
        pressure_score = 0
        if opp_moves <= 2:
            pressure_score += 40
        if my_moves <= 2:
            pressure_score -= 40

        return mobility_score + piece_score + pressure_score

    def time_up(self) -> bool:
        '''
        checks if time limit is exceeded
        '''
        return (time.time() - self.start_time) >= THINKING_TIME