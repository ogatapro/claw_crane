import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '192.168.40.247'  # 替换为Jetson的IP地址
    server_port = 65432  # 与服务器端使用的端口号相同
    
    client_socket.connect((server_ip, server_port))
    
    try:
        while True:
            angle = input("Enter the angle (0-180) or 'exit' to quit: ")
            if angle.lower() == 'exit':
                break
            client_socket.sendall(angle.encode('utf-8'))
    except KeyboardInterrupt:
        print("Program closed!")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
