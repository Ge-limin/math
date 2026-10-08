"""Exact check of a Grassmannian packing, independent of the search code.

Each subspace is given by an m x n integer matrix Y (the published basis,
coordinates scaled by 10^12 and rounded). Its projection is P = Y G^-1 Y^T
with G = Y^T Y, so for two subspaces
    tr(P_a P_b) = tr(adj(G_a) A adj(G_b) A^T) / (det G_a det G_b),  A = Y_a^T Y_b
is an exact rational, and so is D(a, b) = n - tr(P_a P_b). No orthonormality is
assumed and no floating point is used.

    python verify.py packing.txt     # prints the exact minimal distance
"""
import sys
from fractions import Fraction
from itertools import combinations


def det(G):
    n = len(G)
    if n == 1:
        return G[0][0]
    if n == 2:
        return G[0][0] * G[1][1] - G[0][1] * G[1][0]
    return sum((-1) ** j * G[0][j] * det([row[:j] + row[j + 1:] for row in G[1:]]) for j in range(n))


def adj(G):
    n = len(G)
    if n == 1:
        return [[1]]
    minor = lambda i, j: [r[:j] + r[j + 1:] for k, r in enumerate(G) if k != i]
    return [[(-1) ** (i + j) * det(minor(j, i)) for j in range(n)] for i in range(n)]


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A):
    return [list(r) for r in zip(*A)]


def read(path):
    """Header '# m n N', then N blocks of m lines with n integers each."""
    lines = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
    head = [l for l in open(path) if l.startswith("# m n N")][0].split()[4:7]
    m, n, N = map(int, head)
    vals = [[int(x) for x in l] for l in lines]
    assert len(vals) == m * N and all(len(r) == n for r in vals)
    return m, n, N, [vals[k * m:(k + 1) * m] for k in range(N)]


def exact_min_distance(m, n, Ys):
    info = []
    for Y in Ys:
        G = matmul(transpose(Y), Y)
        d = det(G)
        assert d != 0, "degenerate basis"
        info.append((transpose(Y), adj(G), d))
    best = None
    for (Yta, adja, da), (Ytb, adjb, db) in combinations(info, 2):
        A = matmul(Yta, transpose(Ytb))                       # Y_a^T Y_b
        T = matmul(matmul(adja, A), matmul(adjb, transpose(A)))
        tr = Fraction(sum(T[i][i] for i in range(n)), da * db)
        D = n - tr
        if best is None or D < best:
            best = D
    return best


if __name__ == "__main__":
    m, n, N, Ys = read(sys.argv[1])
    D = exact_min_distance(m, n, Ys)
    print(f"m={m} n={n} N={N} exact min D = {float(D):.15f}")
