"""Publish the plane max/min distance ratio results for n = 32..50.

Erich Friedman's page "Minimizing the Ratio of Maximum to Minimum Distance"
(erich-friedman.github.io/packing/maxmin/) lists n <= 31. For n = 32..50:
  1. export coords/nN.txt on a 10^-12 grid and compute r^2 exactly (verify.py);
  2. accept n only if r^2(n) is strictly smaller than r^2(n+1) of our packing for
     n + 1 (deleting a point from it is the trivial way to get n points);
     n = 50 has no larger packing of ours, so it is accepted on verification alone.
Writes results2d.json and RESULTS.md.
"""
import json
import os
from decimal import Decimal, ROUND_FLOOR

import numpy as np

from verify import exact_ratio2, grid_points

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs(os.path.join(HERE, "coords"), exist_ok=True)
    vals = {}
    for n in range(30, 51):
        p = os.path.join(HERE, "bests", f"n{n}.npy")
        if not os.path.exists(p):
            continue
        P = grid_points(np.load(p).tolist())
        r = exact_ratio2(P)
        vals[n] = r
        with open(os.path.join(HERE, "coords", f"n{n}.txt"), "w") as f:
            f.write(f"# n={n} points in the plane; r^2 = (max squared distance)/(min squared distance) = {r.numerator}/{r.denominator}\n")
            f.write("# x y per line, exact decimals with 12 digits after the point\n")
            for x, y in P:
                f.write(f"{x / 10**12:.12f} {y / 10**12:.12f}\n")
    rows = []
    for n in range(32, 51):
        if n not in vals:
            continue
        r = vals[n]
        nxt = vals.get(n + 1)
        ok = nxt is None or r < nxt
        v = (Decimal(r.numerator) / Decimal(r.denominator)).quantize(Decimal("0.00001"), rounding=ROUND_FLOOR)
        rows.append({"n": n, "r2_exact": f"{r.numerator}/{r.denominator}", "r2": f"{v}+",
                     "r2_next": float(nxt) if nxt else None, "accepted": bool(ok)})
    json.dump(rows, open(os.path.join(HERE, "results2d.json"), "w"), indent=1)
    acc = sum(r["accepted"] for r in rows)
    with open(os.path.join(HERE, "RESULTS.md"), "w") as f:
        f.write(f"# Results: plane max/min distance ratio\n\nAccepted: {acc} of {len(rows)} (n = 32..50).\n"
                f"For reference our n=30 is {float(vals[30]):.6f} (page: 26.879+), n=31 {float(vals.get(31, 0)):.6f} (page: 28).\n\n"
                "| n | r^2 (truncated) | accepted |\n|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['n']} | {r['r2']} | {'yes' if r['accepted'] else 'no'} |\n")
    print(f"accepted {acc} of {len(rows)}")


if __name__ == "__main__":
    main()
