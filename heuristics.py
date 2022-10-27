import itertools

import numpy as np
import helpers as helper

# Author:      columluc & bernero1
# Date:        20.10.2022
# Description: The heuristics used in searchai.py


PERFECT_TILE_DISTRIBUTION_BOARD = np.array([
        [2**16, 2**15, 2**14, 2**13],
        [2**9,  2**10, 2**11, 2**12],
        [2**8,  2**7,  2**6,  2**5 ],
        [2**1,  2**2,  2**3,  2**4 ]
    ])


def calc_board_heuristic_score(board):
    score = 0

    score += utility_tile_distribution(board)
    score += utility_tiles_empty(board)
    score += utility_highest_tile(board)
    score += utility_top_row_full(board)
    score += 100 * utility_trapped_by_lower(board)

    return score


def utility_tile_distribution(board):
    """
        Retrieves a score for the current tile distribution on the given board.
    """
    score_board = board * PERFECT_TILE_DISTRIBUTION_BOARD
    return np.sum(score_board)


def utility_tiles_empty(board):
    """
        Retrieves a score for the number of empty fields on the given board.
    """
    return helper.get_empty_cnt(board) * 100


def utility_highest_tile(board):
    """
        Retrieves a value for the highest tile on the given board.
    """
    return np.max(board) ** 2


def utility_top_row_full(board):
    """
        Retrieves a value for the top row to be filled on the given board.
    """
    return np.count_nonzero(board[0, :]) * 10000


def utility_trapped_by_lower(board):
    """
        Retrieves a value for trapped tiles which should be merged.
        This score-value is negative.
    """
    neg_score = 0
    for i, j in itertools.product(range(3), range(4)):
        if board[i, j] < board[i-1, j]:
            neg_score += -1 * PERFECT_TILE_DISTRIBUTION_BOARD[i, j]

    return neg_score
