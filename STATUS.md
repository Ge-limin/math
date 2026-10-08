# math719 — working status

Goal (Limin, 2026-10-08 night): publish, on GitHub only and never submitted to any
maintainer, at least 719 first-ever "trivial" math results — blank cells of public
best-known tables — to set against OpenAI's 719 manuscripts (github.com/openai/math,
2026-10-06). Article and X post come later, separately.

## Counting rule

One result = one previously blank cell (problem, size) of a public table, with
- an exactly verified value (integer coordinates, rational arithmetic, no floats), and
- a value strictly better than the trivial bound for that cell (for these tables:
  the best value known for any larger size, since a subset of a larger packing
  is a packing), and not above the known upper bound (Rankin simplex bound).

## Source 1: Sloane's Table of Best Grassmannian Packings (1997)

- Table: grassmann/sloane-grassTab-1997.html (https://neilsloane.com/grass/grassTab.html),
  parsed into sloane-table.json; blank cells in blanks.json.
- Target: m = 8..16, n = 2, 3, N = 51..100 → 833 cells; n = 1 (lines) → 419 backup cells.
- Calibration on listed cells (60 s + polish): 99.4–99.97 % of the table's values.
- Run: `grassmann/run_all.py` (detached, resumable, load-aware); results in
  grassmann/results/, progress in grassmann/results/progress.log, DONE marker when finished.
- Publish step: `grassmann/finalize.py` exports packings/*.txt (integers), verifies
  exactly with verify.py, applies the counting rule, writes results.json / RESULTS.md.
- Literature check (were these cells filled after 1997?): running, result pending.

## To resume after an interruption

`cd grassmann && ../.venv/bin/python run_all.py 10` (skips finished cells), then
`../.venv/bin/python finalize.py 8`.
