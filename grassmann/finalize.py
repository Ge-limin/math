"""Turn finished cells into published, exactly verified results.

For each cell with results/<cell>.npy:
  1. write packings/<cell>.txt: integer bases (coordinates x 10^12, rounded);
  2. verify the exact minimal distance from that file (verify.py, no floats);
  3. accept the cell only if the value is strictly larger than the trivial
     bound for that N: the best value known for any larger N in the same row,
     from Sloane's table or from our own results (a subset of a larger packing
     is a packing), and not above the Rankin simplex bound.
Writes results.json and RESULTS.md. Run as often as you like; cached by file.

    python finalize.py [WORKERS]
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal, ROUND_FLOOR
from fractions import Fraction

import numpy as np

from verify import exact_min_distance, read

HERE = os.path.dirname(os.path.abspath(__file__))
RES, PACK = os.path.join(HERE, "results"), os.path.join(HERE, "packings")
SCALE = 10 ** 12


def export(cell):
    m, n, N = cell
    Q = np.load(os.path.join(RES, "m%dn%dN%d.npy" % cell))
    path = os.path.join(PACK, "m%dn%dN%d.txt" % cell)
    with open(path, "w") as f:
        f.write(f"# Packing of N={N} {n}-dimensional subspaces of R^{m}; each block is an m x n basis (integers / 10^12)\n")
        f.write(f"# m n N {m} {n} {N}\n")
        for Y in Q:
            for row in np.rint(Y * SCALE).astype(np.int64):
                f.write(" ".join(str(int(x)) for x in row) + "\n")
    return path


def check(cell):
    path = export(cell)
    m, n, N, Ys = read(path)
    D = exact_min_distance(m, n, Ys)
    return cell, D.numerator, D.denominator


def trunc(x, places=6):
    return str(Decimal(x.numerator) / Decimal(x.denominator)).split(".")[0] + "." + \
        str((Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal(10) ** -places, rounding=ROUND_FLOOR)).split(".")[1]


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    os.makedirs(PACK, exist_ok=True)
    cache_path = os.path.join(HERE, "exact-cache.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    cells = sorted(tuple(map(int, f[1:-4].replace("n", " ").replace("N", " ").split()))
                   for f in os.listdir(RES) if f.endswith(".npy"))
    core = {tuple(c) for c in json.load(open(os.path.join(HERE, "blanks-cohn-100.json")))}
    core |= {tuple(c) for c in json.load(open(os.path.join(HERE, "blanks-cohn-n4.json")))}   # n = 4 rows, N <= 100
    extra = {tuple(c) for c in json.load(open(os.path.join(HERE, "blanks-cohn-101-120.json")))}
    sparse = {tuple(c) for c in json.load(open(os.path.join(HERE, "blanks-sparse-rows.json")))}
    cells = [c for c in cells if c in core or c in extra or c in sparse]       # only cells with no published value
    todo = []
    for c in cells:
        key = "m%dn%dN%d" % c
        mtime = os.path.getmtime(os.path.join(RES, key + ".npy"))
        if key not in cache or cache[key]["mtime"] != mtime:
            todo.append((c, mtime))
    with ProcessPoolExecutor(workers) as ex:
        for (cell, num, den), (_, mtime) in zip(ex.map(check, [c for c, _ in todo]), todo):
            cache["m%dn%dN%d" % cell] = {"num": num, "den": den, "mtime": mtime}
    json.dump(cache, open(cache_path, "w"))

    # reference values: Sloane's 1997 table merged with Cohn's current table (cohn.mit.edu/grassmannian)
    table = {tuple(map(int, k.split(","))): {int(N): v for N, v in d.items()}
             for k, d in json.load(open(os.path.join(HERE, "known-table.json"))).items()}
    ours = {c: Fraction(cache["m%dn%dN%d" % c]["num"], cache["m%dn%dN%d" % c]["den"]) for c in cells}
    rows, accepted = [], 0
    for (m, n, N), D in sorted(ours.items()):
        larger = [v for NN, v in table.get((m, n), {}).items() if NN > N] + \
                 [float(v) for (mm, nn, NN), v in ours.items() if (mm, nn) == (m, n) and NN > N]
        trivial = max(larger) if larger else 0.0
        rankin = n * (m - n) / m * N / (N - 1)
        smaller_N = [NN for NN in table.get((m, n), {}) if NN < N]
        next_smaller = table[(m, n)][max(smaller_N)] if smaller_N else None
        ok = float(D) > trivial * (1 + 1e-9) and float(D) <= rankin + 1e-12
        accepted += ok
        rows.append({"m": m, "n": n, "N": N, "band": "N<=100" if (m, n, N) in core else ("sparse row" if (m, n, N) in sparse else "N=101..120"), "D_exact": f"{D.numerator}/{D.denominator}", "D": trunc(D),
                     "trivial_bound": trivial, "rankin_bound": rankin,
                     "table_at_next_smaller_N": next_smaller, "margin_over_trivial": float(D) - trivial, "accepted": ok})
    json.dump(rows, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    keep = {"m%dn%dN%d.txt" % (r["m"], r["n"], r["N"]) for r in rows if r["accepted"]}
    for f in os.listdir(PACK):                       # publish only accepted cells
        if f.endswith(".txt") and f not in keep:
            os.remove(os.path.join(PACK, f))
    with open(os.path.join(HERE, "RESULTS.md"), "w") as f:
        f.write(f"# Results\n\nAccepted: {accepted} of {len(rows)} computed cells.\n\n")
        f.write("| band | accepted | computed |\n|---|---|---|\n")
        for band in ("N<=100", "N=101..120", "sparse row"):
            f.write(f"| {band} | {sum(r['accepted'] for r in rows if r['band'] == band)} | {sum(r['band'] == band for r in rows)} |\n")
        f.write("\n")
        f.write("| m | n | N | min squared distance D (truncated) | trivial bound | margin | accepted |\n|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['m']} | {r['n']} | {r['N']} | {r['D']} | {r['trivial_bound']:.6f} | {r['margin_over_trivial']:.2e} | {'yes' if r['accepted'] else 'no'} |\n")
    print(f"accepted {accepted} of {len(rows)}")


if __name__ == "__main__":
    main()
