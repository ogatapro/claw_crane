import socket

def get_percentage():
    while True:
        # 获取用户输入的百分比值，并检查其有效性
        perc = input("Enter percentage (0-100) or 'exit' to quit: ")
        if perc.lower() == 'exit':
            return 'exit'
        try:
            perc = float(perc)
            if 0 <= perc <= 100:
                return perc
            else:
                print("Invalid input. Please enter a number between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    # 获取服务器IP地址和端口号
    server_ip = "192.168.40.247"
    server_port = 12345
    
    # 创建一个socket对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 连接到服务器
    client_socket.connect((server_ip, server_port))
    
    while True:
        # 获取用户输入的百分比值
        perc = get_percentage()
        
        if perc == 'exit':
            # 发送终止消息到服务器
            client_socket.send(str(-1).encode())
            break
        else:
            # 发送百分比值到服务器
            client_socket.send(str(perc).encode())
    
    # 关闭socket
    client_socket.close()

if __name__ == "__main__":
    main()
