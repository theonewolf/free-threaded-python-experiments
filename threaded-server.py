oimport socket
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def handle_client(conn, addr, mode):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if mode == "compute":
                # Simulate a 2-second CPU-bound task
                x = 0
                for _ in range(10**7):
                    x += 1
            conn.sendall(data if mode == "echo" else b"done")

def main():
    if len(sys.argv) < 3:
        print("Usage: threaded-server.py <num_threads> <mode: echo|compute>")
        sys.exit(1)

    num_threads = int(sys.argv[1])
    mode = sys.argv[2]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 1337))
    server_socket.listen()

    # Use ThreadPoolExecutor to reuse threads for handling clients
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        print(f"Server running with thread pool of {num_threads} threads, mode: {mode}")
        while True:
            try:
                conn, addr = server_socket.accept()
                executor.submit(handle_client, conn, addr, mode)
            except KeyboardInterrupt:
                print("Shutting down server.")
                break

if __name__ == '__main__':
    main()
