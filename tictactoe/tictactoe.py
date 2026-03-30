"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0
    o_count = 0

    for row in board:
        x_count += row.count(X)
        o_count += row.count(O)

    # If X has fewer counts or they are equal it is X's turn
    if x_count <= o_count:
        return X
    # Otherwise it is O's turn
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] is EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Look at the action
    try:
        i, j = action
    except Exception:
        raise Exception("This move is not valid")

    # Check that action is in range
    if not (0 <= i < 3 and 0 <= j < 3):
        raise Exception("This is an out of bounds action")

    # Check that this specific space on the board is empty
    if board[i][j] is not EMPTY:
        raise Exception("Invalid action as the space on the board is not empty")

    # Deep copy the board for new update
    newer_board = deepcopy(board)

    # Find out whose turn it is and apply their move
    newer_board[i][j] = player(board)

    return newer_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for i in range(3):
        if board[i][0] is not EMPTY and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

    # Check columns
    for j in range(3):
        if board[0][j] is not EMPTY and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]

    # Check top-left to bottom-right diagonal
    if board[0][0] is not EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    # Check top-right to bottom-left diagonal
    if board[0][2] is not EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for row in board:
        if EMPTY in row:
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)

    if win == X:
        return 1
    elif win == 0:
        return -1
    else:
        return 0


def min_value(board):

    if terminal(board):
        return utility(board)

    curent_best = math.inf
    for action in actions(board):
        curent_best = min(curent_best, max_value(result(board, action)))
        if curent_best == -1:
            break
    return curent_best


def max_value(board):

    if terminal(board):
        return utility(board)

    curent_best = -math.inf
    for action in actions(board):
        curent_best = max(curent_best, min_value(result(board, action)))
        if curent_best == 1:
            break
    return curent_best


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Do nothing if the game is already over
    if terminal(board):
        return None

    current_p = player(board)

    # X wants to maximize its score
    if current_p == X:
        best_v = -math.inf
        best_a = None

        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_v:
                best_v = value
                best_a = action

        return best_a

    # O wants to minimize its score
    else:
        best_v = math.inf
        best_a = None

        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_v:
                best_v = value
                best_a = action

        return best_a
