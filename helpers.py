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


def get_board_tile_distribution_values(board, heuristic_params):
    return board * get_perfect_tile_distribution_board(heuristic_params)


def get_nth_highest_val_idx(board, n):
    row, col = np.unravel_index(np.argsort(board.ravel()), board.shape)
    row, col = row[::-1], col[::-1]
    return row[n], col[n]


def print_test_results(n_runs, param_sets, results):
    print(
        "####################################################################################################################################")
    print("ALL RUNS (%d) FINISHED!" % n_runs)

    print("\nPARAM_SETS:")
    for param_set in param_sets:
        print("  ", param_set["id"], " --> ", param_set)

    print("\nBEST SCORES:")
    best_score = 0
    best_score_run = 0
    for result in results:
        if result["max_score"] > best_score:
            best_score = result["max_score"]
            best_score_run = result["run"]
        print("  run %d best score:  %d with %.2f sec/mv    (in param set: %d)"
              % (result["run"], result["max_score"],
                 result["max_score_avg_move_decision_time"], result["max_score_param_set"])
              )

    print("\nPARAM_SET AVG SCORES:")
    best_set_avg_score = 0
    best_set_avg_id = 0

    for param_set in param_sets:
        param_set_avg_score = 0
        param_set_avg_move_decision_time_consumption = 0
        candidates = 0
        for result in results:
            for score in result["run_scores"]:
                if score["param_set_id"] == param_set["id"]:
                    param_set_avg_score += score["score"]
                    param_set_avg_move_decision_time_consumption += score["avg_move_decision_time_consumption"]
                    candidates += 1

        # calc avg
        param_set_avg_score = param_set_avg_score / candidates
        param_set_avg_move_decision_time_consumption = param_set_avg_move_decision_time_consumption / candidates
        if param_set_avg_score > best_set_avg_score:
            best_set_avg_score = param_set_avg_score
            best_set_avg_id = param_set["id"]
        print("  param_set %d avg score:  %.2f with %.2f sec/mv"
              % (param_set["id"], param_set_avg_score,
                 param_set_avg_move_decision_time_consumption)
              )

    print("\n\n##############")
    print("BEST PARAM-SET:  %d (avg score: %.2f)" % (best_set_avg_id, best_set_avg_score))
    print("OVERALL BEST SCORE:  %d (run %d)" % (best_score, best_score_run))
    print(
        "\n####################################################################################################################################")
