"""Compute every blank cell, a few at a time, sized to the machine's load.

Resumable: a cell with results/<cell>.npy is done and skipped. Progress goes to
results/progress.log. Start detached so it survives the terminal:

    python run_all.py [MAX_WORKERS]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
PY = os.path.join(HERE, "..", ".venv", "bin", "python")
MAX_WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 10
LOAD_CEILING = float(sys.argv[2]) if len(sys.argv) > 2 else 13.0   # 1-min load average, our own workers included


def cells():
    """The work queue (queue.json): blank cells not dominated by a known construction, in order."""
    return [tuple(c) for c in json.load(open(os.path.join(HERE, "queue.json")))]


def budget(m, n, N):
    return 60 + int(90 * (N / 100) ** 2 * (m * n / 48))     # seconds of random starts before polishing


def log(msg):
    with open(os.path.join(OUT, "progress.log"), "a") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    def busy(c):   # a solver from an earlier scheduler is still working on this cell
        lg = os.path.join(OUT, "m%dn%dN%d.log" % c)
        return os.path.exists(lg) and time.time() - os.path.getmtime(lg) < 1200
    todo = [c for c in cells() if not os.path.exists(os.path.join(OUT, "m%dn%dN%d.npy" % c)) and not busy(c)]
    log(f"start: {len(todo)} cells to do, max {MAX_WORKERS} workers")
    running = []
    while todo or running:
        running = [(c, p) for c, p in running if p.poll() is None]
        load = os.getloadavg()[0]
        if todo and len(running) < MAX_WORKERS and (load < LOAD_CEILING or not running):
            m, n, N = todo.pop(0)
            name = "m%dn%dN%d" % (m, n, N)
            p = subprocess.Popen([PY, os.path.join(HERE, "solve.py"), str(m), str(n), str(N), str(budget(m, n, N)),
                                  str(1000 * m + 100 * n + N), os.path.join(OUT, name + ".npy")],
                                 stdout=open(os.path.join(OUT, name + ".log"), "w"), stderr=subprocess.STDOUT)
            running.append(((m, n, N), p))
            time.sleep(1)
            continue
        time.sleep(5)
        done = len([f for f in os.listdir(OUT) if f.endswith(".npy")])
        if int(time.time()) % 300 < 5:
            log(f"done {done}, running {len(running)}, queued {len(todo)}, load {load:.1f}")
    log("all cells finished")
    open(os.path.join(OUT, "DONE"), "w").close()


if __name__ == "__main__":
    main()
