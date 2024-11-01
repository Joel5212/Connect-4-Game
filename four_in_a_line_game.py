import copy
import time

more_than_five_seconds = False


def main():

    board = create_board()

    start_time = None

    who_starts = int(
        input("Who is moving first? Enter 0 for Player or 1 for Computer: "))

    player_turn = False

    if who_starts == 0:
        player_turn = True

    while True:
        if player_turn == True:
            player_move = input("Enter Move: ")
            if is_legal_move(player_move) == True:
                print("")
                print("Illegal Move! Please Enter Again")
                print("")
                continue
            update_board(board, player_move, player_turn, who_starts)
            player_turn = False
        else:
            computers_move = alpha_beta_search(board, who_starts, start_time)
            update_board(board, computers_move, player_turn, who_starts)
            player_turn = True

        if check_status(board, who_starts) == 1:
            print("")
            print("COMPUTER WON!")
            print("")
            print_board(board)
            return
        elif check_status(board, who_starts) == -1:
            print("")
            print("USER WON!")
            print("")
            print_board(board)
            return
        elif check_status(board, who_starts) == 0:
            print("")
            print("DRAW!")
            print("")
            print_board(board)
            return
        else:
            print("")
            print_board(board)
            print("")
        global more_than_five_seconds
        more_than_five_seconds = False
        start_time = None

# start_time = None

# more_than_five_seconds = False


def alpha_beta_search(board, who_starts, start_time):
    player_turn = True

    start_time = time.time()

    # alpha is the best already explored option to the root for the maximizer
    alpha = -1000000

    # alpha is the best already explored option to the root for the minimizer
    beta = 1000000

    # first maximizer call enters the stack
    move = max_value(board, alpha, beta, who_starts,
                     player_turn, -1, start_time)

    print("Hello", move)

    return move


def calc_heuristic_value_for_case(board, initial_heuristic_value, decrement_weight, add_to_i_and_j_list, i, j):

    herustic_value = initial_heuristic_value

    iterations = len(board) - (i + 1)

    for add_to_i, add_to_j in add_to_i_and_j_list:

        if iterations == 0:
            break

        z = 1

        while z <= iterations:
            if board[i + add_to_i + z][j+add_to_j] == "-":
                herustic_value += decrement_weight
            else:
                break

            z += 1

    return herustic_value


def calc_heuristic_value(board, who_starts, status):

    if status == "Nf":

        heuristic_value = 0

        player_piece = None

        computer_piece = None

        if who_starts == 0:
            player_piece = "X"
            computer_piece = "O"
        elif who_starts == 1:
            player_piece = "O"
            computer_piece = "X"

        # suppose computer piece = X and player piece = O

        for i in range(0, len(board[0])):

            column_check_complete = False

            for j in range(0, len(board[0])):
                try:
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
                            # print("HELLO")
                            heuristic_value -= 500
                            column_check_complete = True
                except IndexError:
                    pass

                # def reduce_heuristic_value(heuristic_value, i, j):

                #     iterations = len(board) - i + 1

                #     while iterations > 0:
                #         board[i][j+2]

                # check for any vertical 4 in a row
                try:
                    # ----two consecutive computer pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if XX--
                        if computer_piece == board[i][j] == board[i][j+1] and board[i][j+2] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 50, -5, [(0, 2), (0, 3)], i, j)

                        # if X-X-
                        elif computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 40, -4, [(0, 1), (0, 3)], i, j)

                    # if anywhere
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            # if --XXO
                            if computer_piece == board[i][j+1] == board[i][j+2] and board[i][j+3] == player_piece and board[i][j-1] == "-" and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, -1), (0, 0)], i, j)

                            # if OXX--
                            if computer_piece == board[i][j] == board[i][j+1] and board[i][j-1] == player_piece and board[i][j+2] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, 2), (0, 3)], i, j)

                            # if OX-X-
                            if board[i][j-1] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, 1), (0, 3)], i, j)

                            # if -X-X-
                            if computer_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1), (0, 3)], i, j)

                            # if -X-XO
                            if board[i][j+3] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][-1] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1)], i, j)

                        if j < len(board[0]) - 2:

                            # if -XX-
                            if computer_piece == board[i][j] == board[i][j+1] and board[i][j-1] == "-" and board[i][j+2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, -1), (0, 2)], i, j)

                            # if X--X
                            if computer_piece == board[i][j-1] == board[i][j+2] and board[i][j] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 30, -3, [(0, 0), (0, 1)], i, j)

                        # if end
                        elif j == len(board[0]) - 3:
                            # if --XX
                            if computer_piece == board[i][j+1] == board[i][j+2] and board[i][j] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(0, 0), (0, -1)], i, j)

                            # if -X-X
                            elif computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 40, -4, [(0, -1), (0, 1)], i, j)

                    # ----three consecutive computer pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if XXX-
                        if computer_piece == board[i][j] == board[i][j+1] == board[i][j+2] and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, 500, -50, [(0, 3)], i, j)

                    # if anywhere
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            if computer_piece == board[i][j] == board[i][j+1] == board[i][j+2]:
                                # if -XXXO
                                if player_piece == board[i][j+3] and board[i][j-1] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, -1)], i, j)

                                # if OXXX-
                                if player_piece == board[i][j-1] and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, 3)], i, j)

                                # if -XXX-
                                if board[i][j-1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 500, -50, [(0, -1), (0, 3)], i, j)

                        if j < len(board[0]) - 2:

                            # if X-XX
                            if computer_piece == board[i][j-1] == board[i][j+1] == board[i][j+2] and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 400, -40, [(0, 0)], i, j)

                            # if XX-X
                            if computer_piece == board[i][j-1] == board[i][j] == board[i][j+2] and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 400, -40, [(0, 1)], i, j)

                        # if -XXX
                        elif j == len(board[0]) - 2:
                            if computer_piece == board[i][j-1] == board[i][j] == board[i][j+1] and board[i][j-2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 500, -50, [(0, -2)], i, j)

                    # ----two consecutive player pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if OO--
                        if player_piece == board[i][j] == board[i][j+1] and board[j+2] == "-" and board[j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -50, 5, [(0, 2), (0, 3)], i, j)

                        # if O-O-
                        elif player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -40, 4, [(0, 1), (0, 3)], i, j)

                    # if middle
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            # if --OOX
                            if player_piece == board[i][j+1] == board[i][j+2] and board[i][j+3] == computer_piece and board[i][j-1] == "-" and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, -1), (0, 0)], i, j)

                            # if XOO--
                            if player_piece == board[i][j] == board[i][j+1] and board[i][j-1] == computer_piece and board[i][j+2] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, 2), (0, 3)], i, j)

                            # if XO-O-
                            if board[i][j-1] == computer_piece and player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, 1), (0, 3)], i, j)

                            # if -O-O-
                            if player_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-" and board[i][j+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1), (0, 3)], i, j)

                            # if -O-OX
                            if board[i][j+3] == computer_piece and player_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1)], i, j)

                        if j < len(board[0]) - 2:

                            # if -OO-
                            if player_piece == board[i][j] == board[i][j+1] and board[i][j-1] == "-" and board[i][j+2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, -1), (0, 2)], i, j)

                            # if O--O
                            if player_piece == board[i][j-1] == board[i][j+2] and board[i][j] == "-" and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -30, 3, [(0, 0), (0, 1)], i, j)

                        # if end
                        if j == len(board[0]) - 3:

                            # if --OO
                            if player_piece == board[i][j+1] == board[i][j+2] and board[i][j] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -50, 5, [(0, 0), (0, -1)], i, j)

                            # if -O-O
                            elif player_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j-1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -40, 4, [(0, -1), (0, 1)], i, j)

                    # ----three consecutive player pieces in a row with open spot----

                    # if start
                    if j == 0:

                        # if OOO-
                        if player_piece == board[i][j] == board[i][j+1] == board[i][j+2] and board[i][j+3] == "-":
                            heuristic_value += calc_heuristic_value_for_case(
                                board, -500, 50, [(0, 3)], i, j)

                    # if middle
                    elif j > 0:

                        if j < len(board[0]) - 3:

                            if player_piece == board[i][j] == board[i][j+1] == board[i][j+2]:

                                # if -OOOX
                                if computer_piece == board[i][j+3] and board[i][j-1] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, -1)], i, j)

                                # if XOOO-
                                if computer_piece == board[i][j-1] and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, 3)], i, j)

                                # if -OOO-
                                if board[i][j-1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, -500, 50, [(0, -1), (0, 3)], i, j)

                        if j < len(board[0]) - 2:

                            # if O-OO
                            if player_piece == board[i][j-1] == board[i][j+1] == board[i][j+2] and board[i][j] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -400, 40, [(0, 0)], i, j)

                            # if OO-O
                            if player_piece == board[i][j-1] == board[i][j] == board[i][j+2] and board[i][j+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -400, 40, [(0, 1)], i, j)

                        # -OOO
                        elif j == len(board[0]) - 2:
                            if player_piece == board[i][j-1] == board[i][j] == board[i][j+1] and board[i][j-2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, -500, 50, [(0, -2)], i, j)

                except IndexError:
                    pass

                try:

                    if i == 0:
                        i_and_j_values = [(j, j)]
                    else:
                        i_and_j_values = [(i, j), (j, i)]

                    if j == 0 and (i == 0 or i == 1 or i == 2):

                        for i_value, j_value in i_and_j_values:

                            temp_i_value = (len(board)-1) - i_value

                            # if
                            # X
                            #  X
                            #   -
                            #    -
                            if computer_piece == board[i_value][j_value] == board[i_value+1][j_value+1] and board[i_value+2][j_value+2] == "-" and board[i_value+3][j_value+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(2, 2), (3, 3)], i_value, j_value)

                            # if
                            #    X
                            #   X
                            #  -
                            # -
                            if computer_piece == board[temp_i_value-2][j_value+2] == board[temp_i_value-3][j_value+3] and board[temp_i_value][j_value] == "-" and board[temp_i_value-1][j_value+1] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(2, 2), (3, 3)], temp_i_value, j_value)

                            # if
                            # X
                            #  -
                            #   X
                            #    -
                            if computer_piece == board[i_value][j_value] == board[i_value+2][j_value+2] and board[i_value+1][j_value+1] == "-" and board[i_value+3][j_value+3] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(1, 1), (3, 3)], i_value, j_value)

                            # if
                            #    X
                            #   -
                            #  X
                            # -
                            if computer_piece == board[temp_i_value-1][j_value+1] == board[temp_i_value-3][j_value+3] and board[temp_i_value][j_value] == "-" and board[temp_i_value-2][j_value+2] == "-":
                                heuristic_value += calc_heuristic_value_for_case(
                                    board, 50, -5, [(1, 1), (3, 3)], i_value, j_value)

                    if j > 0:

                        if j < len(board[0]) - 4:

                            for i_value, j_value in i_and_j_values:

                                board = [["-", "-", "-", "-", "-", "-", "-"],
                                         ["-", "-", "-", "-", "-", "-", "-"],
                                         ["-", "-", "-", "-", "-", "-", "-"],
                                         ["-", "-", "-", "-", "-", "-", "-"],
                                         ["X", "-", "-", "-", "-", "-", "-"],
                                         ["X", "O", "O", "O", "O", "X", "X"]]

                                # if
                                # -
                                #  -
                                #   X
                                #    X
                                #     O
                                if computer_piece == board[i_value+1][j_value+1] == board[i_value+2][j_value+2] and board[i_value+3][j_value+3] == player_piece and board[i_value-1][j_value-1] == "-" and board[i_value][j_value] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 50, -5, [(-1, -1), (0, 0)], i_value, j_value)

                                # if
                                #     -
                                #    -
                                #   X
                                #  X
                                # O
                                if computer_piece == board[len(board[0])-2-i_value][j_value-1] == board[len(board[0])-3-i_value][j_value] and board[i_value+3][j_value+3] == player_piece and board[i_value-1][j_value-1] == "-" and board[i_value][j_value] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 50, -5, [(-1, -1), (0, 0)], i_value, j_value)

                                # if
                                # O
                                # X
                                #  X
                                #   -
                                #    -
                                #     -
                                if computer_piece == board[i+1][j+1] == board[i][j+1] and board[i][j-1] == player_piece and board[i][j+2] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 50, -5, [(0, 2), (0, 3)], i, j)

                                # if
                                # O
                                # X
                                #  -
                                #   X
                                #    -
                                if board[i-1][j-1] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][j+1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 40, -4, [(0, 1), (0, 3)], i, j)

                            # if -X-X-
                            # -
                            # X
                            #  -
                            #   X
                            #    -
                                if computer_piece == board[i][j] == board[i][j+2] and board[i][j-1] == "-" and board[i][j+1] == "-" and board[i][j+3] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 40, -4, [(0, -1), (0, 1), (0, 3)], i, j)

                            # if -X-XO
                            # -
                            # X
                            #  -
                            #   X
                            #    O
                                if board[i][j+3] == player_piece and computer_piece == board[i][j] == board[i][j+2] and board[i][-1] == "-" and board[i][j+1] == "-":
                                    heuristic_value += calc_heuristic_value_for_case(
                                        board, 40, -4, [(0, -1), (0, 1)], i, j)

                except IndexError:
                    pass

        return heuristic_value

    elif status == 1:
        return 1000000
    elif status == -1:
        return -1000000
    elif status == 0:
        return 0


board = [["-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-"],
         ["-", "-", "-", "-", "-", "-", "-"],
         ["X", "-", "-", "-", "-", "-", "-"],
         ["X", "O", "O", "O", "O", "X", "X"]]

# print(calc_heuristic_value(board, 1, "Nf"))


def check_status(board, who_starts):

    total_non_empty_count = 0

    player_piece = None

    computer_piece = None

    if who_starts == 0:
        player_piece = "X"
        computer_piece = "O"
    elif who_starts == 1:
        player_piece = "O"
        computer_piece = "X"

    for i in range(0, len(board[0])):
        for j in range(0, len(board[0])):

            try:

                if j < 4:
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
                        return 1
                    if player_piece == row_val_one_horizontal == row_val_two_horizontal == row_val_three_horizontal == row_val_four_horizontal:
                        return -1

            except IndexError:
                pass

            try:
                if j < 3:

                    row_val_one_vertical = board[j][i]
                    row_val_two_vertical = board[j + 1][i]
                    row_val_three_vertical = board[j + 2][i]
                    row_val_four_vertical = board[j + 3][i]

                    if row_val_one_vertical == row_val_two_vertical == row_val_three_vertical == row_val_four_vertical == computer_piece:
                        return 1
                    if row_val_one_vertical == row_val_two_vertical == row_val_three_vertical == row_val_four_vertical == player_piece:
                        return -1

            except IndexError:
                pass

    if total_non_empty_count == 42:
        return 0
    else:
        return "Nf"

# print(check_status(board, 1))

# print(check_status(board, 1))

# def cut_off_search():
#     global start_time

#     elapsed_time = time.time() - start_time

#     if elapsed_time > 5:
#         global more_than_five_seconds
#         more_than_five_seconds = True


# maximizer function will try minimizing the value as small as possible
times_at_max = 0


def max_value(board, alpha, beta, who_starts, player_turn, depth, start_time):
    depth += 1

    status = check_status(board, who_starts)

    if depth != 0:
        max_value = calc_heuristic_value(board, who_starts, status)
    else:
        max_value = -10000000

    # return if terminal state has been reached (if a 0, 1, or -1 is returned)
    if status != "Nf" or depth == 6:

        return max_value

    # switching to player's or computer's turn
    if player_turn == True:
        player_turn = False
    elif player_turn == False:
        player_turn = True

    max_move = None

    for successor in get_successors(board, who_starts, player_turn):
        new_board = successor[0]
        player_turn = successor[1]

        elapsed_time = time.time() - start_time

        # base case if the program has been running for more than 5 seconds
        if elapsed_time >= 5:
            print(depth)
            print(times_at_max)
            global more_than_five_seconds
            more_than_five_seconds = True
            return max_value

        min_found_value = min_value(
            new_board, alpha, beta, who_starts, player_turn, depth, start_time)

        if depth == 0:
            print(more_than_five_seconds)
            print("Min Found Value", min_found_value)
            print("Max value so far", max_value)

        # base case if the program has been running for more than 5 seconds
        if more_than_five_seconds == True:
            if max_value < min_found_value:

                max_value = min_found_value

                if depth == 0:
                    print("gello")
                    max_move = successor[2]

            if depth == 0:
                print("MOVE", max_move)
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


def min_value(board, alpha, beta, who_starts, player_turn, depth, start_time):
    depth += 1

    status = check_status(board, who_starts)

    min_value = calc_heuristic_value(board, who_starts, status)

    # return if terminal state has been reached (if a 0, 1, or -1 is returned)
    if status != "Nf":

        return min_value

    # switching to player's or computer's turn
    if player_turn == True:
        player_turn = False
    elif player_turn == False:
        player_turn = True

    for successor in get_successors(board, who_starts, player_turn):
        new_board = successor[0]
        player_turn = successor[1]

        elapsed_time = time.time() - start_time

        if elapsed_time >= 5:
            global more_than_five_seconds
            more_than_five_seconds = True
            return min_value

        max_found_value = max_value(
            new_board, alpha, beta, who_starts, player_turn, depth, start_time)

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


def get_successors(board, who_starts, player_turn):

    succesors = []

    piece = ""

    # whoever starts is X, and player turn determines if X or O is going
    if who_starts == 0 and player_turn == True:
        piece = "X"
    elif who_starts == 0 and player_turn == False:
        piece = "O"
    elif who_starts == 1 and player_turn == False:
        piece = "X"
    elif who_starts == 1 and player_turn == True:
        piece = "O"

    for col_index in range(0, len(board[0])):
        new_board = copy.deepcopy(board)
        for row_index in range(0, len(board)):
            move = None
            if board[row_index][col_index]:
                # since this is connect 4, the successors would be the different boards with a piece placed in each column

                if row_index == 0 and new_board[row_index][col_index] != '-':
                    break

                if (row_index < 5 and board[row_index+1][col_index] != '-') or row_index == 5 and board[row_index][col_index] == '-':
                    new_board[row_index][col_index] = piece
                    move = (row_index, col_index)
                    succesors.append((new_board, player_turn, move))
                    break

    # for i in range(0, len(board[0])):
    #     for j in range(0, len(board)):
    #         new_board = copy.deepcopy(board)
    #         move = None
    #         if board[i][j] == "-":
    #             new_board[i][j] = piece
    #             move = (i, j)
    #             succesors.append((new_board, player_turn, move))

    return succesors


def is_legal_move(player_move):
    try:
        player_move_integer = int(player_move)

        if player_move_integer >= 1 and player_move_integer <= 7:
            return False
        else:
            return True
    except:
        return True


def update_board(board, move, player_turn, who_starts):

    print(move)

    row_index = None

    col_index = None

    piece = None

    if who_starts == 0:
        if player_turn:
            piece = "X"
        else:
            piece = "O"

    if who_starts == 1:
        if player_turn:
            piece = "O"
        else:
            piece = "X"

    if player_turn:

        col_index = int(move) - 1

        print(board)

        for row_index in range(0, len(board)):
            if row_index < 5 and board[row_index+1][col_index] != '-':
                board[row_index][col_index] = piece
                break
            elif row_index == 5 and board[row_index][col_index] == '-':
                board[row_index][col_index] = piece
                break
    else:

        row_index = move[0]

        col_index = move[1]

        board[row_index][col_index] = piece


def create_board():

    board = []

    for i in range(0, 6):
        board_row = []
        for i in range(0, 7):
            board_row.append("-")
        board.append(board_row)

    return board


def print_board(board):

    board_string = " 1  2  3  4  5  6  7\n"
    print("\n------ GAME BOARD ------\n")
    for row in board:
        for value in row:
            if value == "X":
                board_string += " X "
            elif value == "O":
                board_string += " O "
            else:
                board_string += " - "
        board_string += "\n"

    print(board_string)


main()
