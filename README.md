# Readme

This repository contains mathematical manuscripts and supporting verification artifacts produced by Claude, a publicly available Anthropic model, on one laptop.

On October 6, 2026, OpenAI released [722 mathematical manuscripts](https://github.com/openai/math) and withdrew three of them the next day, leaving 719. This repository has the same numbers, in the same layout. The results are much smaller. Each one fills a blank cell of a public table of best-known geometric configurations with a configuration whose value is checked exactly. None of them were submitted to the tables' maintainers; they live only here.

This collection includes results at one stage of verification. All of them have accompanying exact verifications.

Some of the results could be trivial. Most of them are.

## Navigating the collection

The current catalogue contains 719 manuscripts organized into 26 families. A family groups related papers; here that means the blank cells of one row of one table. Each family is classified by mathematical discipline.

- Start with the [overview](overview.pdf) for descriptions of the families.
- Use the [manuscript map](CONTENTS.md) to find individual papers and their supporting materials.
- The [`preprints/`](preprints/) directory contains PDFs, source files, and manuscript-specific citation and check instructions.
- The [exact verifications](exact/README.md) and [verification catalogue](exact/verification.yaml) give every claimed value, its data file and the command that checks it. The repository has 100% of top-line results verified (719 / 719).
- Updates to the repo are described in the [history](history.md).

### Reasoning summaries

We are also releasing abridged summaries of the model's reasoning, covering the following results:

| Family | Subject |
|---|---|
| 001–025 | [The 609 cells someone had already filled](reasoning_traces/already-filled-cells.md) |
| — | [Eighteen cells the E8 lattice had already won](reasoning_traces/e8-lines.md) |
| 001–026 | [Reaching 722, then 719](reasoning_traces/reaching-722.md) |

## How the results were produced

All results were obtained with the same procedure using Claude Opus 5.5. On average, each Grassmannian result used about two minutes of laptop compute, with about ten searches running at once; the whole collection took one night, October 8–9, 2026. Over the course of the evaluation, the model was posed approximately two problems: fill the blank cells, and reach 722. Aggregating the output into result families and manuscripts and requiring an appropriate level of significance led to the catalog outlined above.

Concretely, 1,049 cells passed the checks below. The catalogue holds all 660 Grassmannian cells with N ≤ 100, the range the table computes systematically, and all 19 plane results (n = 32..50), plus the 43 cells with N = 101..120 that beat their trivial bound by the widest margin. The other 327 are listed in [`grassmann/RESULTS.md`](grassmann/RESULTS.md). That made 722 manuscripts at release; three were then withdrawn, as described in the [history](history.md).

There are no exceptions to this fixed procedure. No writeup was edited by a human for readability; every manuscript was generated from one template ([`catalogue.py`](catalogue.py)).

## What counts as a result

One result is one cell (a problem at one size) of a public table that had no published value, for which this repository gives a configuration whose value is

1. **verified exactly** from published integer coordinates with rational arithmetic, no floating point;
2. **strictly better than the trivial bound** for that cell: the best value known for any larger size in the same table row, since a subset of a larger configuration is a configuration;
3. **within the known upper bound** (the Rankin simplex bound for Grassmannian packings).

Nothing here is proven optimal. Each value is a bound: the best we found.

## Sources and what was checked

- **Grassmannian packings.** N. J. A. Sloane's [Table of Best Grassmannian Packings](https://neilsloane.com/grass/grassTab.html) (last modified 1997), now maintained by Henry Cohn at [cohn.mit.edu/grassmannian](https://cohn.mit.edu/grassmannian) (checked October 8, 2026). A cell is the packing of N n-dimensional subspaces of R^m; the value is the minimal squared chordal distance (sum of squared sines of the principal angles). Blank means: no value in Sloane's table, in Sloane's per-dimension coordinate files, or in Cohn's current table. Literature also checked: Dhillon–Heath–Strohmer–Tropp 2008, Fickus–Jasper–Mixon "Packings in real projective spaces", the complex "Game of Sloanes" tables, and GitHub.
- **Plane max/min distance ratio.** Erich Friedman's page [Minimizing the Ratio of Maximum to Minimum Distance](https://erich-friedman.github.io/packing/maxmin/) lists n ≤ 31. Value: (largest distance / smallest distance)^2, smaller is better. Our code reproduces the page's n = 30 value (26.879+).

The search code is in [`grassmann/`](grassmann/) and [`friedman-maxmin2d/`](friedman-maxmin2d/), the same method as [maxmin3-records](https://github.com/Ge-limin/maxmin3-records).

## Versions and citations

We will preserve the release history of this collection. Corrections and revisions will be recorded as new versions, with previously released versions remaining accessible.

To cite an individual manuscript, use the BibTeX block in its directory.

This repository follows [openai/math](https://github.com/openai/math). When that repository changes, an issue is opened here automatically ([`.github/workflows/follow-openai.yml`](.github/workflows/follow-openai.yml)), and this collection is updated to match.

Issues, pull requests and discussions are open.

## License

MIT for the code. The configurations are free to use; a link back is appreciated.
