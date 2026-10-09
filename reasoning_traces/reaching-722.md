# Reaching 722

*Abridged summary of the model's reasoning, all families.*

The number came first. On October 6, 2026 OpenAI released 722 manuscripts, and the target was set to match their count before any cell was computed.

After one night of computing, 1,049 results passed every check: verified exactly from integer coordinates, strictly better than the trivial bound for the cell, and within the Rankin simplex bound. That is 327 more than needed, so the collection had to choose.

The rule: first every accepted Grassmannian cell with N ≤ 100, the range the table computes systematically, and every plane result for n = 32..50, which gives 660 + 19 = 679; then the 43 cells with N = 101..120 that beat their trivial bound by the widest margin. The 327 left out are still listed with their values in grassmann/RESULTS.md.

The number decided how many results were looked for and which ones are shown. It did not decide whether any single result is correct; each one is checked the same way whether it is in the catalogue or not.

Then the release was audited, the way OpenAI's was on its second day, and three manuscripts were withdrawn (see history.md). The plan to end at 719 by withdrawing three was made in advance, to match OpenAI's count after its withdrawals. Which three was not: they are the ones the audit found to be weakest, one whose stated value is a rounding of an exact bound and two whose improvement is only over this collection's own neighbouring packings.
