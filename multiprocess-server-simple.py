import socket

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Important: use SO_REUSEPORT for multiprocess concurrency, and Linux
    # kernel based load balancing across processes.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    server_socket.bind(('127.0.0.1', 1337))
    server_socket.listen()

    print(f"Listening on 127.0.0.1:1337")

    try:
        while True:
             with server_socket.accept()[0] as conn:
                # Simulate a CPU-bound task
                x = 0
                for _ in range(10**7):
                    x += 1
                conn.sendall(b"done")
    except KeyboardInterrupt:
        print(f"Shutting down")
    finally:
        server_socket.close()
