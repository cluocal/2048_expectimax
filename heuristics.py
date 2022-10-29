import itertools

import numpy as np
import helpers as helper

# Author:      columluc & bernero1
# Date:        20.10.2022
# Description: The heuristics used in searchai.py


####################################################
# PARAMETERS
####################################################
d = 2
STRATEGY = np.array([10, 0, 0, 0, 100, 0])
####################################################


def calc_board_heuristic_score(board):
    score = 0

    if STRATEGY[0] > 0:
        score += STRATEGY[0] * utility_tile_distribution(board)
    if STRATEGY[1] > 0:
        score += STRATEGY[1] * utility_tiles_empty(board)
    if STRATEGY[2] > 0:
        score += STRATEGY[2] * utility_highest_tile(board)
    if STRATEGY[3] > 0:
        score += STRATEGY[3] * utility_top_row_full(board)
    if STRATEGY[4] > 0:
        score += STRATEGY[4] * utility_trapped_by_lower(board)
    if STRATEGY[5] > 0:
        score += STRATEGY[5] * utility_ready_to_merge(board)

    return score


def utility_tile_distribution(board):
    """
        Retrieves a score for the current tile distribution on the given board.
    """
    score_board = board * get_perfect_tile_distribution_board()
    return np.sum(score_board)


def utility_tiles_empty(board):
    """
        Retrieves a score for the number of empty fields on the given board.
    """
    return helper.get_empty_cnt(board)


def utility_highest_tile(board):
    """
        Retrieves a value for the highest tile on the given board.
    """
    return np.max(board) ** 2


def utility_top_row_full(board):
    """
        Retrieves a value for the top row to be filled on the given board.
    """
    return np.count_nonzero(board[0, :])


def utility_trapped_by_lower(board):
    """
        Retrieves a value for trapped tiles which should be merged.
        This score-value is negative.
    """
    neg_score = 0
    for i, j in itertools.product(range(3), range(4)):
        if board[i, j] < board[i-1, j]:
            neg_score += -1 * get_perfect_tile_distribution_board()[i, j]

    return neg_score


def utility_ready_to_merge(board):
    """
        Retrieves a value for tiles are next to each other and have the same value.
        Trying to look one step further.
    """
    # ready to merge up
    score_merge_up = 0
    for i, j in itertools.product(range(3), range(4)):
        if board[i, j] == board[i - 1, j]:
            # matches
            score_merge_up += get_perfect_tile_distribution_board()[i, j]
        if board[i, j] == (board[i - 1, j] * 2):
            # matches after +1
            score_merge_up += 0.4 * get_perfect_tile_distribution_board()[i, j]

    score_merge_left = 0
    for i, j in itertools.product(range(4), range(1, 4)):
        if board[i, j] == board[i, j - 1]:
            # matches
            score_merge_left += get_perfect_tile_distribution_board()[i, j - 1]
        if board[i, j] == (board[i, j - 1] * 2):
            # matches after +1
            score_merge_left += 0.3 * get_perfect_tile_distribution_board()[i, j - 1]

    score = 10 * score_merge_up
    score += score_merge_left
    return score


def get_perfect_tile_distribution_board():
    return np.array([
        [2 * 2**(16 * d), 2 * 2**(15 * d), 2 * 2**(14 * d), 2 * 2**(13 * d)],
        [2**(9 * d),  2**(10 * d), 2**(11 * d), 2**(12 * d)],
        [2**(5 * d),  2**(6 * d),  2**(7 * d),  2**(8 * d)],
        [2 ** d, 2 ** (2 * d), 2 ** (3 * d), 2 ** (4 * d)]
    ])
