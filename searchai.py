import itertools

import numpy as np

import game
import sys
import helpers as helper
import heuristics
from heuristics import calc_board_heuristic_score
import multiprocessing as mp


# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   Algorithm from https://github.com/nneonneo/2048-ai
# Description: The logic to beat the game. Based on expectimax algorithm.


UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
MOVE_ARGS = [UP, DOWN, LEFT, RIGHT]
STATE_MAX, STATE_CHANCE = 1, 2

pool = None


def find_best_move(board, heuristic_params):
    """
        retrieves the best move for the next turn.
    """
    global pool
    results = []

    empty_cnt = helper.get_empty_cnt(board)
    if empty_cnt <= 1:
        max_depth = 3
    elif empty_cnt <= 4:
        max_depth = 2
    else:
        max_depth = 1

    # FAST
    #max_depth = 1

    if pool is None:
        pool = mp.Pool(processes=len(MOVE_ARGS))

    for move in MOVE_ARGS:
        results.append(pool.apply_async(score_toplevel_move, (move, board, max_depth, heuristic_params)))

    results = [ret.get() for ret in results]
    best_move = results.index(max(results))

    # for m in MOVE_ARGS:
    #     print("move: %d score: %.4f" % (m, results[m]))

    return best_move


def score_toplevel_move(move, board, max_depth, heuristic_params):
    """
        Entry-point to score the first move.
    """
    board_after = execute_move(move, board)

    ##################
    # PRECONDITIONS
    ##################
    if helper.boards_equal(board, board_after):
        # move does not change the board
        return 0

    if heuristics.utility_trapped_by_lower(board_after, heuristic_params) <= (- 2**13) and max_depth <= 2:
        # trapped tiles should be merged (only for first row, <= - 2**13)!
        max_depth += 1
    # elif not (board_after[0, 0] > board_after[0, 1] > board_after[0, 2] > board_after[0, 3]):
    #     # trying to get perfect order in first row
    #     max_depth += 1

    # Implement the Expectimax Algorithm.
    # 1.) Start the recursion until it reach a certain depth
    # 2.) When you don't reach the last depth, get all possible board states and
    #     calculate their scores dependence of the probability this will occur. (recursively)
    # 3.) When you reach the leaf calculate the board score with your heuristic.

    return expectimax_value(board_after, STATE_CHANCE, max_depth, heuristic_params)


def expectimax_value(board, state, remaining_depth, heuristic_params):
    if remaining_depth <= 0:  # leaf-node reached!
        return calc_board_heuristic_score(board, heuristic_params)

    elif state == STATE_MAX:
        return max_value(board, remaining_depth, heuristic_params)

    elif state == STATE_CHANCE:
        return chance_value(board, remaining_depth, heuristic_params)

    else:
        print("INVALID STATE IN expectimax_value!")
        return -1


def max_value(board, remaining_depth, heuristic_params):
    max_val = 0

    # try all moves and get max value
    for move in MOVE_ARGS:
        board_after = execute_move(move, board)
        if not helper.boards_equal(board_after, board):
            val = expectimax_value(board_after, STATE_CHANCE, remaining_depth - 1, heuristic_params)
            if val > max_val:
                max_val = val

    return max_val


def chance_value(board, remaining_depth, heuristic_params):
    return chance_value_fast(board, remaining_depth, heuristic_params)

    #######################################
    # REPLACED THROUGH FASTER CALCULATION
    #######################################

    # chance = 0
    # successor_cnt = 0
    #
    # # iterate over all possible tile-spawn-points
    # for i in range(4):
    #     for j in range(4):
    #         if board[i, j] == 0:
    #             successor_cnt += 1
    #             # calc for spawning a 2
    #             board_after = helper.set_board_value(board, i, j, 2)
    #             chance += 0.9 * expectimax_value(board_after, STATE_MAX, remaining_depth, heuristic_params)
    #             # calc for spawning a 4
    #             board_after = helper.set_board_value(board, i, j, 4)
    #             chance += 0.1 * expectimax_value(board_after, STATE_MAX, remaining_depth, heuristic_params)
    #
    # return chance / successor_cnt


def chance_value_fast(board, remaining_depth, heuristic_params):
    spawn_board = np.zeros_like(board)

    # get all possible tile-spawn-points
    for i, j in itertools.product(range(4), range(4)):
        if board[i, j] == 0:
            spawn_board[i, j] = 1

    # get values for spawn-points
    spawn_board = helper.get_board_tile_distribution_values(spawn_board, heuristic_params)

    # calc chance only for n worst spawn-points
    n = 4
    if remaining_depth >= 3:
        n = 2
    elif remaining_depth >= 2:
        n = 3

    # continue calc for these n spawn-points
    chance = 0
    successor_cnt = 0
    for n_i in range(n):
        row, col = helper.get_nth_highest_val_idx(spawn_board, n_i)
        successor_cnt += 1
        # calc for spawning a 2
        board_after = helper.set_board_value(board, row, col, 2)
        chance += 0.9 * expectimax_value(board_after, STATE_MAX, remaining_depth, heuristic_params)
        # calc for spawning a 4
        board_after = helper.set_board_value(board, row, col, 4)
        chance += 0.1 * expectimax_value(board_after, STATE_MAX, remaining_depth, heuristic_params)

    return chance / successor_cnt


def execute_move(move, board):
    """
        Move and return the grid without a new random tile.
        It won't affect the state of the game in the browser.
    """
    if move == UP:
        return game.merge_up(board)
    elif move == DOWN:
        return game.merge_down(board)
    elif move == LEFT:
        return game.merge_left(board)
    elif move == RIGHT:
        return game.merge_right(board)
    else:
        sys.exit("No valid move")
