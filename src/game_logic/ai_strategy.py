import numpy as np
import random

def choose_next_move(game, depth=5):
    """
    Minimax-based AI: evaluates future board states up to a given depth.
    Returns the best column for the robot.
    """
    board = game.board.copy()
    ai_player = game.current_player
    opponent = 1 if ai_player == 2 else 2

    valid_cols = get_valid_columns(board)
    if not valid_cols:
        return None

    best_score = -np.inf
    best_col = random.choice(valid_cols)
    best_moves = []

    for col in valid_cols:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        temp_board[row, col] = ai_player
        score = minimax(temp_board, depth - 1, False, ai_player, opponent, -np.inf, np.inf)
        if score > best_score:
            best_score = score
            best_moves = [col]
        elif score == best_score:
            best_moves.append(col)

    best_col = random.choice(best_moves)    
    return best_col


# -------------------------------
# Helper functions
# -------------------------------

def get_valid_columns(board):
    return [c for c in range(board.shape[1]) if board[0, c] == 0]

def get_next_open_row(board, col):
    for r in range(board.shape[0] - 1, -1, -1):
        if board[r, col] == 0:
            return r

def winning_move(board, player):
    rows, cols = board.shape
    # Horizontal
    for r in range(rows):
        for c in range(cols - 3):
            if all(board[r, c+i] == player for i in range(4)):
                return True
    # Vertical
    for r in range(rows - 3):
        for c in range(cols):
            if all(board[r+i, c] == player for i in range(4)):
                return True
    # Diagonal ↘
    for r in range(rows - 3):
        for c in range(cols - 3):
            if all(board[r+i, c+i] == player for i in range(4)):
                return True
    # Diagonal ↙
    for r in range(rows - 3):
        for c in range(3, cols):
            if all(board[r+i, c-i] == player for i in range(4)):
                return True
    return False


# -------------------------------
# Minimax core with alpha-beta pruning
# -------------------------------

def minimax(board, depth, maximizing, ai_player, opponent, alpha, beta):
    valid_cols = get_valid_columns(board)
    is_terminal = winning_move(board, ai_player) or winning_move(board, opponent) or len(valid_cols) == 0

    if depth == 0 or is_terminal:
        if winning_move(board, ai_player):
            return 100000
        elif winning_move(board, opponent):
            return -100000
        else:
            return score_position(board, ai_player)

    if maximizing:
        value = -np.inf
        for col in valid_cols:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            temp_board[row, col] = ai_player
            value = max(value, minimax(temp_board, depth - 1, False, ai_player, opponent, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = np.inf
        for col in valid_cols:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            temp_board[row, col] = opponent
            value = min(value, minimax(temp_board, depth - 1, True, ai_player, opponent, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


# -------------------------------
# Heuristic scoring function
# -------------------------------

def score_position(board, player):
    score = 0
    opponent = 1 if player == 2 else 2
    rows, cols = board.shape

    # Prefer center columns
    center_array = board[:, cols // 2]
    score += list(center_array).count(player) * 4

    # Score all horizontal windows
    for r in range(rows):
        row_array = list(board[r, :])
        for c in range(cols - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, player, opponent)

    # Score vertical windows
    for c in range(cols):
        col_array = list(board[:, c])
        for r in range(rows - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, player, opponent)

    # Score positively sloped diagonals
    for r in range(rows - 3):
        for c in range(cols - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    # Score negatively sloped diagonals
    for r in range(rows - 3):
        for c in range(3, cols):
            window = [board[r+i][c-i] for i in range(4)]
            score += evaluate_window(window, player, opponent)

    return score



def evaluate_window(window, player, opponent):
    window = list(window)
    score = 0

    player_count = window.count(player)
    opp_count = window.count(opponent)
    empty_count = window.count(0)

    # Reward good patterns
    if player_count == 4:
        score += 10000
    elif player_count == 3 and empty_count == 1:
        score += 100
    elif player_count == 2 and empty_count == 2:
        score += 10

    # Strongly punish giving opponent 3 in a row
    if opp_count == 3 and empty_count == 1:
        score -= 120
    elif opp_count == 2 and empty_count == 2:
        score -= 5    

    return score




