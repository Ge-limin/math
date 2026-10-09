"""Build the manuscript collection from the finalized results.

Selects exactly 719 results, the number of manuscripts in OpenAI's release
(github.com/openai/math, October 6, 2026), and lays them out the way that
repository does:

    CONTENTS.md                 manuscript map: families, then their manuscripts with abstracts
    overview.tex                catalogue of families by discipline (overview.pdf is built from it)
    history.md                  release history
    preprints/<slug>/           README.md (title, author, date, BibTeX) and build/source/paper.tex
    exact/verification.yaml     every manuscript, its data file, its claim and the command that checks it
    catalogue.json              the selection, one row per manuscript

Selection: every accepted cell with N <= 100 and every accepted plane result
(the 679 least arguable ones), then the 40 accepted cells with N = 101..120
that beat their trivial bound by the widest margin. The other accepted cells
stay listed in grassmann/RESULTS.md but are not in the collection.

    python catalogue.py
"""
import datetime
import glob
import json
import os
import re
import shutil
from decimal import Decimal, ROUND_FLOOR
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "grassmann")
P2 = os.path.join(HERE, "friedman-maxmin2d")
REPO = "https://github.com/Ge-limin/math"
AUTHOR = "Limin Ge"
TARGET = 722            # manuscripts released, as in OpenAI's first README (October 6, 2026)

# Withdrawn after release, as OpenAI withdrew three manuscripts on October 7.
# The manuscripts stay in preprints/ with a notice; they leave the catalogue.
WITHDRAWN_ON = "October 9, 2026"
WITHDRAWN = {
    "m10n4N5": (
        "The manuscript states 2.999999 for five four-dimensional subspaces of R^10. The Rankin simplex bound for this "
        "cell is exactly 3, and the configuration falls short of it by 0.000000005, which is the precision of the search, "
        "not a property of the problem. The optimum for this cell is very likely exactly 3. A manuscript about this "
        "cell should prove that with an exact configuration; this one gives a number slightly below it.\n\n"
        "**This withdrawal concerns the statement; it does not assert that the configuration is wrong.**"),
    "m12n4N98": (
        "The manuscript beats the trivial bound for its cell by 0.0000106, the smallest margin in the collection. It "
        "was obtained by deleting one subspace from this collection's own packing for N = 99 and polishing the rest, "
        "so it improves on this collection rather than on anything published. The same holds for the manuscript for "
        "N = 96, withdrawn with it.\n\n"
        "**This withdrawal concerns significance; it does not assert that the configuration is wrong.**"),
    "m12n4N96": (
        "The manuscript beats the trivial bound for its cell by 0.0000117, the second smallest margin in the "
        "collection. It was obtained by deleting one subspace from this collection's own packing for N = 97 and "
        "polishing the rest, so it improves on this collection rather than on anything published. The same holds for "
        "the manuscript for N = 98, withdrawn with it.\n\n"
        "**This withdrawal concerns significance; it does not assert that the configuration is wrong.**"),
}

NOUN = {1: ("line", "lines"), 2: ("plane", "planes"), 3: ("three-space", "three-spaces"), 4: ("four-space", "four-spaces")}
DISCIPLINES = ["Real projective geometry", "Coding theory", "Discrete geometry"]


def discipline(fam):
    if fam["kind"] == "plane":
        return "Discrete geometry"
    return "Real projective geometry" if fam["n"] == 1 else "Coding theory"


def trunc(fr, places):
    v = (Decimal(fr.numerator) / Decimal(fr.denominator)).quantize(Decimal(10) ** -places, rounding=ROUND_FLOOR)
    return f"{v}"


def date_of(path):
    d = datetime.date.fromtimestamp(os.path.getmtime(path))
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y"), d.strftime("%B-") + str(d.day) + d.strftime("-%Y")


def seconds_of(log):
    if not os.path.exists(log):
        return None
    m = re.findall(r" (\d+)s\s*$", open(log).read(), re.M)
    return int(m[-1]) if m else None


def select():
    g = json.load(open(os.path.join(G, "results.json")))
    p = json.load(open(os.path.join(P2, "results2d.json")))
    acc = [r for r in g if r["accepted"]]
    core = [r for r in acc if r["band"] == "N<=100"]
    ext = sorted([r for r in acc if r["band"] == "N=101..120"], key=lambda r: -r["margin_over_trivial"])
    plane = [r for r in p if r["accepted"]]
    take = TARGET - len(core) - len(plane)
    assert 0 <= take <= len(ext), take
    return core + ext[:take], plane, len(acc) + len(plane)


def trivial_source(r, known, sloane, ours):
    """Which configuration gives the trivial bound: (description, N')."""
    m, n, N, t = r["m"], r["n"], r["N"], r["trivial_bound"]
    if t == 0:
        return None
    for NN, v in sorted(known.get((m, n), {}).items()):
        if NN > N and abs(v - t) < 1e-9:
            src = "listed in Sloane's 1997 table" if NN in sloane.get((m, n), {}) else "listed in Cohn's current table"
            return src, NN
    for (mm, nn, NN), v in sorted(ours.items()):
        if (mm, nn) == (m, n) and NN > N and abs(v - t) < 1e-9:
            return "found by this search", NN
    return "a larger configuration", None


def tex_escape(s):
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")


PAPER_TEX = r"""\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,margin=22mm]{geometry}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{fancyvrb,multicol}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue]{hyperref}
\newtheorem*{theorem}{Theorem}
\title{%(title)s}
\author{%(author)s\thanks{Found and checked by Claude, a model released by Anthropic, running on the author's laptop. The author sent the prompts.}}
\date{%(date)s}
\begin{document}
\maketitle
\begin{abstract}
%(abstract)s
\end{abstract}

\section{Result}
%(theorem)s

\section{Context}
%(context)s

\section{Verification}
%(verification)s

\section{How it was found}
%(method)s

\appendix
\section{Exact value}
{\small
\begin{verbatim}
%(exact_lines)s
\end{verbatim}}

\section{Coordinates}
%(coords_intro)s
{\tiny
\begin{multicols}{%(cols)d}
\VerbatimInput{%(datafile)s}
\end{multicols}}
\end{document}
"""


def grass_manuscript(r, ctx):
    m, n, N = r["m"], r["n"], r["N"]
    cell = "m%dn%dN%d" % (m, n, N)
    D = Fraction(*map(int, r["D_exact"].split("/")))
    one, many = NOUN[n]
    title = f"A Packing of {N} {many.title()} in R{m}"
    title_tex = f"A Packing of {N} {many.title()} in $\\mathbb{{R}}^{{{m}}}$"
    date, date_slug = date_of(os.path.join(G, "results", cell + ".npy"))
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-") + "-" + date_slug
    src = trivial_source(r, ctx["known"], ctx["sloane"], ctx["ours"])
    d6 = trunc(D, 6)
    if src and src[1]:
        triv = (f"The best value implied by known packings is {r['trivial_bound']:.6f}, obtained by deleting "
                f"{src[1] - N} of the {src[1]} {many} of the packing {src[0]}.")
    else:
        triv = "No packing with more " + many + " in this row gives a value to compare with."
    abstract = (f"We give {N} {n}-dimensional subspaces of R^{m} whose smallest squared chordal distance is "
                f"at least {d6}. This cell of the table of best Grassmannian packings has no published value. "
                f"{triv} The value is checked with exact rational arithmetic from integer coordinates. "
                f"We do not claim it is optimal.")
    abstract_tex = abstract.replace(f"R^{m}", f"$\\mathbb{{R}}^{{{m}}}$")
    theorem = (f"\\begin{{theorem}}\nThere are {N} subspaces of dimension {n} in $\\mathbb{{R}}^{{{m}}}$ whose pairwise squared "
               f"chordal distances $D(a,b) = {n} - \\operatorname{{tr}}(P_aP_b)$ are all at least\n"
               f"\\[ D_{{\\min}} = {d6}\\ldots \\]\n\\end{{theorem}}\nThe exact value of $D_{{\\min}}$, a rational number, is given in Appendix~A.\n")
    context = (f"N.~J.~A.~Sloane's \\emph{{Table of Best Grassmannian Packings}} (last modified 1997), now maintained by "
               f"Henry Cohn, lists values for some $N$ in the row $m={m}$, $n={n}$. The cell $N={N}$ is blank in Sloane's table, "
               f"in Sloane's coordinate files and in Cohn's table as checked on October 8, 2026. "
               f"{tex_escape(triv)} The Rankin simplex bound for this cell is "
               f"${n}({m}-{n})/{m}\\cdot {N}/{N - 1} = {r['rankin_bound']:.6f}$, and the value above lies below it.\n")
    verification = ("Each subspace is given by an integer $m\\times n$ basis $Y$ (coordinates times $10^{12}$, rounded). "
                    "With $G=Y^\\top Y$ the projection is $P=YG^{-1}Y^\\top$, so for two subspaces\n"
                    "\\[ \\operatorname{tr}(P_aP_b)=\\frac{\\operatorname{tr}(\\operatorname{adj}(G_a)\\,A\\,\\operatorname{adj}(G_b)\\,A^\\top)}{\\det G_a\\det G_b},\\qquad A=Y_a^\\top Y_b, \\]\n"
                    "an exact rational number. No orthonormality is assumed and no floating point is used. Run\n"
                    f"\\begin{{verbatim}}\npython grassmann/verify.py grassmann/packings/{cell}.txt\n\\end{{verbatim}}\n"
                    f"in \\url{{{REPO}}}.\n")
    secs = seconds_of(os.path.join(G, "results", cell + ".log"))
    method = ("Many random starts of gradient descent on the Grassmannian against a log-sum-exp of the pairwise overlaps, "
              "sharpened over time, then a polishing stage (\\texttt{grassmann/solve.py})"
              + (f"; about {secs} seconds on one laptop, with about ten such searches running at once." if secs else ".") + "\n")
    data = os.path.join(G, "packings", cell + ".txt")
    return {
        "kind": "grassmann", "family": (m, n), "m": m, "n": n, "N": N, "cell": cell, "slug": slug,
        "title": title, "title_tex": title_tex, "date": date, "abstract": abstract, "abstract_tex": abstract_tex,
        "claim": f"D_min >= {d6}", "exact": r["D_exact"], "data": os.path.relpath(data, HERE),
        "check": f"python grassmann/verify.py grassmann/packings/{cell}.txt", "seconds": secs, "band": r["band"],
        "tex": dict(theorem=theorem, context=context, verification=verification, method=method,
                    coords_intro=f"{N} blocks of {m} rows with {n} integers each; divide by $10^{{12}}$. "
                                 f"File: \\texttt{{grassmann/packings/{cell}.txt}}.",
                    cols=4 if n <= 2 else 3, datafile=data),
    }


def plane_manuscript(r):
    n = r["n"]
    R = Fraction(*map(int, r["r2_exact"].split("/")))
    title = f"Spreading {n} Points in the Plane"
    date, date_slug = date_of(os.path.join(P2, "bests", f"n{n}.npy"))
    slug = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-") + "-" + date_slug
    r5 = trunc(R, 5)
    if r["r2_next"]:
        triv = (f"Deleting a point from our {n + 1}-point configuration gives {r['r2_next']:.5f}; this one is smaller.")
    else:
        triv = "There is no larger configuration in the table to compare with."
    abstract = (f"We place {n} points in the plane so that the squared ratio of the largest to the smallest distance "
                f"between them is at most {r5}+. Erich Friedman's table of best known configurations lists n up to 31. "
                f"{triv} The ratio is computed exactly from the published coordinates. We do not claim it is optimal.")
    theorem = (f"\\begin{{theorem}}\nThere are {n} points in the plane with\n"
               f"\\[ \\Bigl(\\frac{{\\max d}}{{\\min d}}\\Bigr)^2 = {r5}\\ldots \\]\n\\end{{theorem}}\nThe exact value, a rational number, is given in Appendix~A.\n")
    context = ("Erich Friedman's page \\emph{Minimizing the Ratio of Maximum to Minimum Distance} lists the best known "
               f"configurations for $n\\le 31$. The value for $n={n}$ is not on the page. {tex_escape(triv)}\n")
    verification = ("The coordinates are decimals with 12 digits after the point, so they are exact rationals; "
                    "all squared distances, and their largest-to-smallest ratio, are computed with integers. Run\n"
                    f"\\begin{{verbatim}}\npython friedman-maxmin2d/verify.py friedman-maxmin2d/coords/n{n}.txt\n\\end{{verbatim}}\n"
                    f"in \\url{{{REPO}}}.\n")
    method = ("Random starts of a constrained local optimizer (SLSQP), then basin hopping seeded from the neighbouring sizes "
              "(\\texttt{friedman-maxmin2d/}).\n")
    data = os.path.join(P2, "coords", f"n{n}.txt")
    return {
        "kind": "plane", "family": ("plane",), "n": n, "N": n, "cell": f"plane-n{n}", "slug": slug,
        "title": title, "title_tex": title, "date": date, "abstract": abstract, "abstract_tex": abstract,
        "claim": f"r^2 <= {r['r2']}", "exact": r["r2_exact"], "data": os.path.relpath(data, HERE),
        "check": f"python friedman-maxmin2d/verify.py friedman-maxmin2d/coords/n{n}.txt", "seconds": None, "band": "plane",
        "tex": dict(theorem=theorem, context=context, verification=verification, method=method,
                    coords_intro=f"{n} points, $x$ and $y$ per line. File: \\texttt{{friedman-maxmin2d/coords/n{n}.txt}}.",
                    cols=2, datafile=data),
    }


def families(ms):
    fams = {}
    for x in ms:
        fams.setdefault(x["family"], []).append(x)
    out = []
    for key, items in fams.items():
        items.sort(key=lambda x: x["N"])
        Ns = [x["N"] for x in items]
        if key == ("plane",):
            f = {"kind": "plane", "title": "Spreading points in the plane",
                 "summary": f"First values for n = {Ns[0]}–{Ns[-1]} ({len(Ns)} cells) in Erich Friedman's table of point sets "
                            "in the plane minimizing the ratio of the largest to the smallest distance, which stops at n = 31. "
                            "Each value is smaller than what deleting a point from the next configuration gives."}
        else:
            m, n = key
            f = {"kind": "grassmann", "m": m, "n": n, "title": f"Packings of {NOUN[n][1]} in R{m}",
                 "summary": f"First values for {len(Ns)} blank cells (N = {span(Ns)}) in the row m = {m}, n = {n} of the table of "
                            "best Grassmannian packings, blank in Sloane's 1997 table and in Cohn's current one. "
                            "Each value beats every packing obtained by deleting subspaces from a larger known one."}
        f["items"] = items
        out.append(f)
    order = {d: i for i, d in enumerate(DISCIPLINES)}
    out.sort(key=lambda f: (order[discipline(f)], f.get("n", 0), f.get("m", 0)))
    for i, f in enumerate(out, 1):
        f["no"] = "%03d" % i
        f["discipline"] = discipline(f)
    return out


def span(Ns):
    runs, start = [], Ns[0]
    for a, b in zip(Ns, Ns[1:] + [None]):
        if b != a + 1:
            runs.append(f"{start}" if start == a else f"{start}–{a}")
            start = b
    return ", ".join(runs)


def write_preprint(x):
    d = os.path.join(HERE, "preprints", x["slug"])
    os.makedirs(os.path.join(d, "build", "source"), exist_ok=True)
    with open(os.path.join(d, "build", "source", "coordinates.txt"), "w") as f:      # numbers only; the text says what they are
        f.writelines(l for l in open(os.path.join(HERE, x["data"])) if not l.startswith("#"))
    num, den = x["exact"].split("/")
    wrap = lambda z: "\n".join(z[i:i + 72] for i in range(0, len(z), 72))
    t = dict(x["tex"], datafile="coordinates.txt", exact_lines="numerator:\n" + wrap(num) + "\ndenominator:\n" + wrap(den), title=x["title_tex"], author=AUTHOR, date=x["date"],
             abstract=x["abstract_tex"])
    open(os.path.join(d, "build", "source", "paper.tex"), "w").write(PAPER_TEX % t)
    url = f"{REPO}/blob/main/preprints/{x['slug']}/paper.pdf"
    notice = ""
    if x["cell"] in WITHDRAWN:
        notice = (f"**Withdrawn on {WITHDRAWN_ON}.**\n\n{WITHDRAWN[x['cell']]} "
                  "The manuscript and its data remain below; the result is no longer in the catalogue.\n\n")
    open(os.path.join(d, "README.md"), "w").write(
        f"# [{x['title']}](paper.pdf)\n\n{AUTHOR}  \n{x['date']}\n\n{notice}"
        f"## Check it\n\n```\n{x['check']}\n```\n\nData: [`{x['data']}`](../../{x['data']}). Exact value: `{x['exact']}`.\n\n"
        "## Citation\n\n```bibtex\n"
        f"@misc{{LG:{x['slug']},\n  author = {{{{{AUTHOR}}}}},\n  title = {{{{{x['title_tex']}}}}},\n"
        f"  howpublished = {{Limin Ge Math Release preprint\n                  \\href{{{url}}}{{LG:{x['slug']}}}}},\n  year = {{2026}}\n}}\n```\n")


def write_contents(fams):
    out = [f"# Mathematics manuscript collection\n\n**{sum(len(f['items']) for f in fams)} manuscripts covering {len(fams)} result families.**\n\n"
           "[**Read the overview PDF**](overview.pdf).\n\n## Manuscript map\n\n"
           "Each result description is followed by its constituent manuscripts and their abstracts. Paper titles link directly to PDFs.\n\n"
           "<table>\n<thead><tr><th>Result</th></tr></thead>\n"]
    for f in fams:
        out.append(f"<tbody><tr>\n<td>\n\n**{f['no']}. {f['title']}.** {f['summary']}\n\n</td>\n</tr></tbody>\n")
        for x in f["items"]:
            out.append(f"<tbody><tr>\n<td>\n\n&emsp;[{x['title']}](preprints/{x['slug']}/paper.pdf)\n\n{x['abstract']}\n\n</td>\n</tr></tbody>\n")
    out.append("</table>\n")
    open(os.path.join(HERE, "CONTENTS.md"), "w").write("".join(out))


OVERVIEW_HEAD = r"""\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,left=21mm,right=21mm,top=20mm,bottom=20mm,headheight=12pt,headsep=6mm,footskip=9mm]{geometry}
\usepackage{fontspec}
\setmainfont{texgyrepagella-regular.otf}[BoldFont=texgyrepagella-bold.otf,ItalicFont=texgyrepagella-italic.otf,BoldItalicFont=texgyrepagella-bolditalic.otf]
\usepackage{amsmath}
\usepackage{unicode-math}
\setmathfont{texgyrepagella-math.otf}
\usepackage[protrusion=true,expansion=false]{microtype}
\usepackage{fancyhdr,lastpage,xcolor,ragged2e,needspace}
\definecolor{muted}{gray}{0.38}
\definecolor{linkink}{HTML}{275B59}
\usepackage[unicode,colorlinks=true,linkcolor=linkink,urlcolor=linkink,pdfauthor={%(author)s},pdftitle={%(author)s Research Catalog},pdfsubject={%(fams)d result families in %(target)d manuscripts}]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{1.2em}
\widowpenalty=10000
\clubpenalty=10000
\raggedbottom
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize\scshape %(author)s Research Catalog}
\fancyhead[R]{\footnotesize\scshape %(author)s}
\fancyfoot[L]{\footnotesize\color{muted}%(fams)d result families\enspace\textperiodcentered\enspace%(target)d manuscripts}
\fancyfoot[R]{\footnotesize\thepage\, /\,\pageref*{LastPage}}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}
\fancypagestyle{firstpage}{\fancyhead{}\renewcommand{\headrulewidth}{0pt}}
\newcommand{\cataloguesection}[2]{%%
  \par\Needspace{10\baselineskip}\addvspace{12pt}%%
  \hypertarget{subject#2}{}\label{subject#2}%%
  \pdfbookmark[0]{#1}{section#2}%%
  {\fontsize{15}{18}\selectfont\bfseries #1\par}%%
  \nobreak\vspace{9pt}\nobreak
}
\newcommand{\resultentry}[4]{%%
  \par\noindent\begin{minipage}{\linewidth}%%
  \fontsize{10.5}{12.6}\selectfont\RaggedRight%%
  \hypertarget{result#1}{}%%
  {\bfseries\textcolor{muted}{#1.}\enspace #2.}\enspace #3\par%%
  \vspace{1.2pt}{\fontsize{8}{9.5}\selectfont\color{muted}#4\par}%%
  \end{minipage}\par\vspace{5pt}%%
}
\begin{document}
\thispagestyle{firstpage}
{\small\scshape Mathematics\hfill %(author)s\par}
\vspace{5pt}
{\LARGE\bfseries %(author)s Research Catalog\par}
\vspace{4pt}
{\small %(fams)d result families in %(target)d manuscripts\hfill %(date)s\par}
\vspace{7pt}
{\small An overview of the \href{%(repo)s}{manuscript collection}. Results are grouped by subject; entry numbers follow the catalog order and do not indicate a ranking. PDF links follow each summary.\par}
\vspace{8pt}\hrule height 0.35pt\vspace{5pt}

{\large\bfseries Contents\par}
\vspace{7pt}
"""


def write_overview(fams, release_date):
    out = [OVERVIEW_HEAD % dict(author=AUTHOR, fams=len(fams), target=sum(len(f["items"]) for f in fams), date=release_date, repo=REPO)]
    for i, d in enumerate(DISCIPLINES, 1):
        out.append(f"\\noindent\\hyperlink{{subject{i}}}{{{d}}}\\nobreak\\hfill\\pageref*{{subject{i}}}\\par\\vspace{{5pt}}\n")
    out.append("\n\\clearpage\n\n")
    for i, d in enumerate(DISCIPLINES, 1):
        out.append(f"\\cataloguesection{{{d}}}{{{i}}}\n\n")
        for f in fams:
            if f["discipline"] != d:
                continue
            links = "\\enspace\\textperiodcentered\\enspace\\allowbreak ".join(
                f"\\href{{{REPO}/blob/main/preprints/{x['slug']}/paper.pdf}}{{{'n' if x['kind'] == 'plane' else 'N'}\\,=\\,{x['N']}}}"
                for x in f["items"])
            title = f["title"].replace(f"R{f.get('m')}", f"$\\mathbb{{R}}^{{{f.get('m')}}}$") if f["kind"] == "grassmann" else f["title"]
            out.append(f"\\resultentry{{{f['no']}}}{{{title}}}{{{tex_escape(f['summary'])}}}{{{links}}}\n\n")
    out.append("\\end{document}\n")
    open(os.path.join(HERE, "overview.tex"), "w").write("".join(out))


def write_verification(ms):
    out = ["# Catalog of manuscripts with an exactly verified main result. Paths are relative to the repository root.\n",
           'version: "v0.1"\n\nproject:\n  name: "Limin Ge math repository"\n'
           '  description: "Exact verifications accompanying a mathematics manuscript collection."\n'
           f'  authors: ["{AUTHOR}"]\n  license: "MIT"\n\n'
           f"summary:\n  manuscripts: {len(ms)}\n  verified: {len(ms)}\n  share: \"100%\"\n\nsources:\n"]
    for x in ms:
        out.append(f'  - title: "{x["title"]}"\n    authors: ["{AUTHOR}"]\n    id: preprints/{x["slug"]}/paper.pdf\n'
                   f'    type: article\n    data: {x["data"]}\n    claim: "{x["claim"]}"\n    exact: "{x["exact"]}"\n'
                   f'    check: "{x["check"]}"\n\n')
    os.makedirs(os.path.join(HERE, "exact"), exist_ok=True)
    open(os.path.join(HERE, "exact", "verification.yaml"), "w").write("".join(out))


def main():
    grass, plane, accepted_total = select()
    known = {tuple(map(int, k.split(","))): {int(N): v for N, v in d.items()}
             for k, d in json.load(open(os.path.join(G, "known-table.json"))).items()}
    sloane = {tuple(map(int, k.split(","))): {int(N): v for N, v in d.items()}
              for k, d in json.load(open(os.path.join(G, "sloane-table.json"))).items()}
    ours = {(r["m"], r["n"], r["N"]): float(Fraction(*map(int, r["D_exact"].split("/"))))
            for r in json.load(open(os.path.join(G, "results.json")))}
    ctx = dict(known=known, sloane=sloane, ours=ours)
    ms = [grass_manuscript(r, ctx) for r in grass] + [plane_manuscript(r) for r in plane]
    assert len(ms) == TARGET and len({x["slug"] for x in ms}) == TARGET
    assert set(WITHDRAWN) <= {x["cell"] for x in ms}
    slugs = {x["slug"] for x in ms}
    for old in os.listdir(os.path.join(HERE, "preprints")) if os.path.isdir(os.path.join(HERE, "preprints")) else []:
        if old not in slugs:
            shutil.rmtree(os.path.join(HERE, "preprints", old))
    for x in ms:
        write_preprint(x)
    fams = families([x for x in ms if x["cell"] not in WITHDRAWN])
    write_contents(fams)
    write_overview(fams, "October 9, 2026")
    write_verification([x for f in fams for x in f["items"]])
    secs = [x["seconds"] for x in ms if x["seconds"]]
    stats = {"released": len(ms), "withdrawn": len(WITHDRAWN), "catalogued": sum(len(f["items"]) for f in fams), "families": len(fams), "accepted_total": accepted_total,
             "by_discipline": {d: sum(len(f["items"]) for f in fams if f["discipline"] == d) for d in DISCIPLINES},
             "families_by_discipline": {d: sum(f["discipline"] == d for f in fams) for d in DISCIPLINES},
             "grassmann_seconds_mean": sum(secs) / len(secs), "grassmann_seconds_total": sum(secs), "with_seconds": len(secs)}
    json.dump({"stats": stats, "manuscripts": [dict({k: v for k, v in x.items() if k != "tex"}, withdrawn=x["cell"] in WITHDRAWN) for x in ms],
               "families": [{"no": f["no"], "title": f["title"], "discipline": f["discipline"],
                             "manuscripts": [x["slug"] for x in f["items"]]} for f in fams]},
              open(os.path.join(HERE, "catalogue.json"), "w"), indent=1, default=list)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
