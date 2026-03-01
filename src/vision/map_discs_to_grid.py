import numpy as np
import cv2

def map_discs_to_grid(mask_red, mask_yellow, grid_shape=(6, 7)):
    """
    Map detected red/yellow discs to grid cells (row, column).
    Returns a 2D board array:
      0 = empty
      1 = red disc
      2 = yellow disc
    """

    rows, cols = grid_shape
    board = np.zeros((rows, cols), dtype=int)

    h, w = mask_red.shape
    cell_w = w / cols
    cell_h = h / rows

    # --- Red discs ---
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 200:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                col = int(cx / cell_w)
                row = int(cy / cell_h)
                if 0 <= row < rows and 0 <= col < cols:
                    board[row, col] = 1

    # --- Yellow discs ---
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_yellow:
        area = cv2.contourArea(cnt)
        if area > 200:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                col = int(cx / cell_w)
                row = int(cy / cell_h)
                if 0 <= row < rows and 0 <= col < cols:
                    board[row, col] = 2

    return board

# import numpy as np

# def map_discs_to_grid(mask_red, mask_yellow, grid_shape=(6, 7), occupancy_thresh=0.15):
#     """
#     Decide cell occupancy by % of mask pixels inside each cell.
#     Returns a 6x7 board: 0=empty, 1=red, 2=yellow
#     """
#     rows, cols = grid_shape
#     h, w = mask_red.shape
#     cell_w = w / cols
#     cell_h = h / rows

#     board = np.zeros((rows, cols), dtype=int)

#     for r in range(rows):
#         y0 = int(r * cell_h)
#         y1 = int((r + 1) * cell_h)
#         for c in range(cols):
#             x0 = int(c * cell_w)
#             x1 = int((c + 1) * cell_w)

#             cell_area = (y1 - y0) * (x1 - x0)
#             if cell_area <= 0:
#                 continue

#             red_count = np.count_nonzero(mask_red[y0:y1, x0:x1])
#             yellow_count = np.count_nonzero(mask_yellow[y0:y1, x0:x1])

#             red_ratio = red_count / cell_area
#             yellow_ratio = yellow_count / cell_area

#             # Only mark a color if it clearly dominates and passes threshold
#             if max(red_ratio, yellow_ratio) >= occupancy_thresh:
#                 if red_ratio > yellow_ratio:
#                     board[r, c] = 1
#                 else:
#                     board[r, c] = 2

#     return board
