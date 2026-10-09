# math (formerly math719) — working status

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
- Literature check (were these cells filled after 1997?): done, see "Night of 2026-10-08/09" below.

## To resume after an interruption

`cd grassmann && ../.venv/bin/python run_all.py 10` (skips finished cells), then
`../.venv/bin/python finalize.py 8`.

## Night of 2026-10-08/09: what happened

- Literature check found that Henry Cohn now maintains the table (cohn.mit.edu/grassmannian) and had
  already filled 609 of the 1,252 cells first planned; those were dropped and the queue rebuilt from
  cells blank in both tables (blanks-cohn-100.json, blanks-cohn-101-120.json).
- Cells dominated by a known special construction (E8 lines in R^8; large constructions in the m=16 rows)
  fail the trivial-bound rule and are reported as not accepted.
- Added n = 4 rows m = 9..13 (blanks-cohn-n4.json) and "sparse rows" (blanks-sparse-rows.json) to reach the target.
- repair.py rebuilt cells whose trivial bound comes from a packing at most 5 larger (7 recovered).
- Second source: plane max/min distance ratio, Friedman's page, n = 32..50 (friedman-maxmin2d/).

## October 9: the collection (layout of github.com/openai/math)

- `catalogue.py` selects 722 of the 1,049 accepted results, OpenAI's count at launch (660 cells N ≤ 100, 19 plane,
  43 widest-margin cells N = 101..120), and writes CONTENTS.md, overview.tex, preprints/<slug>/ (README +
  build/source/paper.tex), exact/verification.yaml, catalogue.json. history.md, reasoning_traces/ and README.md are
  written by hand. `build_pdfs.py` compiles paper.pdf for each manuscript and overview.pdf with Tectonic.
- `exact/check_all.py` re-checks every manuscript from the data files (719 checked earlier: 0 mismatches, 14 s with 4 workers).
- Released 722 (commit c0485a6), then withdrew 3 the way OpenAI did on October 7, ending at 719 (WITHDRAWN in catalogue.py).
