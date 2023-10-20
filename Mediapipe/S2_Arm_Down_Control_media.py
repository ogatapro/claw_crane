import cv2
import mediapipe as mp
import socket

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = "192.168.40.247"
server_port = 12345
client_socket.connect((server_ip, server_port))

cap = cv2.VideoCapture(1)

initial_position_y = None
current_percentage = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * frame.shape[0]

                if initial_position_y is not None:
                    distance_moved_y = wrist_y - initial_position_y

                    if distance_moved_y > 30:  # 向下移动
                        current_percentage = min(100, current_percentage + 2)
                    elif distance_moved_y < -30:  # 向上移动
                        current_percentage = max(0, current_percentage - 2)

                    cv2.putText(frame, f"Percentage: {current_percentage}%", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    client_socket.send(str(current_percentage).encode())

        cv2.imshow('Frame', frame)

        key = cv2.waitKey(1)
        if key == 13:  # Enter key
            initial_position_y = wrist_y
            current_percentage = 0  # Reset percentage when Enter is pressed
        elif key == 27:  # ESC key
            break
finally:
    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()
