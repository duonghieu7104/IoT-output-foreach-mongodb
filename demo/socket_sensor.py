import socket
import time
import sys

# Màu ANSI
BLUE = "\033[36m" 
GREEN = "\033[32m"
RED = "\033[31m"  
RESET = "\033[0m"  

def stream_data(file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 9998))
        s.listen(1)
        print(f"{BLUE}Server listening on localhost:9998{RESET}")
        while True:
            conn, addr = s.accept()
            print(f"{GREEN}Connection from {addr}{RESET}")
            with conn:
                with open(file_path, "r") as f:
                    for line in f:
                        conn.sendall(line.encode("utf-8"))
                        time.sleep(2)
            print(f"{RED}Client disconnected, waiting for new connection...{RESET}")

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "/app/logs/0_gas_sensor_log.txt"
    stream_data(file_path)
