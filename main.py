import cv2
import os
import numpy as np
import time
from vision.color_detection import detect_colors
from vision.detect_board import detect_board_grid
from vision.map_discs_to_grid import map_discs_to_grid
from game_logic import Connect4Game
from ui.dashboard import show_dashboard
from robot_control.connect4_robot import Connect4Robot

# ----- GRID / DISPLAY CONVENTIONS -----
ROWS, COLS = 6, 7
BOTTOM_ORIGIN = True
MIRROR_COLUMNS = False


def to_display_indices(r_img: int, c_img: int):
    """
    Convert image indices to display indices.
    Now assumes bottom row = row 1 in the logic already.
    """
    if MIRROR_COLUMNS:
        c_disp = COLS - c_img
    else:
        c_disp = c_img + 1

    # Row: already bottom-based, just +1
    r_disp = r_img + 1

    return int(r_disp), int(c_disp)


def detect_move_strict(prev_board: np.ndarray,
                       curr_board: np.ndarray,
                       rows: int,
                       cols: int):
    """
    Strict, gravity-aware move detector.
    Returns (row_img, col_img, color, new_move: bool)

    - exactly one column must have changes
    - in that column, exactly one new occupied cell appears
    - that new cell must be the lowest empty position in prev_board
    """
    # where board changed
    changed = (prev_board != curr_board)

    # count changes by column
    changed_cols = []
    for c in range(cols):
        col_changes = np.where(changed[:, c])[0]
        if col_changes.size > 0:
            changed_cols.append(c)

    # If no change or more than one column changed -> ignore
    if len(changed_cols) != 1:
        return None, None, None, False

    c = changed_cols[0]

    # In that column, find cells that turned from empty->occupied
    became_filled_rows = []
    for r in range(rows):
        if prev_board[r, c] == 0 and curr_board[r, c] != 0:
            became_filled_rows.append(r)

    # We only accept exactly one new filled cell
    if len(became_filled_rows) != 1:
        return None, None, None, False

    r_new = became_filled_rows[0]
    color = int(curr_board[r_new, c])

    # Gravity check: r_new must be the lowest empty in prev_board
    # i.e., all rows below r_new must already be filled in prev_board
    for rb in range(r_new + 1, rows):  # rows increase downward in image
        if prev_board[rb, c] == 0:
            # there was an empty below; disc couldn't float here
            return None, None, None, False

    return r_new, c, color, True


def main():
    camera_id = 1  # use 1 for external webcam

    # --- Show dashboard for settings ---
    try:
        settings = show_dashboard()
    except Exception as e:
        print("⚠️ Could not open dashboard UI:", e)
        settings = {}

    if settings.get("cancelled"):
        print("Setup cancelled by user.")
        return

    player_name = settings.get("player_name", "Human")
    chosen_color = settings.get("player_color", "Yellow")  # "Red" or "Yellow"
    difficulty = settings.get("difficulty", "Medium")
    who_starts = settings.get("who_starts", "Human")

    # Map to numeric values used by vision mapping (1=Red, 2=Yellow)
    color_map = {"Red": 1, "Yellow": 2}
    human_color = color_map.get(chosen_color, 2)
    # robot gets other color
    robot_color = 1 if human_color != 1 else 2

    # Warn about physical robot color expectation (robot code assumes it places Red coins)
    if robot_color != 1:
        print("⚠️ Warning: robot is physically configured to play Red by default.")
        print("If you selected the robot to be Yellow, the robot will still place red coins physically.")

    print(f"Player '{player_name}' selected {chosen_color} coins.")
    print(f"Difficulty: {difficulty}")
    print(f"Who starts: {who_starts}")

    # Step 1: Load or create board grid
    if not os.path.exists("board_grid.npy"):
        print("🟩 No saved board grid found. Please select the board area.")
        detect_board_grid(camera_id=camera_id)

    x, y, w, h = np.load("board_grid.npy")
    x, y, w, h = int(x), int(y), int(w), int(h)
    print("✅ Loaded board grid:", (x, y, w, h))

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print("❌ Could not open camera.")
        return

    previous_board = np.zeros((ROWS, COLS), dtype=int)
    last_move_text = ""
    last_detection_time = 0.0
    COOLDOWN = 1.0  # seconds to avoid double prints

    print("🎥 Live feed started. Press ESC to exit.")

    # ---------- PRIME BASELINE: read a few frames to settle lighting/masks ----------
    prime_frames = 10
    for _ in range(prime_frames):
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame not captured during priming.")
            cap.release()
            cv2.destroyAllWindows()
            return
        board_frame = frame[y:y+h, x:x+w]
        mask_yellow, mask_red, output = detect_colors(board_frame)
        previous_board = map_discs_to_grid(mask_red, mask_yellow, grid_shape=(ROWS, COLS))
    # Who starts is taken from the dashboard settings

    # Initialize game logic & robot
    game = Connect4Game()
    game_over = False

    # difficulty -> minimax depth mapping
    depth_map = {"Easy": 2, "Medium": 4, "Hard": 6}
    AI_DEPTH = depth_map.get(difficulty, 4)

    print(f"🎨 Human = {'Red' if human_color==1 else 'Yellow'} ({human_color})")
    print(f"🎨 Robot = {'Red' if robot_color==1 else 'Yellow'} ({robot_color})")

    # Initialize robot controller
    robot = Connect4Robot()

    # If robot starts, let AI and robot play the first move
    if who_starts == "Robot":
        from game_logic.ai_strategy import choose_next_move
        robot_col = choose_next_move(game, depth=AI_DEPTH)
        if robot_col is not None:
            print(f"🤖 Robot starts and plays in column {robot_col + 1}")

            # Update logical board
            game.current_player = robot_color
            game.make_move(robot_col)
            game.switch_player()

            # Physically execute the move
            robot.play_move(robot_col)
        else:
            print("🤖 No valid moves available at start.")
    else:
        print("🧍 Human starts. Waiting for first move...")

    # -------------------- MAIN LOOP --------------------
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame not captured.")
            break

        board_frame = frame[y:y+h, x:x+w]
        mask_yellow, mask_red, output = detect_colors(board_frame)
        board_state = map_discs_to_grid(mask_red, mask_yellow, grid_shape=(ROWS, COLS))

        # --- STRICT, GRAVITY-AWARE MOVE DETECTION (no stability waiting) ---
        now = time.time()
        if now - last_detection_time > COOLDOWN:
            r_img, c_img, color, new_move = detect_move_strict(previous_board, board_state, ROWS, COLS)
            if new_move:
                # Convert for display: Row 1 = bottom, Col 1 = left
                # image row 0 is TOP; to bottom-origin: disp_row = ROWS - r_img
                r_disp = ROWS - r_img
                c_disp = (COLS - c_img) if MIRROR_COLUMNS else (c_img + 1)

                color_name = "Red" if color == 1 else "Yellow"
                last_move_text = f"🎯 {color_name} placed at Row {r_disp}, Col {c_disp}"
                print(last_move_text)

                # If this disc is NOT human color, it's a robot disc -> just update baseline and skip logic
                if color != human_color:
                    previous_board = board_state.copy()
                    last_detection_time = now
                    continue

                # 🧩 Update the logical board with human move and check for winner
                game.board[r_img, c_img] = color
                winner = game.check_winner()

                if winner == 1:
                    print("🏆 Red wins!")
                    last_move_text = "🏆 Red wins!"
                    game_over = True
                elif winner == 2:
                    print("🏆 Yellow wins!")
                    last_move_text = "🏆 Yellow wins!"
                    game_over = True
                elif winner == -1:
                    print("🤝 It's a draw!")
                    last_move_text = "🤝 It's a draw!"
                    game_over = True
                else:
                    # Human played, now robot's turn
                    game.switch_player()

                    if not game_over:
                        from game_logic.ai_strategy import choose_next_move
                        robot_col = choose_next_move(game, depth=AI_DEPTH)
                        if robot_col is not None:
                            print(f"🤖 Robot should play in column {robot_col + 1}")
                            game.current_player = robot_color
                            row = game.make_move(robot_col)
                            game.switch_player()

                            # Check if robot won
                            winner = game.check_winner()
                            if winner == robot_color:
                                print("🏆 Robot wins!")
                                last_move_text = "🏆 Robot wins!"
                                game_over = True

                            # Physically play robot move
                            robot.play_move(robot_col)
                        else:
                            print("🤖 No valid moves left.")

                # IMPORTANT: update baseline ONLY AFTER a confirmed move
                if not game_over:
                    previous_board = board_state.copy()
                last_detection_time = now

        # ---------- DRAW OVERLAYS ----------
        cell_w = int(w / COLS)
        cell_h = int(h / ROWS)

        # grid lines
        for i in range(COLS + 1):
            cv2.line(output, (i * cell_w, 0), (i * cell_w, h), (0, 255, 0), 2)
        for j in range(ROWS + 1):
            cv2.line(output, (0, j * cell_h), (w, j * cell_h), (0, 255, 0), 2)

        # cell labels (bottom-origin numbers)
        for r in range(ROWS):
            for c in range(COLS):
                cy = int((r + 0.5) * cell_h)
                cx = int((c + 0.5) * cell_w)
                r_disp = ROWS - r
                c_disp = (COLS - c) if MIRROR_COLUMNS else (c + 1)
                cv2.putText(output, f"{r_disp},{c_disp}",
                            (cx - 18, cy + 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                             (255, 255, 255), 1, cv2.LINE_AA)

        if last_move_text:
            cv2.putText(output, last_move_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Connect 4 - Live Detection", output)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🛑 Live feed stopped.")

    # Try to close robot connection cleanly
    try:
        robot.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
