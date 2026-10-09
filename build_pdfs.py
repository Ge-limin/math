"""Compile every manuscript (preprints/<slug>/build/source/paper.tex -> preprints/<slug>/paper.pdf)
and the overview (overview.tex -> overview.pdf) with Tectonic. Skips PDFs newer than their source.

    python build_pdfs.py [WORKERS]
"""
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def stale(pdf, *sources):
    return not os.path.exists(pdf) or any(os.path.getmtime(s) > os.path.getmtime(pdf) for s in sources)


def compile_tex(src_dir, name, target):
    tex = os.path.join(src_dir, name + ".tex")
    deps = [tex] + [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith(".txt")]
    if not stale(target, *deps):
        return None
    r = subprocess.run(["tectonic", "-X", "compile", "--keep-logs", tex, "--outdir", src_dir],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return f"FAIL {tex}\n{r.stderr[-1500:]}"
    shutil.move(os.path.join(src_dir, name + ".pdf"), target)
    return f"ok {os.path.relpath(target, HERE)}"


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    jobs = [(os.path.join(HERE, "preprints", s, "build", "source"), "paper", os.path.join(HERE, "preprints", s, "paper.pdf"))
            for s in sorted(os.listdir(os.path.join(HERE, "preprints")))]
    jobs.append((HERE, "overview", os.path.join(HERE, "overview.pdf")))
    done = failed = 0
    with ThreadPoolExecutor(workers) as ex:
        for msg in ex.map(lambda j: compile_tex(*j), jobs):
            if msg is None:
                continue
            if msg.startswith("FAIL"):
                failed += 1
                print(msg, flush=True)
            else:
                done += 1
    print(f"compiled {done}, failed {failed}, up to date {len(jobs) - done - failed}")


if __name__ == "__main__":
    main()
