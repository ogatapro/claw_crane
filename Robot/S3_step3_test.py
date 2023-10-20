# filename: jetson_server.py
import socket
from Arm_Lib import Arm_Device

# 创建机械臂对象
Arm = Arm_Device()

Arm.Arm_serial_servo_write(6, 0, 500)

HOST = '0.0.0.0'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Waiting for connection...")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            if data == 'move_servo':
                print("Moving servo from 180 to 0")
                Arm.Arm_serial_servo_write(6, 180, 500)
                conn.sendall(b'Moved servo')

