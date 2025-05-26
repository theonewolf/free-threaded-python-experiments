# Python Concurrency Server Benchmarks

This project contains a set of simple Python network servers designed to benchmark the performance and behavior of threading and multiprocessing models, particularly in the context of the Global Interpreter Lock (GIL) and free-threaded Python (e.g., Python 3.12+ `nogil` builds).

It includes tools to benchmark, visualize, and compare how different concurrency strategies perform under CPU-bound and I/O-bound workloads.

---

## 🔧 Project Structure

```bash
.
├── benchmark.py                 # Benchmark client for generating load
├── controller.py                # Orchestrates benchmarks and collects results
├── threaded-server.py           # Thread-per-connection server
├── threaded-server-simple.py    # Minimal version of the above
├── multiprocess-server.py       # Process-per-core server using SO_REUSEPORT
├── multiprocess-server-simple.py# Minimal version of the above
├── figures/
│   ├── free-threading-cores.png # Visual: CPU core use in nogil Python
│   ├── gil-cores.png            # Visual: CPU core use in standard Python
│   └── python-cores.svg         # Source SVG for diagrams
├── run.sh                       # Main script to run the benchmarks
├── setup.sh                     # Environment and dependency setup
├── clean.sh                     # Cleanup utility
├── LICENSE                      # MIT license
└── README.md                    # You’re reading it!
```

---

## 🚀 Usage

### 1. Set up the environment

Install dependencies using the provided setup script:

```bash
./setup.sh
```

> Note: Note: You may need to run with bash explicitly depending on your shell.

### 2. Run a threaded or multiprocess server

#### Threaded example:

```bash
python threaded-server.py 8 compute
```

#### Multiprocess example:

```bash
python multiprocess-server.py 8 compute
```

- The first argument is the number of threads or processes.
  - The second argument is the mode:
  - `echo`: I/O-bound workload
  - `compute`: CPU-bound workload (simulated heavy loop)

#### Benchmark with `benchmark.py`:

Run the benchmark tool in another terminal:

```bash
python benchmark.py 4 15
```

- The first argument is the number of benchmark threads
- The second argument is the time to run in seconds

#### Run all Benchmarks

```bash
./run.sh
```

This script runs all server variants and captures results using the controller Python script.

#### Cleanup

```bash
./clean.sh
```

Deletes all temporary files.

## 📊 Figures

The figures/ directory contains visuals showing CPU utilization differences:
- `gil-cores.png` — Threaded Python under the GIL.
- `free-threading-cores.png` — Free-threaded Python (nogil).
- `python-cores.svg` — Editable source diagram (SVG).  Made with Inkscape.

## 🧠 Why This Exists

This repo explores:
- How the GIL affects multi-threaded server performance.
- The benefit of multiprocessing in standard Python.
- The performance impact of free-threaded Python (3.14+).
- The behavior of `SO_REUSEPORT` for load balancing processes.

## 📝 License

This project is released under the MIT License.

## 🙋 Questions or Contributions?

Issues and pull requests are welcome. If you’re experimenting with nogil Python or concurrency in general, feel free to contribute!
