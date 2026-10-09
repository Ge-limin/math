# Exact verifications

This directory contains exact verifications of all results in this repository.
They are organized in two small scripts, one per table ([`grassmann/verify.py`](../grassmann/verify.py), 73 lines; [`friedman-maxmin2d/verify.py`](../friedman-maxmin2d/verify.py)), so we recommend checking all of them at once:

```
python exact/check_all.py 4
```

It recomputes every manuscript's value from its published data file with integers and fractions only, and compares it with the value the manuscript states. See the [verification catalogue](verification.yaml) for each manuscript's claim, data file and check command.

## Technical note: time

Checking the entire collection takes about 15 seconds on a laptop with 4 workers.
