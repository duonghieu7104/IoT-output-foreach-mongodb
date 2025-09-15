import socket
import time
import sys

FILE_PATH = "/app/logs/100_gas_sensor_log.txt"
HOST = "localhost"
PORT = 9998

# Màu ANSI
BLUE = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

def stream_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"{BLUE}Server listening on {HOST}:{PORT}{RESET}")
        while True:
            conn, addr = s.accept()
            print(f"{GREEN}Connection from {addr}{RESET}")
            with conn:
                with open(FILE_PATH, "r") as f:
                    lines = f.readlines()
                
                interval = 2 / len(lines)
                for line in lines:
                    conn.sendall(line.encode("utf-8"))
                    time.sleep(interval)
            print(f"{RED}Client disconnected, waiting for new connection...{RESET}")

if __name__ == "__main__":
    stream_data()
