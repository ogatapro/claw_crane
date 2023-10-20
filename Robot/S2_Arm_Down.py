import socket
from Arm_Lib import Arm_Device
import time

# 定义两个预设位置
POS_0_PERCENT = [90, 90, 90, 90, 90, 180]
POS_100_PERCENT = [88, 26, 72, 45, 86, 0]

def set_arm_position(percentage):
    Arm = Arm_Device()
    time.sleep(.1)
    
    # 计算每个舵机的目标位置
    target_positions = [
        p0 + (p100 - p0) * (percentage / 100) for p0, p100 in zip(POS_0_PERCENT, POS_100_PERCENT)
    ]
    
    # 设置舵机的位置
    Arm.Arm_serial_servo_write6(*target_positions, 1000)

def main():
    # 创建一个socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 获取服务器IP地址和端口号
    server_ip ="192.168.40.247"
    server_port = 12345
    
    # 绑定IP和端口，并监听连接
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    
    print(f"Listening for connections on {server_ip}:{server_port}...")
    
    # 接收客户端的连接
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}...")
    
    while True:
        # 接收百分比值
        
        perc = float(client_socket.recv(1024).decode())
        
        if perc == -1:
            # 如果收到终止消息，则关闭连接
            print("Terminating connection...")
            client_socket.close()
            break
        elif 0 <= perc <= 100:
            # 根据百分比值设置舵机的位置
            print(f"Moving servo to {perc} degrees")
            set_arm_position(perc)
            time.sleep(0.01)

if __name__ == "__main__":
    main()

