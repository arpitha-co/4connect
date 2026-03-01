import cv2
import numpy as np

def detect_board_grid(camera_id=1, rows=6, cols=7):
    """
    Lets the user manually select the Connect 4 board ROI and draws a grid over it.
    Saves ROI coordinates for later use.
    """
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()
    if not ret:
        print("Camera not working")
        cap.release()
        return None

    # Let user select board ROI
    roi = cv2.selectROI("Select Board", frame, fromCenter=False)
    x, y, w, h = roi
    cv2.destroyWindow("Select Board")

    # Compute cell size
    cell_w = w // cols
    cell_h = h // rows

    # Draw grid
    board_frame = frame.copy()
    for i in range(cols + 1):
        cv2.line(board_frame, (x + i * cell_w, y), (x + i * cell_w, y + h), (0, 255, 0), 2)
    for j in range(rows + 1):
        cv2.line(board_frame, (x, y + j * cell_h), (x + w, y + j * cell_h), (0, 255, 0), 2)

    cv2.imshow("Board Grid", board_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cap.release()

    # Save grid info for later use
    np.save("board_grid.npy", np.array([x, y, w, h]))
    print("✅ Board grid saved as board_grid.npy")

    return (x, y, w, h)


if __name__ == "__main__":
    detect_board_grid()
