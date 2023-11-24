import cv2
import mediapipe as mp
import socket
import time

# サーバーのIPアドレスとポートを定義
SERVER_IP = '10.50.185.91'
SERVER_PORT = 27781

def send_command(client_socket, command):
    """サーバーにコマンドを送信する関数"""
    try:
        client_socket.sendall(command.encode('utf-8'))
    except Exception as e:
        print(f"コマンド送信中にエラーが発生しました: {e}")

def control_arm_by_angle(client_socket):
    """カメラと手の追跡を使用して機械臂の角度を制御する関数"""
    send_command(client_socket, 'STEP1_START\n')
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)  # システムのデフォルトカメラを使用
    is_recording = False
    initial_position_x = None
    prev_wrist_x = None
    angle = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            wrist_x = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    wrist_position = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    wrist_x = int(wrist_position.x * frame.shape[1])
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            key = cv2.waitKey(1)
            
            if key == 13:  # Enterキー
                if not is_recording:
                    if wrist_x is not None:
                        initial_position_x = wrist_x
                        is_recording = True
                else:
                    is_recording = False
            
            elif key == 27:  # ESCキー
                send_command(client_socket, 'EXIT\n')
                break
            
            if is_recording and wrist_x is not None and initial_position_x is not None:
                if prev_wrist_x is not None:
                    if wrist_x > prev_wrist_x:
                        angle += 1
                    elif wrist_x < prev_wrist_x:
                        angle -= 1
                    angle = max(0, min(180, angle))
                    send_command(client_socket, str(angle) + '\n')
                    print(f"送信された角度: {angle}") 
                    time.sleep(0.01)
                prev_wrist_x = wrist_x
            
                cv2.putText(frame, f"角度: {angle}", (frame.shape[1] - 150, frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            
            cv2.imshow('手の追跡', frame)

    finally:
        cap.release()
        cv2.destroyAllWindows()

def control_arm_by_percentage(client_socket):
    """手のY座標の動きに基づいて機械臂の高さを制御する関数"""
    send_command(client_socket, 'STEP2_START\n')
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    cap = cv2.VideoCapture(0)  # システムのデフォルトカメラを使用

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
                    wrist_y = int(wrist_position.y * frame.shape[0])

                    if is_recording and wrist_y is not None and initial_position_y is not None:
                        if prev_wrist_y is not None:
                            if wrist_y > prev_wrist_y:
                                value_y += 2
                            elif wrist_y < prev_wrist_y:
                                value_y -= 2
                        value_y = max(0, min(value_y, 100))
                        print(f"Y座標の値: {value_y}")
                        send_command(client_socket, str(value_y) + '\n')
                        time.sleep(0.01)
                    prev_wrist_y = wrist_y
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            key = cv2.waitKey(1)

            if key == 13:
                if not is_recording:
                    if wrist_y is not None:
                        initial_position_y = wrist_y
                        is_recording = True
                else:
                    is_recording = False

            elif key == 27:
                send_command(client_socket, 'EXIT\n')
                break

            if is_recording and wrist_y is not None and initial_position_y is not None:
                distance_moved_y = wrist_y - initial_position_y
                distance_moved_y = max(0, min(distance_moved_y, 100))

                cv2.putText(frame, f"Y移動距離: {distance_moved_y}", (frame.shape[1] - 150, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            cv2.imshow('手の追跡', frame)

    finally:
        cap.release()
        cv2.destroyAllWindows()

def control_arm_by_step3(client_socket):
    """サーバーに第三ステップのコマンドを送信する関数"""
    send_command(client_socket, 'STEP3_START\n')

def main():
    """メイン関数、プログラムの実行を管理"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_IP, SERVER_PORT))

        try:
            while True:
                cmd = input("角度制御には '1'、高さ制御には '2'、つかむには '3' を押す、終了するには 'exit' を入力: ")
                if cmd == '1':
                    control_arm_by_angle(client_socket)
                elif cmd == '2':
                    control_arm_by_percentage(client_socket)
                elif cmd == '3':
                    control_arm_by_step3(client_socket)
                elif cmd.lower() == 'exit':
                    send_command(client_socket, 'EXIT')
                    break
        except Exception as e:
            print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
