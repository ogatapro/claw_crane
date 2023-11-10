# filename: mac_client.py
import socket

HOST = '10.50.185.91'  # 请将此处替换为Jetson的IP地址
PORT = 65432

print("Press enter to move the servo")
input()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'move_servo')
    data = s.recv(1024)

print('Received', repr(data))

