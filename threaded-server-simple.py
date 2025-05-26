import socket
from concurrent.futures import ThreadPoolExecutor

def handle_client(conn):
    with conn:
        # Simulate a 2-second CPU-bound task
        x = 0
        for _ in range(10**7):
            x += 1
        conn.sendall(b"done")

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 1337))
    server_socket.listen()

    # Use ThreadPoolExecutor to reuse threads for handling clients
    with ThreadPoolExecutor(max_workers=4) as executor:
        print("Server running with thread pool")
        while True:
            try:
                conn, _ = server_socket.accept()
                executor.submit(handle_client, conn)
            except KeyboardInterrupt:
                print("Shutting down server.")
                break
