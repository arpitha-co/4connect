# # vision/color_detection.py

import cv2
import numpy as np

def detect_colors(frame):
    """Detect yellow and red discs from a live camera frame and return cleaned masks + overlay."""
    # 1) Pre-smooth to reduce noise
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Yellow discs
    lower_yellow = (18, 101, 101)
    upper_yellow = (37, 255, 255)

    # Red discs
    lower_red1 = (0, 120, 70)
    upper_red1 = (10, 255, 255)
    lower_red2 = (170, 120, 70)
    upper_red2 = (180, 255, 255)

    # Masks
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Combine masks for visualization
    combined_mask = cv2.bitwise_or(mask_yellow, mask_red)

    # Create colored overlay
    output = frame.copy()
    output[mask_yellow > 0] = (0, 255, 255)  # yellow highlight
    output[mask_red > 0] = (0, 0, 255)       # red highlight

    # Optionally, detect contours (for future use)
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_yellow:
        area = cv2.contourArea(cnt)
        if area > 200:  # adjust threshold
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 255), 2)

    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 200:
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Return values to main loop
    return mask_yellow, mask_red, output

# import cv2
# import numpy as np

# def detect_colors(frame):
#     """Detect yellow and red discs from a live camera frame and return cleaned masks + overlay."""
#     # 1) Pre-smooth to reduce noise
#     blurred = cv2.GaussianBlur(frame, (5, 5), 0)

#     hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#     # --- Yellow range ---
#     lower_yellow = (7, 106, 73)
#     upper_yellow = (26, 255, 255)

#     # --- Red range (two parts, because hue wraps) ---
#     lower_red1 = (0, 120, 70)
#     upper_red1 = (10, 255, 255)
#     lower_red2 = (170, 120, 70)
#     upper_red2 = (180, 255, 255)

#     # Raw masks
#     mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
#     mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
#     mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
#     mask_red = cv2.bitwise_or(mask_red1, mask_red2)

#     # 2) Morphology to remove specks / fill small gaps
#     kernel = np.ones((5, 5), np.uint8)
#     mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel, iterations=1)
#     mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_CLOSE, kernel, iterations=1)

#     mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel, iterations=1)
#     mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel, iterations=1)

#     # 3) Visualization overlay
#     output = frame.copy()
#     output[mask_yellow > 0] = (0, 255, 255)  # yellow highlight
#     output[mask_red > 0] = (0, 0, 255)       # red highlight

#     return mask_yellow, mask_red, output
