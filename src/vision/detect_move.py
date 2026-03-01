# import numpy as np

# def detect_move(prev_board, curr_board, last_move=None):
#     """
#     Detects where a new disc was placed.
#     Assumes bottom row = row 1, top = row 6.
#     """
#     new_cells = []

#     for r in range(prev_board.shape[0]):  # rows
#         for c in range(prev_board.shape[1]):  # cols
#             if prev_board[r, c] == 0 and curr_board[r, c] != 0:
#                 color = curr_board[r, c]
#                 new_cells.append((r, c, color))

#     if not new_cells:
#         return None  # no new move

#     # Convert row index so row 1 is bottom
#     # (OpenCV usually gives top-left as (0,0))
#     # So we invert rows if needed:
#     # Example: row_display = 6 - r
#     new_cells_display = [(6 - r, c + 1, color) for (r, c, color) in new_cells]

#     # Since bottom = row 1, we want the *lowest* one (smallest row_display)
#     final_move = min(new_cells_display, key=lambda x: x[0])

#     row, col, color = final_move
#     print(f"🎯 New disk detected: Row {row}, Col {col}, Color {color}")
#     return row, col, color


import numpy as np

def detect_move(prev_board, curr_board, last_move=None):
    """
    Compare two 6x7 board arrays to detect where a new disc appeared.
    Returns:
        (row_img, col_img, color, new_move)
    where (row_img, col_img) are 0-based image indices (top=0).
    """
    prev_board = np.array(prev_board)
    curr_board = np.array(curr_board)

    # New cell = was empty (0) before, now nonzero
    diff = (prev_board == 0) & (curr_board != 0)
    indices = np.argwhere(diff)

    if len(indices) == 0:
        return None, None, None, False

    # --- pick the *lowest (largest row index)* cell ---
    # (connect 4 drops from top to bottom)
    row, col = max(indices, key=lambda x: x[0])
    color = int(curr_board[row, col])

    # If same as last detected move, ignore
    if last_move == (row, col, color):
        return None, None, None, False

    return row, col, color, True
