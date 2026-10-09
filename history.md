# History

For any withdrawn papers, their README files explain the gap. So far there are none.

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
