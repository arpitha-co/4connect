# This is the file to access the camera stream

import cv2

def get_frame(camera_index=0):
    """Open camera stream, display live feed, and return last captured frame."""
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return None

    print("🎥 Press ESC to capture frame and exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Could not read frame.")
            break

        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    return frame

