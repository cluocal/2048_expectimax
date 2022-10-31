#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author:      chrn (original by nneonneo)
# Date:        11.11.2016, updated by scik 30.08.2019
# Copyright:   https://github.com/nneonneo/2048-ai
# Description: Helps the user achieve a high score in a real game of 2048 by using a move searcher.
#              This Script initialize the AI and controls the game flow.


# from __future__ import print_function

import time

import numpy as np

import helpers
import heuristics
# import heuristicai as ai #for task 4
import searchai as ai  # for task 5
from HeuristicParams import HeuristicParams


# import heuristicai_SOLUTION as ai #for task 4
# import searchai_SOLUTION as ai #for task 5


def print_board(m):
    for row in m:
        for c in row:
            print('%8d' % c, end=' ')
        print()


def _to_val(c):
    if c == 0: return 0
    return c


def to_val(m):
    return [[_to_val(c) for c in row] for row in m]


def _to_score(c):
    if c <= 1:
        return 0
    return (c - 1) * (2 ** c)


def to_score(m):
    return [[_to_score(c) for c in row] for row in m]


def find_best_move(board, heuristic_params):
    return ai.find_best_move(board, heuristic_params)


def movename(move):
    return ['up', 'down', 'left', 'right'][move]


def play_game(gamectrl):
    score, board, max_val, move_no, avg_moves_per_seconds, avg_move_decision_time_consumption \
        = play_game_and_return(gamectrl, True, -1, None)
    print("###########################  GAME OVER  ###########################")
    print(
        "Final score %d; highest tile %d.; avg mv/sec: %010.2f; avg sec/mv: %010.2f"
        % (score, max_val, avg_moves_per_seconds, avg_move_decision_time_consumption)
    )


def play_game_and_return(gamectrl, verbose_output, max_moves, heuristic_params):
    if heuristic_params is None:
        heuristic_params = HeuristicParams()

    tot_move_decision_time_consumption = 0
    avg_move_decision_time_consumption = 0
    avg_moves_per_seconds = 0

    move_no = 0
    start_time = time.time()
    while 1:
        state = gamectrl.get_status()
        if state == 'ended':
            break
        elif state == 'won':
            time.sleep(0.75)
            gamectrl.continue_game()

        if 0 < max_moves <= move_no:
            break

        move_no += 1
        board = gamectrl.get_board()
        move_decision_start_time = time.time()
        move = find_best_move(board, heuristic_params)
        if move < 0:
            break

        # time calc
        move_end_time = time.time()
        move_rel_time = move_end_time - start_time
        move_decision_time_consumption = move_end_time - move_decision_start_time
        tot_move_decision_time_consumption += move_decision_time_consumption
        avg_move_decision_time_consumption = tot_move_decision_time_consumption / move_no
        avg_moves_per_seconds = 1 / avg_move_decision_time_consumption

        if verbose_output:
            print("%010.6f: Score %d, Move %d: %s, avg mv/s: %010.2f" % (
                move_rel_time, gamectrl.get_score(), move_no, movename(move), avg_moves_per_seconds))

        gamectrl.execute_move(move)

    score = gamectrl.get_score()
    max_val = max(max(row) for row in to_val(board))
    board = gamectrl.get_board()

    return score, board, max_val, move_no, avg_moves_per_seconds, avg_move_decision_time_consumption


def test_2048(gamectrl, n_runs):
    print("Starting 2048 in test-mode ...\n")
    results = []

    # define param-sets
    param_sets = [
        {'id': 212, 'move_limit': 2000, 'd': '1', 'strategy': [10, 0, 0, 1000, 0, 0]},
        {'id': 223, 'move_limit': 2000, 'd': '1', 'strategy': [100, 100, 100, 100, 1, 10]},
        {'id': 232, 'move_limit': 2000, 'd': '1', 'strategy': [100, 10000, 1000, 100, 1, 10]},
        {'id': 240, 'move_limit': 2000, 'd': '2', 'strategy': [100, 10, 10, 10, 0.8, 10]},
        {'id': 241, 'move_limit': 2000, 'd': '2', 'strategy': [1000, 10, 10, 10, 0.8, 10]}
    ]

    # each run out of n_runs with same param-sets
    for n_i in range(1, n_runs + 1):
        print("####################################################################################################################################")
        print("##########################################")
        print("#############   RUN", n_i, "of", n_runs, "  #############")
        print("##########################################\n")
        results = test_run(gamectrl, param_sets, results, n_i)

    helpers.print_test_results(n_runs, param_sets, results)


def test_run(gamectrl, param_sets, results, run_no):
    gamectrl.restart_game()

    # scores for this run
    run_max_score = 0
    run_max_score_param_set = 0
    run_max_score_avg_move_decision_time = 0
    run_scores = []

    # run once with each param-set
    for param_set in param_sets:
        print("\n############################")
        print("###  RUN %d, PARAM-SET %d  ###" % (run_no, param_set["id"]))
        print("############################")
        print("params:")
        print("  move_limit:", param_set["move_limit"])
        print("  d:", param_set["d"])

        # set params
        params = HeuristicParams()
        params.d = int(param_set["d"])
        params.strategy = param_set["strategy"]

        # start run
        score, board, max_val, moves, avg_moves_per_seconds, avg_move_decision_time_consumption \
            = play_game_and_return(gamectrl, False, param_set["move_limit"], params)
        gamectrl.restart_game()

        run_scores.append({
            "param_set_id": param_set["id"],
            "score": score, "max_val": max_val, "moves": moves,
            "avg_moves_per_seconds": avg_moves_per_seconds,
            "avg_move_decision_time_consumption": avg_move_decision_time_consumption
        })
        if score > run_max_score:
            run_max_score = score
            run_max_score_param_set = param_set["id"]
            run_max_score_avg_move_decision_time = avg_move_decision_time_consumption

        print("run scores:")
        print("  final score:", score)
        print("  highest tile:", max_val)
        print("  moves:", moves)
        print("  avg mv/sec:", avg_moves_per_seconds)
        print("  avg sec/mv:", avg_move_decision_time_consumption)
        print("  end board-state:\n", board)

        # run n_i - param_set_i finished

    results.append({
        "run": run_no, "max_score": run_max_score,
        "max_score_param_set": run_max_score_param_set,
        "max_score_avg_move_decision_time": run_max_score_avg_move_decision_time,
        "run_scores": run_scores
    })
    print("\n")  # run n_i finished

    return results


def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description="Use the AI to play 2048 via browser control")
    parser.add_argument('-p', '--port', help="Port number to control on (default: 32000 for Firefox, 9222 for Chrome)",
                        type=int)
    parser.add_argument('-b', '--browser',
                        help="Browser you're using. Only Firefox with the Remote Control extension, and Chrome with remote debugging (default), are supported right now.",
                        default='chrome', choices=('firefox', 'chrome'))
    parser.add_argument('-k', '--ctrlmode',
                        help="Control mode to use. If the browser control doesn't seem to work, try changing this.",
                        default='hybrid', choices=('keyboard', 'fast', 'hybrid'))
    parser.add_argument('-t', '--testmode', help="Test-mode (multiple runs with different parameters)", default=False,
                        type=bool)
    parser.add_argument('-n', '--nTestRuns', help="Amount of test-runs", default=1, type=int)

    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)

    if args.browser == 'firefox':
        from ffctrl import FirefoxRemoteControl
        if args.port is None:
            args.port = 32000
        ctrl = FirefoxRemoteControl(args.port)
    elif args.browser == 'chrome':
        from chromectrl import ChromeDebuggerControl
        if args.port is None:
            args.port = 9222
        ctrl = ChromeDebuggerControl(args.port)

    if args.ctrlmode == 'keyboard':
        from gamectrl import Keyboard2048Control
        gamectrl = Keyboard2048Control(ctrl)
    elif args.ctrlmode == 'fast':
        from gamectrl import Fast2048Control
        gamectrl = Fast2048Control(ctrl)
    elif args.ctrlmode == 'hybrid':
        from gamectrl import Hybrid2048Control
        gamectrl = Hybrid2048Control(ctrl)

    if gamectrl.get_status() == 'ended':
        gamectrl.restart_game()

    if args.testmode:
        if args.nTestRuns is None:
            args.nTestRuns = 1
        test_2048(gamectrl, args.nTestRuns)
    else:
        play_game(gamectrl)


if __name__ == '__main__':
    import sys
    from sys import exit

    exit(main(sys.argv[1:]))
