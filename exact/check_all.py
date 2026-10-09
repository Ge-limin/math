"""Re-check every manuscript in the collection from its published data file.

For each entry of catalogue.json, recompute the exact value with the verifier
(integers and fractions only) and compare it with the value the manuscript
states. Prints one line per failure and a summary with the elapsed time.

    python exact/check_all.py [WORKERS]
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, "grassmann")]
import verify as grass  # noqa: E402



def check(x):
    path = os.path.join(ROOT, x["data"])
    if x["kind"] == "grassmann":
        m, n, N, Ys = grass.read(path)
        value = grass.exact_min_distance(m, n, Ys)
    else:
        lines = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
        P = [(int(a.replace(".", "").replace("-", "")) * (-1 if a.startswith("-") else 1),
              int(b.replace(".", "").replace("-", "")) * (-1 if b.startswith("-") else 1)) for a, b in lines]
        d = [(p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for i, p in enumerate(P) for q in P[i + 1:]]
        value = Fraction(max(d), min(d))
    return x["slug"], value == Fraction(x["exact"])


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    ms = json.load(open(os.path.join(ROOT, "catalogue.json")))["manuscripts"]
    t0, bad = time.time(), []
    with ProcessPoolExecutor(workers) as ex:
        for slug, ok in ex.map(check, ms, chunksize=4):
            if not ok:
                bad.append(slug)
                print("MISMATCH", slug, flush=True)
    print(f"checked {len(ms)}, mismatches {len(bad)}, {time.time() - t0:.0f} s with {workers} workers")


if __name__ == "__main__":
    main()
