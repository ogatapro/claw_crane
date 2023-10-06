import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)  # 使用第一个摄像头

is_recording = False
initial_position_y = None
prev_wrist_y = None
value_y = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        wrist_y = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist_position = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                

        if is_recording and wrist_y is not None and initial_position_y is not None:
            if prev_wrist_y is not None:
                if wrist_y > prev_wrist_y:
                    value_y += 2
                elif wrist_y < prev_wrist_y:
                    value_y -= 2
            print(f"Value Y: {value_y}")  # Printing the value for debugging
        prev_wrist_y = wrist_y
        wrist_y = int(wrist_position.y * frame.shape[0])
        mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        key = cv2.waitKey(1)
        
        if key == 13:  # Enter key
            if not is_recording:
                if wrist_y is not None:
                    initial_position_y = wrist_y
                    is_recording = True
            else:
                is_recording = False
        
        elif key == 27:  # ESC key
            break
        
        if is_recording and wrist_y is not None and initial_position_y is not None:
            distance_moved_y = wrist_y - initial_position_y
            distance_moved_y = min(max(distance_moved_y, -100), 100)

            cv2.putText(frame, f"Distance Y: {distance_moved_y}", (frame.shape[1] - 150, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        cv2.imshow('Hand Tracking', frame)
finally:
    cap.release()
    cv2.destroyAllWindows()