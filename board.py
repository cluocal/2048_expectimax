import numpy as np


def board_equals(board, newboard):
    """
    Check if two boards are equal
    """
    return  (newboard == board).all()

def board_highestTile(board):
    max = np.zeros(shape=(0, 3))
    for i in len(board):
        for k in len(board[i]):
            if board[i][k] > max[0]:
                max[0] = max
                max[1] = i
                max[2] = k
    return max

def board_countEmptyTiles(board):
    amount = 0
    for i in len(board):
        for k in len(board[i]):
            if board[i][k] > 0:
                amount += 1

    return amount

