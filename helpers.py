import numpy as np

from heuristics import get_perfect_tile_distribution_board

# Author:      columluc & bernero1
# Date:        20.10.2022
# Description: The heuristics used in searchai.py


def boards_equal(board_1, board_2):
    """
        Checks if the two given boards are equal
    """
    return np.array_equal(board_1, board_2)  # or: (board_1 == board_2).all()


def get_empty_cnt(board):
    return 16 - np.count_nonzero(board)


def set_board_value(board, row, col, val):
    board_after = board.copy()
    board_after[row, col] = val
    return board_after


def get_board_tile_distribution_values(board):
    return board * get_perfect_tile_distribution_board()


def get_nth_highest_val_idx(board, n):
    row, col = np.unravel_index(np.argsort(board.ravel()), board.shape)
    row, col = row[::-1], col[::-1]
    return row[n], col[n]
