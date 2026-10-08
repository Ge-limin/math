"""Second chance for cells whose search result did not beat the trivial bound.

The trivial bound for N is a known packing with more subspaces, minus some of
them. So start exactly there: take each known packing with N' = N+1..N+5
(ours in results/, or Sloane's coordinate files grassc.m.n.N'.txt), drop
subspaces one at a time (from the closest pair, whichever drop helps more),
then polish. Keep the result only if it is better than what results/ holds.
Cells are processed from large N to small, since a repaired cell raises the
trivial bound of the cell below it.

    python repair.py SLOANE_FILES_DIR
"""
import json
import os
import re
import sys

import numpy as np

from solve import min_distance, orthonormal, polish

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")


def load_sloane(path, m, n, N):
    x = np.array([float(t) for t in open(path).read().split()])
    assert x.size == m * n * N
    return orthonormal(np.transpose(x.reshape(N, n, m), (0, 2, 1)))


def shrink(Q, N):
    """Drop subspaces until N remain, each time removing one of the closest pair."""
    while len(Q) > N:
        _, S = None, None
        M = np.einsum("aik,bil->abkl", Q, Q)
        S = (M * M).sum(axis=(2, 3))
        np.fill_diagonal(S, -1)
        a, b = np.unravel_index(np.argmax(S), S.shape)
        Qa, Qb = np.delete(Q, a, 0), np.delete(Q, b, 0)
        Q = Qa if min_distance(Qa) >= min_distance(Qb) else Qb
    return Q


def starts(m, n, N, sloane_dir):
    for NN in range(N + 1, N + 6):
        ours = os.path.join(RES, "m%dn%dN%d.npy" % (m, n, NN))
        if os.path.exists(ours):
            yield f"ours N={NN}", np.load(ours)
        f = os.path.join(sloane_dir, "grassc.%d.%d.%d.txt" % (m, n, NN))
        if os.path.exists(f):
            yield f"Sloane N={NN}", load_sloane(f, m, n, NN)


def main():
    sloane_dir = sys.argv[1]
    rows = json.load(open(os.path.join(HERE, "results.json")))
    known = {tuple(map(int, k.split(","))): {int(N): v for N, v in d.items()}
             for k, d in json.load(open(os.path.join(HERE, "known-table.json"))).items()}

    def reachable(r):   # the value to beat comes from a configuration at most 5 larger
        far = [v for NN, v in known.get((r["m"], r["n"]), {}).items() if NN > r["N"] + 5]
        return not far or max(far) < r["trivial_bound"] - 1e-12

    todo = sorted([(r["m"], r["n"], r["N"]) for r in rows if not r["accepted"] and reachable(r)],
                  key=lambda c: (c[0], c[1], -c[2]))
    if len(sys.argv) > 3:                          # shard K of SHARDS, whole table rows per shard
        k, shards = int(sys.argv[2]), int(sys.argv[3])
        todo = [c for c in todo if hash((c[0], c[1])) % shards == k]
    for m, n, N in todo:
        path = os.path.join(RES, "m%dn%dN%d.npy" % (m, n, N))
        current = min_distance(np.load(path)) if os.path.exists(path) else -1
        best, bestQ, src = current, None, None
        for label, Q0 in starts(m, n, N, sloane_dir):
            Q = shrink(Q0, N)
            Q, d = polish(Q, iters=3000)
            if d > best:
                best, bestQ, src = d, Q, label
        if bestQ is not None:
            np.save(path, bestQ)
        print(f"m={m} n={n} N={N}: {current:.9f} -> {best:.9f}" + (f" (from {src})" if src else " (no improvement)"), flush=True)


if __name__ == "__main__":
    main()
