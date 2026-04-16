#!/usr/bin/env python3
"""Generate metrics_table.tex: 9 runs x 10 tasks, total cost + time only."""
import json, os

BASE = "results_on_swe_pro"
RUNS = [
    ("mcp_r1",    "auto_run_on_swe_pro_mcp_claude-sonnet-4-6"),
    ("mcp_r2",    "auto_run_on_swe_pro_mcp_claude-sonnet-4-6_run_2"),
    ("mcp_r3",    "auto_run_on_swe_pro_mcp_claude-sonnet-4-6_run_3"),
    ("skills_r1", "auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6"),
    ("skills_r2", "auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_2"),
    ("skills_r3", "auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_3"),
    ("raw_r1",    "auto_run_on_swe_pro_raw_claude-sonnet-4-6_run_1"),
    ("raw_r2",    "auto_run_on_swe_pro_raw_claude-sonnet-4-6_run_2"),
    ("raw_r3",    "auto_run_on_swe_pro_raw_claude-sonnet-4-6_run_3"),
]

# ── Load data ──────────────────────────────────────────────────────────────────
data = {}
task_ids = None
for run_key, folder_name in RUNS:
    folder = os.path.join(BASE, folder_name)
    data[run_key] = {}
    tasks = sorted(d for d in os.listdir(folder)
                   if os.path.isdir(os.path.join(folder, d)))
    if task_ids is None:
        task_ids = tasks
    for task in tasks:
        ap = os.path.join(folder, task, "answer.json")
        with open(ap) as f:
            a = json.load(f)
        data[run_key][task] = {
            "cost": float(a.get("total_cost_usd") or 0),
            "time": float(a.get("time_taken_seconds") or 0),
        }

run_keys = [k for k, _ in RUNS]

# ── Formatters ─────────────────────────────────────────────────────────────────
def fc(v, bold=False):
    s = f"{v:.2f}"
    return "\\textbf{" + s + "}" if bold else s

def ft(v, bold=False):
    s = str(int(round(v)))
    return "\\textbf{" + s + "}" if bold else s

def task_label(t):
    return "\\texttt{" + t.split("-")[1][:6] + "}"

# ── Body rows ──────────────────────────────────────────────────────────────────
body = []
tots = {k: {"cost": 0., "time": 0.} for k in run_keys}

for task in task_ids:
    row = [task_label(task)]
    for rk in run_keys:
        d = data[rk][task]
        row += [fc(d["cost"]), ft(d["time"])]
        tots[rk]["cost"] += d["cost"]
        tots[rk]["time"] += d["time"]
    body.append("  " + " & ".join(row) + " \\\\")

body.append("  \\midrule")
trow = ["\\textbf{Total}"]
for rk in run_keys:
    t = tots[rk]
    trow += [fc(t["cost"], True), ft(t["time"], True)]
body.append("  " + " & ".join(trow) + " \\\\")
body_str = "\n".join(body)

# ── Header builder ─────────────────────────────────────────────────────────────
def right_border(i):
    """Right-border format string for the i-th run pair (0-indexed)."""
    if i in (2, 5): return "c||"   # end of MCP and Skills sections
    if i == 8:      return "c"     # end of table
    return "c|"                    # between runs within a section

def build_header():
    lines = []

    # Row 1 — section colour bands (each section = 3 runs × 2 cols = 6 cols)
    lines.append(
        "  & \\multicolumn{6}{c||}{\\cellcolor{mcp}\\textbf{MCP}}"
        " & \\multicolumn{6}{c||}{\\cellcolor{skills}\\textbf{MCP + Skills}}"
        " & \\multicolumn{6}{c}{\\cellcolor{raw}\\textbf{Raw}} \\\\"
    )

    # Row 2 — run labels (each run = 2 cols)
    crs = "".join(f"\\cmidrule(lr){{{2+2*i}-{3+2*i}}}" for i in range(9))
    lines.append(f"  {crs}")
    rcells = []
    for i in range(9):
        n  = i % 3 + 1
        rb = right_border(i)
        rcells.append(f"\\multicolumn{{2}}{{{rb}}}{{\\textbf{{R{n}}}}}")
    lines.append("  & " + " & ".join(rcells) + " \\\\")

    # Row 3 — metric labels: Cost($) and T(s) per run
    mcells = []
    for i in range(9):
        rb = right_border(i)
        mcells.append("Cost(\\$)")
        mcells.append(f"\\multicolumn{{1}}{{{rb}}}{{T(s)}}")
    lines.append("  \\textbf{Task} & " + " & ".join(mcells) + " \\\\")

    return "\n".join(lines)

H = build_header()

# ── Assemble .tex ──────────────────────────────────────────────────────────────
tex_parts = [
r"""\documentclass[a4paper]{article}
\usepackage[landscape, margin=0.8cm]{geometry}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{colortbl}
\usepackage{array}
\usepackage{longtable}
\usepackage[T1]{fontenc}
\usepackage{lmodern}

\definecolor{mcp}{RGB}{210,228,255}
\definecolor{skills}{RGB}{210,245,220}
\definecolor{raw}{RGB}{255,225,210}

\begin{document}
\small
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.2}

%% 19 columns: Task | MCP(R1 R2 R3) || Skills(R1 R2 R3) || Raw(R1 R2 R3)
%% Each run pair: Cost($)  Time(s)
\begin{longtable}{@{}
  l ||
  rr|rr|rr ||
  rr|rr|rr ||
  rr|rr|rr
@{}}

\toprule""",
H,
r"""\midrule
\endfirsthead

\toprule""",
H,
r"""\midrule
\endhead

\midrule \multicolumn{19}{r}{\textit{continued\ldots}} \\
\endfoot

\bottomrule
\endlastfoot

""",
body_str,
r"""

\end{longtable}
\end{document}
"""]

tex = "\n".join(tex_parts)

out = os.path.join(BASE, "metrics_table.tex")
with open(out, "w") as f:
    f.write(tex)
print(f"Written: {out}")
