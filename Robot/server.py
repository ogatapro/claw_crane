import socket
import sys
sys.path.append('/home/ogataproject/Arm_Lib')
import time
from Arm_Lib import Arm_Device

# 定义两个预设位置
POS_0_PERCENT = [90, 90, 90, 90, 90, 180]
POS_100_PERCENT = [88, 26, 72, 45, 86, 0]
current_angle_1 = 90  # 假设90是初始位置
# 创建Arm对象并进行初始化
Arm = Arm_Device()
time.sleep(.1)

def set_arm_position(percentage):
    # 计算每个舵机的目标位置
    target_positions = [
        current_angle_1,  # 舵机1的位置保持不变
        POS_0_PERCENT[1] + (POS_100_PERCENT[1] - POS_0_PERCENT[1]) * (percentage / 100),
        POS_0_PERCENT[2] + (POS_100_PERCENT[2] - POS_0_PERCENT[2]) * (percentage / 100),
        POS_0_PERCENT[3] + (POS_100_PERCENT[3] - POS_0_PERCENT[3]) * (percentage / 100),
        POS_0_PERCENT[4] + (POS_100_PERCENT[4] - POS_0_PERCENT[4]) * (percentage / 100),
        POS_0_PERCENT[5] + (POS_100_PERCENT[5] - POS_0_PERCENT[5]) * (percentage / 100),
    ]
    # 设置舵机的位置
    Arm.Arm_serial_servo_write6(*target_positions, 1000)

def receive_message(client_socket):
    message = ""
    while True:
        data = client_socket.recv(1)  # 每次读取一个字节
        if not data or data == b'\n':
            break
        message += data.decode('utf-8')
    return message

def handle_step1_start(client_socket):
    global current_angle_1  # 声明要使用全局变量
    print("Ready to receive angle for STEP1...")
    while True:
        angle_message = receive_message(client_socket)
        if angle_message.lower() == 'exit':  # 客户端输入'exit'时退出
            break
        if angle_message.isdigit():
            angle = int(angle_message)
            angle = max(0, min(180, angle))  # 确保角度值在0到180之间
            print(f"Moving servo to {angle} degrees")
            current_angle_1 = angle  # 存储一号舵机的当前位置
            Arm.Arm_serial_servo_write(1, angle, 100)  # 移动到指定角度
            time.sleep(0.01)
        else:
            print("Invalid angle received")


def handle_step2_start(client_socket):
    print("Ready to receive percentage for STEP2...")
    while True:
        percentage_message = receive_message(client_socket)
        if percentage_message.lower() == 'exit':  # 客户端输入'exit'时退出
            break
        if percentage_message.isdigit():
           percentage = int(percentage_message)
           percentage = max(0, min(100, percentage))  # Clamp the percentage between 0 and 100
           print(f"Setting arm position to {percentage}%")
           set_arm_position(percentage)
           time.sleep(0.01)
        else:
           print("Invalid percentage received")
    

def handle_step3_start():
    print("Executing STEP3_START...")
    Arm.Arm_serial_servo_write(6, 180, 500)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(5, 90, 500)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(4, 90, 500)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(3, 90, 500)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(2, 90, 500)
    time.sleep(0.5)
    Arm.Arm_serial_servo_write(1, 90, 500)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 27782))
    server_socket.listen()
    
    print("Server is waiting for a connection...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        
        try:
            while True:
                command = receive_message(client_socket)
                if not command:
                    print("Client disconnected")
                    break
                
                print(f"Received command: {command}")
                
                # 根据接收到的命令执行不同的操作
                if command == 'STEP1_START':
                    print("第一步开始")
                    handle_step1_start(client_socket)  # 执行第一步操作
                    print("第一步结束")
                elif command == 'STEP2_START':
                    print("第二步开始")
                    handle_step2_start(client_socket)  # 执行第二步操作
                    print("第二步结束")
                elif command == 'STEP3_START':
                    print("第三步开始")
                    handle_step3_start()  # 执行第三步操作
                    print("第三步结束")
                elif command == 'EXIT':
                    print("Exit command received. Closing connection.")
                    break

        except KeyboardInterrupt:
            print("Server is shutting down...")
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
    # 确保当且仅当socket存在时才关闭它
          if 'client_socket' in locals() or 'client_socket' in globals():
            client_socket.close()
          if 'server_socket' in locals() or 'server_socket' in globals():
            server_socket.close()

if __name__ == "__main__":
    main()

