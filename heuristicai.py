import random

import numpy as np

import game
import sys

# Author:				chrn (original by nneonneo)
# Date:				11.11.2016
# Description:			The logic of the AI to beat the game.

move_no = 0
UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
last_move = LEFT
next_move = None
board_before = None
board_before_1 = None

corner_mode = LEFT


def find_best_move(board):
    global move_no
    global last_move
    global next_move
    global board_before
    global board_before_1
    global corner_mode
    # ----------------------------------------------

    if board[0, 0] != 0 and board[0, 0] < board[0, 1] and move_no > 5:
        print("########################## AHH, SHIT!    TILE APPEARED AT TOP-LEFT CORNER :(  ##########################")
        print(board_before_1)
        print("\n")
        print(board_before)
        print("MOVE: ", last_move)
        print("\n")
        print(board)
        print("\n\n")
        return -1

    print("CORNER-MODE: ", "LEFT" if corner_mode == LEFT else "RIGHT")

    if next_move is not None:
        if next_move == UP and not is_line_full(board, 0):
            # top left corner would be lost
            best_move = LEFT
        else:
            best_move = next_move

        next_move = None

    else:
        if has_to_fill_last_in_line(board, 0):
            # change corner_mode if only last element must be merged
            corner_mode = RIGHT
            best_move, next_move = RIGHT, UP
        elif has_merge_up_shifted(board, 0) and is_line_full(board, 0):
            best_move = RIGHT
            next_move = UP
        else:
            # try move to merge fields
            best_move = find_merging_move(board)

            if best_move == -1:
                # use the top_corner_strategy if nothing of the above applies
                best_move = top_corner_strategy(board)

    # ----------------------------------------------
    # POST-CHECK
    board_after = execute_move(best_move, board)
    if corner_mode == LEFT:
        if board_after[0, 0] == 0:
            if not np.any(board_after[1:, 0]):  # all zeros left line except line 0
                best_move = top_corner_strategy(board)
            else:
                best_move = LEFT  # must go left, otherwise TOP-LEFT corner lost
    elif corner_mode == RIGHT:
        if board_after[0, 3] == 0 or not is_line_full(board, 0):
            # last element merged, change corner_mode back
            corner_mode = LEFT
        if board_after[0, 0] == 0:
            # prevent from losing first line corner (TOP-LEFT)
            best_move = LEFT

    # ----------------------------------------------
    last_move = best_move
    board_before_1 = board_before
    board_before = board
    move_no = move_no + 1
    return best_move


def find_best_move_random_agent():
    return random.choice([UP,DOWN,LEFT,RIGHT])


def top_corner_strategy(board):
    global next_move
    move = corner_mode

    if last_move == corner_mode:
        move = UP
    elif last_move == UP:
        move = corner_mode
    elif last_move == (RIGHT if corner_mode == LEFT else LEFT):
        # was opposite of corner_mode move
        if is_board_unchanged(board) and \
                boards_equal(board, execute_move(LEFT, board)) and \
                boards_equal(board, execute_move(RIGHT, board)) and \
                boards_equal(board, execute_move(UP, board)):
            move = DOWN  # only down others not possible
            next_move = UP  # to be sure it moves up
        else:
            move = corner_mode
    elif last_move == DOWN:
        move = UP

    if is_board_unchanged(board) and (last_move == corner_mode or last_move == UP):
        move = (RIGHT if corner_mode == LEFT else LEFT)  # opposite of corner_mode move

    return move


def execute_move(move, board):
    """
    move and return the grid without a new random tile 
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


def is_board_unchanged(board):
    return boards_equal(board, board_before) and boards_equal(board_before, board_before_1)


def boards_equal(board_1, board_2):
    return np.array_equal(board_1, board_2)


def has_stairs_top_left(board):
    return \
        is_line_full(board, 0) \
        and np.all(board[1, :3]) \
        and np.all(board[2, :2]) \
        and np.all(board[3, :1])


def has_merge_up_shifted(board, upper_line):
    top_line_before = 0
    for el in board[upper_line]: top_line_before = top_line_before + el

    board = execute_move(RIGHT, board)
    board = execute_move(UP, board)

    top_line = 0
    for el in board[upper_line]: top_line = top_line + el

    return top_line > top_line_before


def has_to_fill_last_in_line(board, line_no):
    ret = False

    if corner_mode == LEFT:
        if not is_line_full(board, line_no):
            return False
        # check for perfect line
        ret = board[line_no, 0] >= 256 and \
              board[line_no, 1] == (board[line_no, 0] / 2) and \
              board[line_no, 2] == (board[line_no, 1] / 2) and \
              board[line_no, 2] > board[line_no, 3]
    # else:
    #     if board[line_no, 0] == 0 or board[line_no, 3] < 256:
    #         return False
    #     ret = board[line_no, 0] < board[line_no, 1] < board[line_no, 2] < board[line_no, 3]

    ##########################
    # disable this strategy
    ##########################
    #ret = False
    return ret


def is_line_full(board, line_no):
    """
        Retrieves true if the given line has 4 elements.

        Args:
            board: the current board
            line_no: the line-number to test (beginning with 0)
        Returns:
            boolean: true if line has 4 elements
    """
    return np.all(board[line_no, :])

def find_merging_move(board):
    best_move = -1
    sum_before = np.sum(board)

    board_after = execute_move(corner_mode, board)
    sum_move_corner_mode = np.sum(board_after)
    sum_move_corner_mode_top_line = np.sum(board_after[0, :])

    board_after = execute_move(UP, board)
    sum_move_UP = np.sum(board_after)
    sum_move_UP_top_line = np.sum(board_after[0, :])

    if sum_move_corner_mode > sum_before or sum_move_UP > sum_before:
        # some tiles merged after exec

        if sum_move_corner_mode == sum_move_UP:

            if sum_move_corner_mode_top_line > sum_move_UP_top_line:
                best_move = corner_mode
            elif sum_move_corner_mode_top_line < sum_move_UP_top_line:
                best_move = UP

        elif sum_move_corner_mode > sum_move_UP:
            best_move = corner_mode
        else:
            best_move = UP


    return best_move