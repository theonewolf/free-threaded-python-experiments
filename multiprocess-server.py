import socket
import multiprocessing
import sys
import os

def handle_client(conn, addr, mode):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if mode == "compute":
                # Simulate a CPU-bound task
                x = 0
                for _ in range(10**7):
                    x += 1
            conn.sendall(data if mode == "echo" else b"done")

def worker(mode):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Important: enable SO_REUSEPORT before bind() for macOS
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    server_socket.bind(('127.0.0.1', 1337))
    server_socket.listen()

    print(f"[PID {os.getpid()}] Listening on 127.0.0.1:1337 in {mode} mode")

    try:
        while True:
            conn, addr = server_socket.accept()
            handle_client(conn, addr, mode)
    except KeyboardInterrupt:
        print(f"[PID {os.getpid()}] Shutting down")
    finally:
        server_socket.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: multiprocess-server.py <num_processes> <mode: echo|compute>")
        sys.exit(1)

    num_processes = int(sys.argv[1])
    mode = sys.argv[2]

    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=worker, args=(mode,))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

if __name__ == '__main__':
    main()
