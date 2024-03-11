"""
Tic Tac Toe Player
"""

import math
import copy

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
    flatten_board = sum(board, [])
    if flatten_board.count(X) > flatten_board.count(O):
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == EMPTY:
                possible_actions.add((column, row))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board_copy = copy.deepcopy(board)
    print("BAR", action)
    if board[action[0]][action[1]] == EMPTY:
        board_copy[action[0]][action[1]] = player(board)
        return board_copy
    else:
        raise ValueError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    def won(p):
        win = False
        if board[0][0] == p and board[0][1] and board[0][2]:
            win = True
        elif board[1][0] == p and board[1][1] and board[1][2]:
            win = True
        elif board[2][0] == p and board[2][1] and board[2][2]:
            win = True
        elif board[0][0] == p and board[1][0] and board[2][0]:
            win = True
        elif board[0][1] == p and board[1][1] and board[2][1]:
            win = True
        elif board[0][2] == p and board[1][2] and board[2][2]:
            win = True
        elif board[0][0] == p and board[1][1] and board[2][2]:
            win = True
        elif board[0][2] == p and board[1][1] and board[2][0]:
            win = True

        return win

    if won(X):
        return X
    elif won(O):
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    flatten_board = sum(board, [])
    if winner(board) or flatten_board.count(EMPTY) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)

    def max_value(current_board):
        if terminal(current_board):
            return utility(current_board)
        print("MAX", actions(current_board))
        v = -math.inf
        for action in actions(current_board):
            v = max(v, min_value(result(current_board, action)))
        return v

    def min_value(current_board):
        if terminal(current_board):
            return utility(current_board)
        print("MIN", actions(current_board))
        v = math.inf
        for action in actions(current_board):
            v = min(v, max_value(result(current_board, action)))
        return v

    if current_player == X:
        max_value(board)
    else:
        min_value(board)
