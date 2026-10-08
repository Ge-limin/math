"""Search for a packing of N n-dimensional subspaces of R^m.

Goal: maximize the minimal squared chordal distance
    D(a, b) = n - ||Q_a^T Q_b||_F^2        (Q_a: orthonormal m x n basis)
which is the sum of squared sines of the principal angles; for n = 1 it is
sin^2 of the angle between two lines. This is the quantity in Sloane's table.

Method: minimize a log-sum-exp of the overlaps S(a, b) = ||Q_a^T Q_b||^2
(a smooth stand-in for the largest overlap) with gradient steps on the
Grassmannian, raising the sharpness p over time so the soft maximum turns into
the true maximum. Many random starts; the best is kept.

    python solve.py M N_SUB N SECONDS SEED OUT.npy
"""
import sys
import time
import numpy as np


def overlaps(Q):
    M = np.einsum("aik,bil->abkl", Q, Q)            # Q_a^T Q_b
    S = (M * M).sum(axis=(2, 3))
    return M, S


def min_distance(Q):
    n = Q.shape[2]
    _, S = overlaps(Q)
    iu = np.triu_indices(len(Q), 1)
    return n - S[iu].max()


def orthonormal(X):
    Q, R = np.linalg.qr(X)
    return Q * np.sign(np.einsum("aii->ai", R))[:, None, :]


def run(m, n, N, rng, iters=6000):
    Q = orthonormal(rng.normal(size=(N, m, n)))
    iu = np.triu_indices(N, 1)
    mask = np.zeros((N, N), bool)
    mask[iu] = True
    mask |= mask.T
    lr0 = 0.05
    for t in range(iters):
        frac = t / iters
        p = 10.0 * (400.0 ** frac)                     # sharpness 10 -> 4000
        lr = lr0 * (0.02 ** frac)
        M, S = overlaps(Q)
        Smax = S[mask].max()
        W = np.where(mask, np.exp(p * (S - Smax)), 0.0)
        W /= W.sum()
        G = 2.0 * np.einsum("ab,bil,abkl->aik", W + W.T, Q, M)
        G -= np.einsum("aij,ajk->aik", Q, np.einsum("aji,ajk->aik", Q, G))   # tangent part
        norm = np.sqrt((G * G).sum()) + 1e-30
        Q = orthonormal(Q - lr * G / norm * np.sqrt(N))
    return Q, min_distance(Q)


def polish(Q, iters=4000):
    """Finish the best start: much sharper soft maximum and much smaller steps."""
    N = len(Q)
    iu = np.triu_indices(N, 1)
    mask = np.zeros((N, N), bool)
    mask[iu] = True
    mask |= mask.T
    best, bestQ = min_distance(Q), Q
    for t in range(iters):
        frac = t / iters
        p = 4000.0 * (100.0 ** frac)                   # 4e3 -> 4e5
        lr = 2e-3 * (0.05 ** frac)
        M, S = overlaps(Q)
        Smax = S[mask].max()
        W = np.where(mask, np.exp(p * (S - Smax)), 0.0)
        W /= W.sum()
        G = 2.0 * np.einsum("ab,bil,abkl->aik", W + W.T, Q, M)
        G -= np.einsum("aij,ajk->aik", Q, np.einsum("aji,ajk->aik", Q, G))
        norm = np.sqrt((G * G).sum()) + 1e-30
        Q = orthonormal(Q - lr * G / norm * np.sqrt(N))
        if t % 50 == 0 or t == iters - 1:
            d = min_distance(Q)
            if d > best:
                best, bestQ = d, Q
    return bestQ, best


def main():
    m, n, N, seconds, seed, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    rng = np.random.default_rng(seed)
    best, bestQ, starts, t0 = -1.0, None, 0, time.time()
    while time.time() - t0 < seconds or bestQ is None:
        Q, d = run(m, n, N, rng)
        starts += 1
        if d > best:
            best, bestQ = d, Q
    rough = best
    bestQ, best = polish(bestQ)
    np.save(out, bestQ)
    print(f"m={m} n={n} N={N} D={best:.12f} starts={starts} rough={rough:.12f} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
