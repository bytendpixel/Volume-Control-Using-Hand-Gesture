import cv2
import numpy as np
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from comtypes import GUID

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Set up system volume control using pycaw

IID_IAudioEndpointVolume = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IID_IAudioEndpointVolume, CLSCTX_ALL, None)
volume_control = interface.QueryInterface(IAudioEndpointVolume)

# Get volume range
vol_range = volume_control.GetVolumeRange()
min_vol, max_vol = vol_range[:2]
# screen-brightness-control
# Start webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert BGR to RGB for Mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Extract thumb and index finger tip positions
            thumb_tip = hand_landmarks.landmark[4]   # Thumb tip
            index_tip = hand_landmarks.landmark[8]   # Index finger tip

            # Convert to pixel values
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            # Draw circles at the finger tips
            cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 0, 255), -1)
            cv2.circle(frame, (index_x, index_y), 10, (0, 255, 0), -1)

            # Draw a line between the thumb and index finger
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)

            # Calculate distance between thumb and index finger
            distance = np.hypot(index_x - thumb_x, index_y - thumb_y)

            # Convert distance to volume level (mapping)
            volume = np.interp(distance, [20, 200], [min_vol, max_vol])
            volume_control.SetMasterVolumeLevel(volume, None)

            # Display volume level on screen
            vol_percentage = np.interp(distance, [20, 200], [0, 100])
            cv2.putText(frame, f'Volume: {int(vol_percentage)}%', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Hand Gesture Volume Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()