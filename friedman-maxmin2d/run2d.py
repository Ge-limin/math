"""Plane version of the maxmin3 pipeline: n = 30..50, random starts then basin hopping.
Low priority (nice 10) so the Grassmannian batch keeps the CPU. Resumable via logs/done_nN."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); PY = os.path.join(HERE, "..", ".venv", "bin", "python")
def run(script, n, secs, tag):
    ps = [subprocess.Popen(["nice", "-n", "10", PY, os.path.join(HERE, script), str(n), str(secs), str(n * 100 + tag * 10 + w)],
                           cwd=HERE, stdout=open(os.path.join(HERE, "logs", f"n{n}.log"), "a"), stderr=subprocess.STDOUT) for w in (1, 2)]
    for p in ps: p.wait()
for n in range(30, 51):
    if os.path.exists(os.path.join(HERE, "logs", f"done_n{n}")): continue
    run("search.py", n, 300, 1)
    run("improve.py", n, 600, 2)
    open(os.path.join(HERE, "logs", f"done_n{n}"), "w").close()
open(os.path.join(HERE, "logs", "DONE"), "w").close()
