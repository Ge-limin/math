# History

For any withdrawn papers, their README files explain the gap and the manuscript stays in place.

## October 9, 2026 (update)

**Withdrawals**

An audit of the release found three manuscripts that should not be in the catalogue. We have withdrawn them:

- A Packing of 5 Four-Spaces in R10: the value stated, 2.999999, is the simplex bound 3 minus the precision of the search. The cell's optimum is very likely exactly 3, which the manuscript does not prove.
- A Packing of 98 Four-Spaces in R12 and A Packing of 96 Four-Spaces in R12: the two smallest margins over the trivial bound in the collection (0.0000106 and 0.0000117), each obtained by deleting one subspace from this collection's own packing for N + 1. They improve on this collection, not on anything published.

The withdrawn manuscripts now carry notices explaining the problem. Each withdrawal concerns the statement or its significance; none asserts that a configuration is wrong.

**Fixes**

None.

**Verifications**

This brings the total of top-line results verified to 719 / 719 = 100%.

## October 9, 2026

**Initial release**

722 manuscripts in 26 result families.

**Withdrawals before release**

- 609 planned cells were dropped because Henry Cohn's current version of the Grassmannian table had already filled them. See [the reasoning summary](reasoning_traces/already-filled-cells.md).
- 141 computed cells were rejected because deleting points from a known larger configuration already did as well, among them all 18 cells for lines in R^8, which the E8 line system had already won. See [the reasoning summary](reasoning_traces/e8-lines.md).
- 327 accepted cells were left out of the catalogue to reach exactly 722. See [the reasoning summary](reasoning_traces/reaching-722.md).

**Fixes**

Cells whose first search did not beat the trivial bound were tried again starting from a known packing a few sizes larger, with subspaces deleted and the rest polished ([`grassmann/repair.py`](grassmann/repair.py)); 7 were recovered.

**Verifications**

All 722 manuscripts are verified exactly. This brings the share of top-line results verified to 722 / 722 = 100%.
