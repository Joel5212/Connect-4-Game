import copy
import time
from flask import Flask, request, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# global variables
more_than_five_seconds = False
winning_pieces = []


def alpha_beta_search(board):
    player_turn = True

    start_time = time.time()

    # alpha is the best already explored option to the root for the maximizer
    alpha = -1000000

    # alpha is the best already explored option to the root for the minimizer
    beta = 1000000

    # first maximizer call enters the stack
    move = max_value(board, alpha, beta,
                     player_turn, -1, start_time)

    return move


def calc_heuristic_value_for_case(board, initial_heuristic_value, decrement_weight, add_to_i_and_j_list, i, j, is_row_check):

    herustic_value = initial_heuristic_value

    for add_to_i, add_to_j in add_to_i_and_j_list:

        increment = 1

        try:
            while board[i+add_to_i+increment][j+add_to_j] == "-":
                herustic_value += decrement_weight
                increment += 1
            continue
        except IndexError:
            continue

    return herustic_value


def addPositionalWeight(j, i, board, computer_piece, player_piece):

    positional_weights = [
        [3, 4, 6, 10, 6, 4, 3],
        [5, 8, 11, 20, 11, 8, 5],
        [7, 10, 16, 25, 16, 10, 7],
        [7, 10, 16, 25, 16, 10, 7],
        [5, 8, 11, 20, 11, 8, 5],
        [3, 4, 6, 10, 6, 4, 3]
    ]

    if board[j][i] == computer_piece:
        return positional_weights[j][i]
    elif board[j][i] == player_piece:
        return -positional_weights[j][i]


def calc_heuristic_value(board, status):

    if status == "Nf":

        heuristic_value = 0

        player_piece = "X"
        computer_piece = "O"

        for i in range(0, len(board[0])):

            column_check_complete = False

            positional_weight_added = False

            for j in range(0, len(board[0])):
                try:
                    if not positional_weight_added and j < len(board) and board[j][i] != '-':
                        heuristic_value += addPositionalWeight(
                            j, i, board, computer_piece, player_piece)
                        positional_weight_added = True

                    if j == 0 and board[j][i] != '-':
                        column_check_complete = True

                    if not column_check_complete:

                        # two consecutive computer pieces in a column with open spot
                        # if
                        # -      #-
                        # -      #-
                        # X  or  #X
                        # X      #X
                        # O
                        if j > 1 and board[j-1][i] == "-" and computer_piece == board[j][i] == board[j+1][i] and (j == len(board)-2 or board[j+2][i] == player_piece):
                            heuristic_value += 50
                            column_check_complete = True

                        # three consecutive computer pieces in a column with open spot
                        # if
                        # -     #-
                        # X     #X
                        # X  or #X
                        # X     #X
                        # O
                        elif j > 0 and board[j-1][i] == "-" and computer_piece == board[j][i] == board[j+1][i] == board[j+2][i] and (j == len(board)-3 or board[j+3][i] == player_piece):
                            heuristic_value += 500
                            column_check_complete = True

                        # two consecutive player pieces in a column with open spot
                        # if
                        # -     #-
                        # O or  #O
                        # O     #O
                        # X
                        elif j > 1 and board[j-1][i] == "-" and player_piece == board[j][i] == board[j+1][i] and (j == len(board)-2 or board[j+2][i] == computer_piece):
                            heuristic_value -= 50
                            column_check_complete = True
                        # three consecutive player pieces in a column with open spot
                        # if
                        # -    #-
                        # O    #O
                        # O or #O
                        # O    #O
                        # X
                        elif j > 0 and board[j-1][i] == "-" and player_piece == board[j][i] == board[j+1][i] == board[j+2][i] and (j == len(board)-3 or board[j+3][i] == computer_piece):
                            heuristic_value -= 500
                            column_check_complete = True
                except IndexError:
                    column_check_complete = True
                    pass

                try:
                    # ----two consecutive computer pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if XX--
                        if computer_piece == board[i][j] == board[i][j+1] and board[i][j+2] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 50, -5, [(0, 2), (0, 3)], i, j, True)

                        # if X-X-
                        elif computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 40, -4, [(0, 1), (0, 3)], i, j, True)

                    # if anywhere
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            # if --XXO
                            if computer_piece == board[i][j+1] == board[i][j+2] and board[i][j+3] == player_piece and board[i][j-1] == "-" and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, -1), (0, 0)], i, j, True)

                            # if OXX--
                            if computer_piece == board[i][j] == board[i][j+1] and board[i][j-1] == player_piece and board[i][j+2] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, 2), (0, 3)], i, j, True)

                            # if OX-X-
                            if board[i][j-1] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, 1), (0, 3)], i, j, True)

                            # if -X-X-
                            if computer_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1), (0, 3)], i, j, True)

                            # if -X-XO
                            if board[i][j+3] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][-1] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1)], i, j, True)

                        if j < len(board[0]) - 2:

                            # if -XX-
                            if computer_piece == board[i][j] == board[i][j+1] and board[i][j-1] == "-" and board[i][j+2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, -1), (0, 2)], i, j, True)

                            # if X--X
                            if computer_piece == board[i][j-1] == board[i][j+2] and board[i][j] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 30, -3, [(0, 0), (0, 1)], i, j, True)

                        # if end
                        elif j == len(board[0]) - 3:
                            # if --XX
                            if computer_piece == board[i][j+1] == board[i][j+2] and board[i][j] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, 0), (0, -1)], i, j, True)

                            # if -X-X
                            elif computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1)], i, j, True)

                    # ----three consecutive computer pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if XXX-
                        if computer_piece == board[i][j] == board[i][j+1] == board[i][j+2] and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 500, -50, [(0, 3)], i, j, True)

                    # if anywhere
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            if computer_piece == board[i][j] == board[i][j+1] == board[i][j+2]:
                                # if -XXXO
                                if player_piece == board[i][j+3] and board[i][j-1] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, -1)], i, j, True)

                                # if OXXX-
                                if player_piece == board[i][j-1] and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, 3)], i, j, True)

                                # if -XXX-
                                if board[i][j-1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, -1), (0, 3)], i, j, True)

                        if j < len(board[0]) - 2:

                            # if X-XX
                            if computer_piece == board[i][j-1] == board[i][j+1] == board[i][j+2] and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 400, -40, [(0, 0)], i, j, True)

                            # if XX-X
                            if computer_piece == board[i][j-1] == board[i][j] == board[i][j+2] and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 400, -40, [(0, 1)], i, j, True)

                        # if -XXX
                        elif j == len(board[0]) - 2:
                            if computer_piece == board[i][j-1] == board[i][j] == board[i][j+1] and board[i][j-2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 500, -50, [(0, -2)], i, j, True)

                    # ----two consecutive player pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if OO--
                        if player_piece == board[i][j] == board[i][j+1] and board[j+2] == "-" and board[j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -50, 5, [(0, 2), (0, 3)], i, j, True)

                        # if O-O-
                        elif player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -40, 4, [(0, 1), (0, 3)], i, j, True)

                    # if middle
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            # if --OOX
                            if player_piece == board[i][j+1] == board[i][j+2] and board[i][j+3] == computer_piece and board[i][j-1] == "-" and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, -1), (0, 0)], i, j, True)

                            # if XOO--
                            if player_piece == board[i][j] == board[i][j+1] and board[i][j-1] == computer_piece and board[i][j+2] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, 2), (0, 3)], i, j, True)

                            # if XO-O-
                            if board[i][j-1] == computer_piece and player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, 1), (0, 3)], i, j, True)

                            # if -O-O-
                            if player_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1), (0, 3)], i, j, True)

                            # if -O-OX
                            if board[i][j+3] == computer_piece and player_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1)], i, j, True)

                        if j < len(board[0]) - 2:

                            # if -OO-
                            if player_piece == board[i][j] == board[i][j+1] and board[i][j-1] == "-" and board[i][j+2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, -1), (0, 2)], i, j, True)

                            # if O--O
                            if player_piece == board[i][j-1] == board[i][j+2] and board[i][j] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -30, 3, [(0, 0), (0, 1)], i, j, True)

                        # if end
                        if j == len(board[0]) - 3:

                            # if --OO
                            if player_piece == board[i][j+1] == board[i][j+2] and board[i][j] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, 0), (0, -1)], i, j, True)

                            # if -O-O
                            elif player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1)], i, j, True)

                    # ----three consecutive player pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if OOO-
                        if player_piece == board[i][j] == board[i][j+1] == board[i][j+2] and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -500, 50, [(0, 3)], i, j, True)

                    # if middle
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            if player_piece == board[i][j] == board[i][j+1] == board[i][j+2]:

                                # if -OOOX
                                if computer_piece == board[i][j+3] and board[i][j-1] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, -1)], i, j, True)

                                # if XOOO-
                                if computer_piece == board[i][j-1] and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, 3)], i, j, True)

                                # if -OOO-
                                if board[i][j-1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, -1), (0, 3)], i, j, True)

                        if j < len(board[0]) - 2:

                            # if O-OO
                            if player_piece == board[i][j-1] == board[i][j+1] == board[i][j+2] and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -400, 40, [(0, 0)], i, j, True)

                            # if OO-O
                            if player_piece == board[i][j-1] == board[i][j] == board[i][j+2] and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -400, 40, [(0, 1)], i, j, True)

                        # -OOO
                        elif j == len(board[0]) - 2:
                            if player_piece == board[i][j-1] == board[i][j] == board[i][j+1] and board[i][j-2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -500, 50, [(0, -2)], i, j, True)

                except IndexError:
                    pass

                if j == 0 and i < 4:

                    i_j_values = None

                    if i == 0:
                        i_j_values = [(0, 0)]
                    else:
                        i_j_values = [(i, 0), (0, i)]

                    for i_value, j_value in i_j_values:

                        temp_i_value = (len(board)-1) - i_value

                        row_increment = 0

                        col_increment = 0

                        z = 0

                        while z < 4:
                            if z == 0:
                                # if
                                # X
                                #  X
                                #   -
                                #    -
                                try:
                                    if computer_piece == board[i_value][j_value] == board[i_value+1][j_value+1] and board[i_value+2][j_value+2] == "-" and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(2, 2), (3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   -
                                #  X
                                # X
                                try:
                                    if temp_i_value-3 > -1 and computer_piece == board[temp_i_value][j_value] == board[temp_i_value-1][j_value+1] and board[temp_i_value-2][j_value+2] == "-" and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(-2, 2), (-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  -
                                #   X
                                #    -
                                try:
                                    if computer_piece == board[i_value][j_value] == board[i_value+2][j_value+2] and board[i_value+1][j_value+1] == "-" and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(1, 1), (3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   X
                                #  -
                                # X
                                try:
                                    if temp_i_value-3 > -1 and computer_piece == board[temp_i_value][j_value] == board[temp_i_value-2][j_value+2] and board[temp_i_value-1][j_value+1] == "-" and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(-1, 1), (-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  X
                                #   X
                                #    -
                                try:
                                    if computer_piece == board[i_value][j_value] == board[i_value+1][j_value+1] == board[i_value+2][j_value+2] and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   X
                                #  X
                                # X
                                try:
                                    if temp_i_value-3 > -1 and computer_piece == board[temp_i_value][j_value] == board[temp_i_value-1][j_value+1] == board[temp_i_value-2][j_value+2] and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  O
                                #   -
                                #    -
                                try:
                                    if player_piece == board[i_value][j_value] == board[i_value+1][j_value+1] and board[i_value+2][j_value+2] == "-" and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(2, 2), (3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   -
                                #  O
                                # O
                                try:
                                    if temp_i_value-3 > -1 and player_piece == board[temp_i_value][j_value] == board[temp_i_value-1][j_value+1] and board[temp_i_value-2][j_value+2] == "-" and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(-2, 2), (-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  -
                                #   O
                                #    -
                                try:
                                    if player_piece == board[i_value][j_value] == board[i_value+2][j_value+2] and board[i_value+1][j_value+1] == "-" and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(1, 1), (3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   O
                                #  -
                                # O
                                try:
                                    if temp_i_value-3 > -1 and player_piece == board[temp_i_value][j_value] == board[temp_i_value-2][j_value+2] and board[temp_i_value-1][j_value+1] == "-" and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(-1, 1), (-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  O
                                #   O
                                #    -
                                try:
                                    if player_piece == board[i_value][j_value] == board[i_value+1][j_value+1] == board[i_value+2][j_value+2] and board[i_value+3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(3, 3)], i_value, j_value, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   O
                                #  O
                                # O
                                try:
                                    if temp_i_value-3 > -1 and player_piece == board[temp_i_value][j_value] == board[temp_i_value-1][j_value+1] == board[temp_i_value-2][j_value+2] and board[temp_i_value-3][j_value+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(-3, 3)], temp_i_value, j_value, False)
                                except IndexError:
                                    pass

                            if z == 1 or z == 2:

                                # if
                                # -
                                #  -
                                #   X
                                #    X
                                #     O

                                try:
                                    if computer_piece == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == player_piece and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (1, 1)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    -
                                #   X
                                #  X
                                # O
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] and board[temp_i_value-row_increment][j_value+col_increment] == player_piece and board[temp_i_value-row_increment-3][j_value+col_increment+3] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(-3, 3), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  X
                                #   X
                                #    -
                                #     -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] and board[i_value+row_increment][j_value+col_increment] == player_piece and board[i_value+row_increment+3][j_value+col_increment+3] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(3, 3), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     O
                                #    X
                                #   X
                                #  -
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == player_piece and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(-1, 1), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  X
                                #   -
                                #    X
                                #     -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == player_piece and board[i_value+row_increment+2][j_value+col_increment+2] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(2, 2), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    X
                                #   -
                                #  X
                                # O
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == player_piece and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(-2, 2), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  X
                                #   -
                                #    X
                                #     O
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == player_piece and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     O
                                #    X
                                #   -
                                #  X
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == player_piece and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(-2, 2), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  X
                                #   -
                                #    X
                                #     -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == "-" and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(4, 4), (0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    X
                                #   -
                                #  X
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 40, -4, [(-4, 4), (-2, 2), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  X
                                #   X
                                #    X
                                #     O
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and player_piece == board[i_value+row_increment+4][j_value+col_increment+4] and board[i_value+row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     O
                                #    X
                                #   X
                                #  X
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and player_piece == board[temp_i_value-row_increment-4][j_value+col_increment+4] and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  X
                                #   X
                                #    X
                                #     -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and player_piece == board[i_value+row_increment][j_value+col_increment] and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    X
                                #   X
                                #  X
                                # O
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and player_piece == board[temp_i_value-row_increment][j_value+col_increment] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  X
                                #   X
                                #    X
                                #     -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    X
                                #   X
                                #  X
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  -
                                #   O
                                #    O
                                #     X
                                try:
                                    if player_piece == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == computer_piece and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (1, 1)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    -
                                #   O
                                #  O
                                # X
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] and board[temp_i_value-row_increment][j_value+col_increment] == computer_piece and board[temp_i_value-row_increment-3][j_value+col_increment+3] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(-3, 3), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  O
                                #   O
                                #    -
                                #     -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] and board[i_value+row_increment][j_value+col_increment] == computer_piece and board[i_value+row_increment+3][j_value+col_increment+3] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(3, 3), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     X
                                #    O
                                #   O
                                #  -
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == computer_piece and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(-1, 1), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  O
                                #   -
                                #    O
                                #     -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == computer_piece and board[i_value+row_increment+2][j_value+col_increment+2] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(2, 2), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    O
                                #   -
                                #  O
                                # X
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == computer_piece and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(-2, 2), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  O
                                #   -
                                #    O
                                #     X
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == computer_piece and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     X
                                #    O
                                #   -
                                #  O
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == computer_piece and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(-2, 2), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  O
                                #   -
                                #    O
                                #     -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+4][j_value+col_increment+4] == "-" and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(4, 4), (0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    O
                                #   -
                                #  O
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-" and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -40, 4, [(-4, 4), (-2, 2), (0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  O
                                #   O
                                #    O
                                #     X
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and computer_piece == board[i_value+row_increment+4][j_value+col_increment+4] and board[i_value+row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     X
                                #    O
                                #   O
                                #  O
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and computer_piece == board[temp_i_value-row_increment-4][j_value+col_increment+4] and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  O
                                #   O
                                #    O
                                #     -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and computer_piece == board[i_value+row_increment][j_value+col_increment] and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    O
                                #   O
                                #  O
                                # X
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and computer_piece == board[temp_i_value-row_increment][j_value+col_increment] and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  O
                                #   O
                                #    O
                                #     -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0), (4, 4)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #     -
                                #    O
                                #   O
                                #  O
                                # -
                                try:
                                    if temp_i_value-row_increment-4 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-4][j_value+col_increment+4] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0), (-4, 4)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                            if z == 1 or z == 2 or z == 3:

                                # if
                                # -
                                #  X
                                #   X
                                #    -
                                try:
                                    if computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+3][j_value+col_increment+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (3, 3)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   X
                                #  X
                                # -
                                try:
                                    if temp_i_value-row_increment-3 > -1 and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-3][j_value+col_increment+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (-3, 3)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  -
                                #   -
                                #    X
                                try:
                                    if computer_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+1][j_value+col_increment+1] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 30, -3, [(1, 1), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   -
                                #  -
                                # X
                                try:
                                    if temp_i_value-row_increment-3 > -1 and computer_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 30, -3, [(0, 0), (-3, 3)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                # -
                                #  -
                                #   X
                                #    X
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and computer_piece == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (1, 1)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   X
                                #  -
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and computer_piece == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (-1, 1)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                # -
                                #  X
                                #   -
                                #    X
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   -
                                #  X
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 50, -5, [(0, 0), (-2, 2)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  -
                                #   X
                                #    X
                                try:
                                    if computer_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 400, -40, [(1, 1)], i_value+row_increment, j_value+col_increment, False)

                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   X
                                #  -
                                # X
                                try:
                                    if temp_i_value-row_increment-3 > -1 and computer_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 400, -40, [(-1, 1)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # X
                                #  X
                                #   -
                                #    X
                                try:
                                    if computer_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 400, -40, [(2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   -
                                #  X
                                # X
                                try:
                                    if temp_i_value-row_increment-3 > -1 and computer_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 400, -40, [(-2, 2)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                #  -
                                #   X
                                #    X
                                #     X
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and computer_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    X
                                #   X
                                #  X
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and computer_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, 500, -50, [(0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # -
                                #  O
                                #   O
                                #    -
                                try:
                                    if player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+3][j_value+col_increment+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (3, 3)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    -
                                #   O
                                #  O
                                # -
                                try:
                                    if temp_i_value-row_increment-3 > -1 and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-3][j_value+col_increment+3] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (-3, 3)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  -
                                #   -
                                #    O
                                try:
                                    if player_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+1][j_value+col_increment+1] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -30, 3, [(1, 1), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   -
                                #  -
                                # O
                                try:
                                    if temp_i_value-row_increment-3 > -1 and player_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -30, 3, [(0, 0), (-3, 3)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                # -
                                #  -
                                #   O
                                #    O
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and player_piece == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (1, 1)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   O
                                #  -
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and player_piece == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (-1, 1)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                # -
                                #  O
                                #   -
                                #    O
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-" and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   -
                                #  O
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-" and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -50, 5, [(0, 0), (-2, 2)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  -
                                #   O
                                #    O
                                try:
                                    if player_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -400, 40, [(1, 1)], i_value+row_increment, j_value+col_increment, False)

                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   O
                                #  -
                                # O
                                try:
                                    if temp_i_value-row_increment-3 > -1 and player_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-1][j_value+col_increment+1] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -400, 40, [(-1, 1)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # O
                                #  O
                                #   -
                                #    O
                                try:
                                    if player_piece == board[i_value+row_increment][j_value+col_increment] == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment+2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -400, 40, [(2, 2)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   -
                                #  O
                                # O
                                try:
                                    if temp_i_value-row_increment-3 > -1 and player_piece == board[temp_i_value-row_increment][j_value+col_increment] == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment-2][j_value+col_increment+2] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -400, 40, [(-2, 2)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                # last
                                #  -
                                #   O
                                #    O
                                #     O
                                try:
                                    if (i_value+row_increment+4 > 5 or j_value+col_increment+4 > 6) and player_piece == board[i_value+row_increment+1][j_value+col_increment+1] == board[i_value+row_increment+2][j_value+col_increment+2] == board[i_value+row_increment+3][j_value+col_increment+3] and board[i_value+row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0)], i_value+row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                                # if
                                #    O
                                #   O
                                #  O
                                # -
                                # last
                                try:
                                    if temp_i_value-row_increment-3 > -1 and (temp_i_value-row_increment-4 < 0 or j_value+col_increment+4 > 6) and player_piece == board[temp_i_value-row_increment-1][j_value+col_increment+1] == board[temp_i_value-row_increment-2][j_value+col_increment+2] == board[temp_i_value-row_increment-3][j_value+col_increment+3] and board[temp_i_value-row_increment][j_value+col_increment] == "-":
                                        heuristic_value += calc_heuristic_value_for_case(
                                            board, -500, 50, [(0, 0)], temp_i_value-row_increment, j_value+col_increment, False)
                                except IndexError:
                                    pass

                            if z > 0:
                                row_increment += 1
                                col_increment += 1
                            z += 1

        return heuristic_value

    elif status == 1:
        return 1000000
    elif status == -1:
        return -1000000
    elif status == 0:
        return 0


def check_status(board):

    total_non_empty_count = 0

    player_piece = "X"
    computer_piece = "O"

    global winning_pieces

    for i in range(0, len(board[0])):
        for j in range(0, len(board[0])):

            if j < 4 and i < 6:
                row_val_one_horizontal = board[i][j]
                row_val_two_horizontal = board[i][j + 1]
                row_val_three_horizontal = board[i][j + 2]
                row_val_four_horizontal = board[i][j + 3]

                if j == 0:
                    if row_val_one_horizontal != "-":
                        total_non_empty_count += 1
                    if row_val_two_horizontal != "-":
                        total_non_empty_count += 1
                    if row_val_three_horizontal != "-":
                        total_non_empty_count += 1
                    if row_val_four_horizontal != "-":
                        total_non_empty_count += 1
                else:
                    if row_val_four_horizontal != "-":
                        total_non_empty_count += 1

                if computer_piece == row_val_one_horizontal == row_val_two_horizontal == row_val_three_horizontal == row_val_four_horizontal:
                    winning_pieces = [[i, j], [i, j + 1],
                                      [i, j + 2], [i, j + 3]]
                    return 1
                if player_piece == row_val_one_horizontal == row_val_two_horizontal == row_val_three_horizontal == row_val_four_horizontal:
                    winning_pieces = [[i, j], [i, j + 1],
                                      [i, j + 2], [i, j + 3]]
                    return -1

            if j < 3:

                row_val_one_vertical = board[j][i]
                row_val_two_vertical = board[j + 1][i]
                row_val_three_vertical = board[j + 2][i]
                row_val_four_vertical = board[j + 3][i]

                if computer_piece == row_val_one_vertical == row_val_two_vertical == row_val_three_vertical == row_val_four_vertical:
                    winning_pieces = [[j, i], [j + 1, i],
                                      [j + 2, i], [j + 3, i]]
                    return 1
                if player_piece == row_val_one_vertical == row_val_two_vertical == row_val_three_vertical == row_val_four_vertical:
                    winning_pieces = [[j, i], [j + 1, i],
                                      [j + 2, i], [j + 3, i]]
                    return -1

            if j == 0 and i < 4:

                i_j_values = None

                if i == 0:
                    i_j_values = [(0, 0)]
                else:
                    i_j_values = [(i, 0), (0, i)]

                for i_value, j_value in i_j_values:

                    temp_i_value = (len(board)-1) - i_value

                    x_increment = 0

                    y_increment = 0

                    z = 0

                    while z < 3:

                        try:
                            row_val_one_diagonal = board[i_value +
                                                         x_increment][j_value+y_increment]
                            row_val_two_diagonal = board[i_value +
                                                         x_increment+1][j_value+y_increment+1]
                            row_val_three_diagonal = board[i_value +
                                                           x_increment+2][j_value+y_increment+2]
                            row_val_four_diagonal = board[i_value +
                                                          x_increment+3][j_value+y_increment+3]

                            row_val_one_diagonal_reverse = board[temp_i_value -
                                                                 x_increment][j_value+y_increment]
                            row_val_two_diagonal_reverse = board[temp_i_value -
                                                                 x_increment-1][j_value+y_increment+1]
                            row_val_three_diagonal_reverse = board[temp_i_value -
                                                                   x_increment-2][j_value+y_increment+2]
                            row_val_four_diagonal_reverse = board[temp_i_value -
                                                                  x_increment-3][j_value+y_increment+3]

                            if computer_piece == row_val_one_diagonal == row_val_two_diagonal == row_val_three_diagonal == row_val_four_diagonal:
                                winning_pieces = [[i_value + x_increment, j_value + y_increment], [i_value + x_increment + 1, j_value + y_increment + 1], [
                                    i_value + x_increment + 2, j_value + y_increment + 2], [i_value + x_increment + 3, j_value + y_increment + 3]]
                                return 1
                            if computer_piece == row_val_one_diagonal_reverse == row_val_two_diagonal_reverse == row_val_three_diagonal_reverse == row_val_four_diagonal_reverse:
                                winning_pieces = [[temp_i_value - x_increment, j_value + y_increment], [temp_i_value - x_increment - 1, j_value + y_increment + 1], [
                                    temp_i_value - x_increment - 2, j_value + y_increment + 2], [temp_i_value - x_increment - 3, j_value + y_increment + 3]]
                                return 1

                            if player_piece == row_val_one_diagonal == row_val_two_diagonal == row_val_three_diagonal == row_val_four_diagonal:
                                winning_pieces = [[i_value + x_increment, j_value + y_increment], [i_value + x_increment + 1, j_value + y_increment + 1], [
                                    i_value + x_increment + 2, j_value + y_increment + 2], [i_value + x_increment + 3, j_value + y_increment + 3]]
                                return -1
                            if player_piece == row_val_one_diagonal_reverse == row_val_two_diagonal_reverse == row_val_three_diagonal_reverse == row_val_four_diagonal_reverse:
                                winning_pieces = [[temp_i_value - x_increment, j_value + y_increment], [temp_i_value - x_increment - 1, j_value + y_increment + 1], [
                                    temp_i_value - x_increment - 2, j_value + y_increment + 2], [temp_i_value - x_increment - 3, j_value + y_increment + 3]]
                                return -1

                        except IndexError:
                            pass

                        x_increment += 1
                        y_increment += 1

                        z += 1

    if total_non_empty_count == 42:
        return 0
    else:
        return "Nf"


def max_value(board, alpha, beta, player_turn, depth, start_time):
    global more_than_five_seconds

    depth += 1

    status = check_status(board)

    if depth != 0:
        max_value = calc_heuristic_value(board, status)
    else:
        max_value = -10000000

    # return if terminal state has been reached (if a 0, 1, or -1 is returned)
    if status != "Nf" or depth == 4:
        return max_value

    # switching to player's or computer's turn
    if player_turn == True:
        player_turn = False
    elif player_turn == False:
        player_turn = True

    max_move = None

    for successor in get_successors(board, player_turn):
        new_board = successor[0]
        player_turn = successor[1]

        elapsed_time = time.time() - start_time

        # base case if the program has been running for more than 5 seconds
        if elapsed_time >= 5:
            more_than_five_seconds = True
            return max_value

        min_found_value = min_value(
            new_board, alpha, beta, player_turn, depth, start_time)

        # base case if the program has been running for more than 5 seconds
        if more_than_five_seconds == True:
            if max_value < min_found_value:

                max_value = min_found_value

                if depth == 0:
                    max_move = successor[2]

            if depth == 0:
                max_value = max_move

            return max_value

        # finding the max value for the maximizer
        if max_value < min_found_value:
            max_value = min_found_value

            if depth == 0:
                max_move = successor[2]

        # pruning if the current v value is greater than or equal to beta
        if max_value >= beta:
            if depth == 0:
                max_value = max_move
            return max_value
        else:
            alpha = max(alpha, max_value)

    if depth == 0:
        max_value = max_move

    return max_value

# minimizer function will try minimizing the value as small as possible


def min_value(board, alpha, beta, player_turn, depth, start_time):
    global more_than_five_seconds

    depth += 1

    status = check_status(board)

    min_value = calc_heuristic_value(board, status)

    # return if terminal state has been reached (if a 0, 1, or -1 is returned)
    if status != "Nf":
        return min_value

    # switching to player's or computer's turn
    if player_turn == True:
        player_turn = False
    elif player_turn == False:
        player_turn = True

    for successor in get_successors(board, player_turn):
        new_board = successor[0]
        player_turn = successor[1]

        elapsed_time = time.time() - start_time

        if elapsed_time >= 5:
            more_than_five_seconds = True
            return min_value

        max_found_value = max_value(
            new_board, alpha, beta, player_turn, depth, start_time)

        # base case if the program has been running for more than 5 seconds
        if more_than_five_seconds == True:
            if min_value > max_found_value:
                min_value = max_found_value

            return min_value

        # finding the min value for the minimizer
        if min_value > max_found_value:
            min_value = max_found_value

        # pruning if the current v value is less than or equal to alpha
        if min_value <= alpha:
            return min_value
        else:
            beta = min(beta, min_value)

    return min_value


def get_successors(board, player_turn):

    succesors = []

    piece = ""

    if player_turn == True:
        piece = "X"
    else:
        piece = "O"

    for col_index in range(0, len(board[0])):
        new_board = copy.deepcopy(board)
        for row_index in range(0, len(board)):
            move = None
            if board[row_index][col_index]:

                if row_index == 0 and new_board[row_index][col_index] != '-':
                    break

                if (row_index < 5 and board[row_index+1][col_index] != '-') or row_index == 5 and board[row_index][col_index] == '-':
                    new_board[row_index][col_index] = piece
                    move = (row_index, col_index)
                    succesors.append((new_board, player_turn, move))
                    break

    return succesors


def update_board(board, move):

    row_index = None

    col_index = None

    piece = "O"

    row_index = move[0]

    col_index = move[1]

    board[row_index][col_index] = piece


def get_computer_move_status_winning_pieces(board):

    move = alpha_beta_search(board)

    update_board(board, move)

    status = check_status(board)

    global more_than_five_seconds

    more_than_five_seconds = False

    global winning_pieces

    return (move[1], status, winning_pieces)

# API endpoint


@app.route('/retrieve-computer-move', methods=['POST'])
def retrieve_computer_move():

    board = request.json

    computer_move_status_winning_pieces = get_computer_move_status_winning_pieces(
        board)

    return jsonify({
        'computer_move_status_winning_pieces': computer_move_status_winning_pieces
    })


if __name__ == '__main__':
    app.run(port=2000)
