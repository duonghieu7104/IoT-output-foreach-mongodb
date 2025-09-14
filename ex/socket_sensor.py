import socket
import time
import sys

FILE_PATH = "/app/logs/100_gas_sensor_log.txt"
HOST = "localhost"
PORT = 9999

def stream_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"📡 Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"✅ Connection from {addr}")
            with conn:
                with open(FILE_PATH, "r") as f:
                    lines = f.readlines()
                
                interval = 2 / len(lines)
                for line in lines:
                    conn.sendall(line.encode("utf-8"))
                    time.sleep(interval)
            print("⚠️ Client disconnected, waiting for new connection...")

if __name__ == "__main__":
    stream_data()
