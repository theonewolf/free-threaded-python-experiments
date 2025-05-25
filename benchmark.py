import threading
import socket
import time
import sys

HOST = '127.0.0.1'
PORT = 1337
MESSAGE = b'ping'

def client_worker(stop_event, counter):
    while not stop_event.is_set():
        try:
            with socket.create_connection((HOST, PORT), timeout=10) as s:
                s.sendall(MESSAGE)
                _ = s.recv(1024)
                counter[0] += 1
        except Exception:
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: benchmark.py <num_threads> [duration_seconds]")
        sys.exit(1)

    num_threads = int(sys.argv[1])
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    stop_event = threading.Event()
    counters = [[0] for _ in range(num_threads)]
    threads = []

    for i in range(num_threads):
        t = threading.Thread(target=client_worker, args=(stop_event, counters[i]))
        t.start()
        threads.append(t)

    time.sleep(duration)
    stop_event.set()

    for t in threads:
        t.join()

    total_requests = sum(c[0] for c in counters)
    rps = total_requests / duration
    print(f"{total_requests} total requests in {duration}s ({rps:.2f} req/sec)")

if __name__ == '__main__':
    main()
