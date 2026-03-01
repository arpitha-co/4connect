import numpy as np

class Connect4Game:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        self.current_player = 1  # 1 = Red, 2 = Yellow
        self.winner = 0

    # -------------------
    # Core game functions
    # -------------------

    def is_valid_move(self, col):
        """Check if the given column is not full."""
        return self.board[0, col] == 0

    def make_move(self, col):
        """
        Drop the current player's disc into the column.
        Returns (row, col) of the placed disc, or None if invalid.
        """
        if not self.is_valid_move(col):
            print(f"⚠️ Column {col+1} is full!")
            return None

        for r in range(self.rows - 1, -1, -1):
            if self.board[r, col] == 0:
                self.board[r, col] = self.current_player
                return (r, col)
        return None

    def switch_player(self):
        """Switch to the other player."""
        self.current_player = 1 if self.current_player == 2 else 2

    def reset(self):
        """Clear the board and reset players."""
        self.board[:] = 0
        self.current_player = 1
        self.winner = 0

    # -------------------
    # Win / Draw detection
    # -------------------

    def check_winner(self):
        """Return 1 (Red), 2 (Yellow), -1 (Draw), or 0 (no winner)."""
        b = self.board
        r, c = self.rows, self.cols

        # Horizontal
        for i in range(r):
            for j in range(c - 3):
                if b[i, j] != 0 and len(set(b[i, j:j + 4])) == 1:
                    self.winner = b[i, j]
                    return self.winner

        # Vertical
        for i in range(r - 3):
            for j in range(c):
                if b[i, j] != 0 and len(set(b[i:i + 4, j])) == 1:
                    self.winner = b[i, j]
                    return self.winner

        # Diagonal ↘
        for i in range(r - 3):
            for j in range(c - 3):
                vals = [b[i + k, j + k] for k in range(4)]
                if vals[0] != 0 and len(set(vals)) == 1:
                    self.winner = vals[0]
                    return self.winner

        # Diagonal ↙
        for i in range(r - 3):
            for j in range(3, c):
                vals = [b[i + k, j - k] for k in range(4)]
                if vals[0] != 0 and len(set(vals)) == 1:
                    self.winner = vals[0]
                    return self.winner

        # Draw check
        if np.all(b != 0):
            self.winner = -1
            return -1

        return 0  # No winner yet

    # -------------------
    # Debug / Display helpers
    # -------------------

    def print_board(self):
        """Print the board with bottom row as Row 1."""
        flipped = np.flipud(self.board)
        for row in flipped:
            print(" ".join(str(int(x)) for x in row))
        print("-" * (self.cols * 2 - 1))
        print(" ".join(str(i + 1) for i in range(self.cols)))
