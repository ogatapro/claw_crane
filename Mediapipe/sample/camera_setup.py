import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)  # カメラデバイスを指定 (0はデフォルトのカメラ)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        continue

    # 画像をRGBフォーマットに変換
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ハンドトラッキングを実行
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 手のランドマークを取得
            for landmark in hand_landmarks.landmark:
                x, y, z = landmark.x, landmark.y, landmark.z  # x, y, z座標
                print(x,y,z)

            # 手のランドマークを描画
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESCキーで終了
        break

cap.release()
cv2.destroyAllWindows()
