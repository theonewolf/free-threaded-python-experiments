import argparse
import subprocess
import time
import csv
import signal
import os
import psutil
import matplotlib.pyplot as plt
import pandas as pd
import re

PYTHONS = {
    'py314': './py314/bin/python3',
    'py314t': './py314t/bin/python3',
}
RESULTS_FILE = 'results.csv'

def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark threaded vs multiprocess Python servers.')
    parser.add_argument('--max-client-threads', type=int, default=8,
                        help='Max number of client threads to simulate')
    parser.add_argument('--server-threads', type=int, nargs='+', required=True,
                        help='List of server thread counts to test (e.g., 1 2 4)')
    parser.add_argument('--benchmark-duration', type=int, default=15,
                        help='Benchmark duration in seconds')
    parser.add_argument('--mode', choices=['echo', 'compute'], default='compute',
                        help='Server mode: echo or compute')
    parser.add_argument('--server-type', choices=['threaded', 'multiprocess'], nargs='+', required=True,
                        help='Which server types to run: threaded, multiprocess, or both')
    return parser.parse_args()

def run_benchmark(client_threads, duration):
    result = subprocess.run(
        ['python3', 'benchmark.py', str(client_threads), str(duration)],
        capture_output=True, text=True
    )
    match = re.search(r"([\d.]+) req/sec", result.stdout)
    return float(match.group(1)) if match else 0.0

def monitor_process(pid):
    try:
        proc = psutil.Process(pid)
        cpu = proc.cpu_percent(interval=1.0)
        mem = proc.memory_info().rss / (1024 * 1024)
        return cpu, mem
    except psutil.NoSuchProcess:
        return 0.0, 0.0

def cleanup_multiprocess():
    try:
        subprocess.run(['pkill', '-f', 'multiprocess-server.py'], check=False)
    except Exception as e:
        print("Cleanup failed:", e)

def collect_results(args):
    rows = []
    for server_type in args.server_type:
        for py_label, py_path in PYTHONS.items():
            for server_threads in args.server_threads:
                print(f"\nLaunching server: {server_type} | {py_label} | {server_threads} threads...")

                if server_type == 'multiprocess':
                    procs = []
                    for _ in range(server_threads):
                        p = subprocess.Popen(
                            [py_path, 'multiprocess-server.py', '1', args.mode],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid
                        )
                        procs.append(p)
                    time.sleep(1)
                    server_pids = [p.pid for p in procs]
                else:
                    server = subprocess.Popen(
                        [py_path, 'threaded-server.py', str(server_threads), args.mode],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid
                    )
                    time.sleep(1)
                    server_pids = [server.pid]

                for client_threads in range(1, args.max_client_threads + 1):
                    total_cpu, total_mem = 0.0, 0.0
                    for pid in server_pids:
                        cpu, mem = monitor_process(pid)
                        total_cpu += cpu
                        total_mem += mem
                    rps = run_benchmark(client_threads, args.benchmark_duration)
                    print(f"{server_type} | {py_label} | server:{server_threads} | client:{client_threads} => {rps:.2f} req/s | CPU: {total_cpu:.1f}% | MEM: {total_mem:.1f}MB")
                    rows.append([
                        server_type, py_label, server_threads,
                        client_threads, rps, total_cpu, total_mem
                    ])

                # Terminate servers
                if server_type == 'multiprocess':
                    for p in procs:
                        try:
                            os.killpg(os.getpgid(p.pid), signal.SIGINT)
                            p.wait(timeout=5)
                        except Exception:
                            p.terminate()
                else:
                    try:
                        os.killpg(os.getpgid(server.pid), signal.SIGINT)
                        server.wait(timeout=5)
                    except Exception:
                        server.terminate()

                time.sleep(0.5)
                if server_type == 'multiprocess':
                    cleanup_multiprocess()
    return rows

def write_csv(rows):
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'server_type', 'python', 'server_threads',
            'client_threads', 'requests_per_sec', 'cpu_percent', 'memory_mb'
        ])
        writer.writerows(rows)

def plot_results():
    df = pd.read_csv(RESULTS_FILE)

    for (server_type, py), group in df.groupby(['server_type', 'python']):
        for metric, ylabel in [('requests_per_sec', 'Requests/sec'),
                               ('cpu_percent', 'CPU %'),
                               ('memory_mb', 'Memory (MB)')]:
            plt.figure()
            for server_threads, sub in group.groupby('server_threads'):
                plt.plot(sub['client_threads'], sub[metric], label=f'{server_threads} server threads')
            plt.title(f"{metric.replace('_', ' ').title()} - {server_type} - {py}")
            plt.xlabel("Benchmark Client Threads")
            plt.ylabel(ylabel)
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"{metric}_{server_type}_{py}.png")
            plt.close()

    peak = df.groupby(['server_type', 'python'])['requests_per_sec'].max().reset_index()
    labels = [f"{row['server_type']} ({row['python']})" for _, row in peak.iterrows()]
    values = peak['requests_per_sec']

    plt.figure()
    plt.bar(labels, values, color='skyblue')
    plt.title("Peak Requests/sec by Server Type and Python Flavor")
    plt.ylabel("Requests per Second")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("peak_bar_plot.png")
    plt.close()

if __name__ == '__main__':
    args = parse_args()
    results = collect_results(args)
    write_csv(results)
    plot_results()
