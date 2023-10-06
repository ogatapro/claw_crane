import cv2
import mediapipe as mp
import socket
import time

def scale_value(value, max_scale_distance):
    return min(max(value, -max_scale_distance), max_scale_distance) * (100 / max_scale_distance)

# 初始化MediaPipe和摄像头
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

# 初始化socket客户端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '10.50.185.91'   # 请替换为您的服务器IP地址
server_port = 65432  # 请确保此端口与您服务器上的端口匹配
client_socket.connect((server_ip, server_port))

# 初始化变量
is_recording = False
initial_position_x = None
initial_position_y = None
prev_wrist_x = None
prev_wrist_y = None
value_x = 0
value_y = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        wrist_x = None
        wrist_y = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist_position = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                wrist_x = int(wrist_position.x * frame.shape[1])
                wrist_y = int(wrist_position.y * frame.shape[0])
                if wrist_x is not None:
                    wrist_x = min(max(wrist_x, 0), frame.shape[1])  # Make sure wrist_x is within frame boundaries
                if wrist_y is not None:
                    wrist_y = min(max(wrist_y, 0), frame.shape[0])  # Make sure wrist_y is within frame boundaries
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                cv2.putText(frame, f"X: {wrist_x}, Y: {wrist_y}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        if is_recording:
            if wrist_x is not None and initial_position_x is not None:
                if prev_wrist_x is not None:
                    if wrist_x > prev_wrist_x:
                        value_x = scale_value(value_x + 2, frame.shape[1] / 2)
                    elif wrist_x < prev_wrist_x:
                        value_x = scale_value(value_x - 2, frame.shape[1] / 2)
                print(f"Value X: {value_x}")  # Printing the value for debugging
                client_socket.sendall((str(value_x) + '\n').encode('utf-8'))
                time.sleep(0.01)  # 暂停0.01秒以确保不会发送太多数据
            prev_wrist_x = wrist_x

            if wrist_y is not None and initial_position_y is not None:
                if prev_wrist_y is not None:
                    if wrist_y > prev_wrist_y:
                        value_y = scale_value(value_y + 2, frame.shape[0] / 2)
                    elif wrist_y < prev_wrist_y:
                        value_y = scale_value(value_y - 2, frame.shape[0] / 2)
                print(f"Value Y: {value_y}")  # Printing the value for debugging
                client_socket.sendall((str(value_y) + '\n').encode('utf-8'))
                time.sleep(0.01)  # 暂停0.01秒以确保不会发送太多数据
            prev_wrist_y = wrist_y

        key = cv2.waitKey(1)

        if key == 13:  # Enter key
            if not is_recording:
                if wrist_x is not None and wrist_y is not None:
                    initial_position_x = wrist_x
                    initial_position_y = wrist_y
                    is_recording = True
            else:
                is_recording = False
                initial_position_x = None
                initial_position_y = None
                prev_wrist_x = None
                prev_wrist_y = None
                value_x = 0
                value_y = 0

        elif key == 27:  # ESC key
            break

        cv2.imshow('Hand Tracking', frame)

finally:
    client_socket.close()
    cap.release()
    cv2.destroyAllWindows()
