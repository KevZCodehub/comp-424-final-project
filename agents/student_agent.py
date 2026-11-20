"""Student agent: edit ONLY this file."""
from agents.agent import Agent
from store import register_agent
from helpers import (Move, get_valid_moves, execute_move, check_winner,
                     check_endgame, random_move, copy_state, top_view, LINES)
from constants import *
import numpy as np
import time

@register_agent("student_agent")          # do not change this string
class StudentAgent(Agent):
    def __init__(self):
        """Set up your agent. This runs once per game, before the first move, and must finish
        within INIT_TIME_LIMIT seconds."""
        super().__init__()
        self.name = "StudentAgent"
        self.lines = None # all possible winning lines
        self.turns = 0

    def step(self, board, reserves, player, opponent):
        """Return the Move you want to play.

        Takes: board, reserves - your own copies of the current position.
               player, opponent - your player number (1 or 2) and the other one.
        Agent.step in agents/agent.py explains each argument and the time limit.
        """
        start = time.perf_counter()
        margin = 0.2
        ply = 2 * self.turns + player - 1
        self.turns += 1

        # setting up all possible winninglines on the first step and passes on following steps
        if self.lines is None:
            self.lines = []
            for line in LINES[WIN_LENGTH]:
                blocked = False
                for cell in line:
                    row = cell[0]
                    column = cell[1]
                    if board[row, column, SMALL] == OBSTACLE:
                        blocked = True
                if blocked == False:
                    self.lines.append(line)

        # ALLOW_MOVES and WIN_LENGTH (from constants) are the rule flags of this game.
        # helpers.get_valid_moves / check_winner already respect them; your own
        # move generator and evaluation function must too.
        # TODO: replace with your search. Keep (time.perf_counter() - start) < STEP_TIME_LIMIT - margin.

        
        moves = get_valid_moves(board, reserves, player)
        best_move = moves[0]
        best_score = None
        
        # checking if a next possible move can end the game greedy style and score all possible moves
        for move in moves:
            # stop and just give best possible move at time limit
            if time.perf_counter() - start >= STEP_TIME_LIMIT - margin:
                break

            new_board, new_reserves = copy_state(board, reserves)
            execute_move(new_board, new_reserves, player, move)
            over, winner, reason = check_endgame(new_board, new_reserves, opponent, ply + 1)

            if winner == player:
                return move

            if winner != opponent:
                if best_score is None:
                    best_move = move

                complete = True

                if over:
                    score = 0
                else:
                    replies = get_valid_moves(new_board, new_reserves, opponent)
                    score = None

                    for reply in replies:
                        if time.perf_counter() - start >= STEP_TIME_LIMIT - margin:
                            complete = False
                            break

                        reply_board, reply_reserves = copy_state(new_board, new_reserves)
                        execute_move(reply_board, reply_reserves, opponent, reply)
                        reply_over, reply_winner, reply_reason = check_endgame(
                            reply_board, reply_reserves, player, ply + 2)

                        if reply_over:
                            if reply_winner == player:
                                reply_score = 100000
                            elif reply_winner == opponent:
                                reply_score = -100000
                            else:
                                reply_score = 0
                        else:
                            reply_score = _evaluate(reply_board, self.lines, player, opponent)

                        if score is None:
                            score = reply_score
                        elif reply_score < score:
                            score = reply_score

                if complete == False:
                    break

                if best_score is None:
                    best_score = score
                    best_move = move
                elif score > best_score:
                    best_score = score
                    best_move = move

        return best_move

# score a possible board after our move as h 
def _evaluate(board, lines, player, opponent):
    owners, sizes = top_view(board)
    weights = [0, 1, 10, 100, 100000]
    total = 0

    for line in lines:
        player_count = 0
        opponent_count = 0

        for cell in line:
            row = cell[0]
            column = cell[1]

            if owners[row, column] == player:
                player_count += 1
            if owners[row, column] == opponent:
                opponent_count += 1

        if opponent_count == 0:
            total += weights[player_count]
        if player_count == 0:
            total -= weights[opponent_count]

    return total
