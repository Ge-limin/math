"""Write README.md from the finalized results (grassmann/results.json, friedman-maxmin2d/results2d.json)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(HERE, "grassmann", "results.json")))
p = json.load(open(os.path.join(HERE, "friedman-maxmin2d", "results2d.json")))
band = lambda b: sum(r["accepted"] for r in g if r["band"] == b)
core, ext, sparse, plane = band("N<=100"), band("N=101..120"), band("sparse row"), sum(r["accepted"] for r in p)
total = core + ext + sparse + plane

readme = f"""# math719

{total} first values for blank cells of public tables of best-known geometric configurations,
computed on one laptop with Claude (Anthropic's model) in one night, October 8–9, 2026.

The number 719 was the target because on October 6, 2026 OpenAI published
[719 mathematical manuscripts](https://github.com/openai/math). These are not that: each result
here is one entry of a table that nobody had filled, found by numerical search and checked exactly.
None of it was submitted to the tables' maintainers. It lives only here.

## What counts as a result

One result is one cell (a problem at one size) of a public table that had no published value,
for which this repository gives a configuration whose value is

1. **verified exactly** from published integer coordinates with rational arithmetic, no floating point;
2. **strictly better than the trivial bound** for that cell: the best value known for any larger
   size in the same table row, since a subset of a larger configuration is a configuration;
3. **within the known upper bound** (the Rankin simplex bound for Grassmannian packings).

Nothing here is proven optimal. Each value is a lower bound: the best we found.

## Counts

| Source | Band | Results |
|---|---|---|
| Grassmannian packings (Sloane / Cohn table) | N ≤ 100, rows the tables compute systematically | {core} |
| Grassmannian packings | N = 101..120, inside rows the table extends past 120 | {ext} |
| Grassmannian packings | "sparse rows": rows where the table lists one special construction; N above it, up to 100 | {sparse} |
| Plane max/min distance ratio (Friedman) | n = 32..50 | {plane} |
| **Total** | | **{total}** |

The first band and the plane results ({core + plane}) are the least arguable. The other two bands
extend rows rather than fill gaps inside a computed range; they are listed separately so anyone can
draw the line where they like.

## Sources and what was checked

- **Grassmannian packings.** N. J. A. Sloane's [Table of Best Grassmannian Packings](https://neilsloane.com/grass/grassTab.html)
  (last modified 1997), now maintained by Henry Cohn at [cohn.mit.edu/grassmannian](https://cohn.mit.edu/grassmannian)
  (checked October 8, 2026). A cell is the packing of N n-dimensional subspaces of R^m; the value is the
  minimal squared chordal distance (sum of squared sines of the principal angles). Blank means: no value
  in Sloane's table, in Sloane's per-dimension coordinate files, or in Cohn's current table. Literature also
  checked: Dhillon–Heath–Strohmer–Tropp 2008, Fickus–Jasper–Mixon "Packings in real projective spaces",
  the complex "Game of Sloanes" tables, and GitHub. About 600 cells we first planned turned out to be filled
  in Cohn's table and were dropped; cells dominated by a known special construction (for example subsets of
  the E8 line system) are rejected by the trivial-bound rule above.
- **Plane max/min distance ratio.** Erich Friedman's page
  [Minimizing the Ratio of Maximum to Minimum Distance](https://erich-friedman.github.io/packing/maxmin/) lists
  n ≤ 31. Value: (largest distance / smallest distance)^2, smaller is better. Our code reproduces the page's
  n = 30 value (26.879+).

## Method

- Grassmannian: many random starts of gradient descent on the Grassmannian against a log-sum-exp of the
  pairwise overlaps, sharpened over time, then a polishing stage (`grassmann/solve.py`). Calibrated on
  cells that the table does list: 99.4–99.97 % of the listed values within about a minute per cell.
- Plane: random starts of a constrained local optimizer (SLSQP), then basin hopping seeded from the
  neighbouring sizes (`friedman-maxmin2d/`), the same method as
  [maxmin3-records](https://github.com/Ge-limin/maxmin3-records).

## Check it yourself

- `grassmann/packings/mMnNN.txt`: integer bases (coordinates × 10^12). `python grassmann/verify.py FILE`
  prints the exact minimal distance using only integers and fractions.
- `friedman-maxmin2d/coords/nN.txt`: point coordinates; the header carries the exact ratio.
- `grassmann/RESULTS.md`, `grassmann/results.json`, `friedman-maxmin2d/RESULTS.md`: every cell with its value,
  trivial bound and whether it was accepted.

## License

MIT for the code. The configurations are free to use; a link back is appreciated.
"""
open(os.path.join(HERE, "README.md"), "w").write(readme)
print("README total", total, "core", core, "ext", ext, "sparse", sparse, "plane", plane)
