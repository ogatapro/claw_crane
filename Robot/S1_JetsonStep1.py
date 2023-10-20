import sys
import socket
sys.path.append('/home/ogataproject/Arm_Lib')

import time
from Arm_Lib import Arm_Device

Arm = Arm_Device()
time.sleep(.1)


def receive_message(client_socket):
    message = ""
    while True:
        data = client_socket.recv(1)  # 每次读取一个字节
        if not data or data == b'\n':
            break
        message += data.decode('utf-8')
    return message

def main():
    print("Main function started!");
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 65432))  # 绑定到所有可用接口，端口65432
    server_socket.listen()
    
    print("Server is waiting for a connection...")
    
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    
    try:
        while True:
            message = receive_message(client_socket)
            if not message:
                print("Client disconnected")
                break
            
            print("Received data:", message)
            angle = int(message)
            angle = max(0, min(180, angle))  # Clamp the angle between 0 and 180
            
            print(f"Moving servo to {angle} degrees")
            Arm.Arm_serial_servo_write(1, angle, 100)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Program closed!")
    except socket.error as e:
        print(f"Socket error:{e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    main()

