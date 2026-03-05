"""
KubeSingle65 — MCP Strengths & Weaknesses Chart Generator
Produces docs/charts/mcp_strengths_cons.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    "claude-direct": "#4B9CD3",   # blue
    "grok-direct":   "#F4A300",   # amber
    "claude-mcp":    "#2ECC71",   # green  ← OUR MCP
    "grok-mcp":      "#E74C3C",   # red
}
MCP_EDGE  = "#1A8A4A"   # darker green border to highlight
HIGHLIGHT  = "#2ECC71"
GREY       = "#AAAAAA"
BG         = "#F9F9FB"
DARK       = "#1C1C1E"

MODELS = ["claude-direct", "grok-direct", "claude-mcp", "grok-mcp"]
LABELS = ["Claude\nDirect", "Grok\nDirect", "Claude\nMCP ★", "Grok\nMCP"]
COLORS = [C[m] for m in MODELS]
EDGES  = [MCP_EDGE if m == "claude-mcp" else "#888" for m in MODELS]
LW     = [2.5 if m == "claude-mcp" else 0.8 for m in MODELS]

# ── Data ─────────────────────────────────────────────────────────────────────

# 1. Average % Score across penalty regimes
scores = {
    "−5 pen":  [63.6, 56.1, 50.8, 38.4],
    "−2 pen":  [74.1, 61.3, 57.7, 47.1],
    "no-pen":  [81.1, 64.8, 62.3, 52.9],
}

# 2. Hallucination rate (%) and total hallucinations
hall_rate  = [37.1, 14.3, 15.4, 37.9]
hall_total = [13,   4,    6,    11  ]

# 3. Average response time (seconds) — from Table 5.1
avg_time = [116, 81, 79, 82]

# 4. Files found / missed / hallucinated — from Section 9.2
files_found  = [28, 22, 22, 17]
files_missed = [ 4,  4, 10, 13]
files_hall   = [13,  4,  6, 11]

# 5. Per-question −5pen% for claude-mcp
tc_labels = [f"TC{i:03d}" for i in range(1, 11)]
mcp_per_q = [100, 68, 28, 30, 66.7, 100, 65, 100, 0, -50]
dir_per_q = [100, 30, 28, 68.3, 70, 100, 40, 100, 90, 10]

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 14), facecolor=BG)
fig.suptitle(
    "KubeSingle65 — claude-mcp  Strengths & Weaknesses",
    fontsize=18, fontweight="bold", color=DARK, y=0.98,
)

gs = fig.add_gridspec(
    3, 3,
    left=0.06, right=0.97,
    top=0.93,  bottom=0.06,
    hspace=0.55, wspace=0.38,
)

ax1 = fig.add_subplot(gs[0, :2])   # top-left wide: scores
ax2 = fig.add_subplot(gs[0, 2])    # top-right: hallucination rate
ax3 = fig.add_subplot(gs[1, 0])    # mid-left: avg time
ax4 = fig.add_subplot(gs[1, 1:])   # mid-right wide: stacked files
ax6 = fig.add_subplot(gs[2, :])    # bottom wide: per-question


def style_ax(ax, title, ylabel=None):
    ax.set_facecolor(BG)
    ax.set_title(title, fontsize=11, fontweight="bold", color=DARK, pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color=DARK)
    ax.tick_params(colors=DARK, labelsize=8)
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#CCCCCC")
    ax.grid(axis="y", color="#E0E0E0", linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)


# ── Panel 1: Grouped bar — three penalty regimes ──────────────────────────────
regimes = list(scores.keys())
n, k = len(MODELS), len(regimes)
x = np.arange(n)
w = 0.26

for i, (regime, marker) in enumerate(zip(regimes, ["///", "", "xxx"])):
    bars = ax1.bar(
        x + (i - 1) * w,
        scores[regime],
        width=w,
        label=regime,
        color=[(*plt.cm.colors, 0.82)[0] if False else c for c in COLORS],
        edgecolor=EDGES,
        linewidth=LW,
        hatch=marker if regime != "−2 pen" else "",
        alpha=0.88,
    )

# Re-draw with proper colors (matplotlib hatch + alpha)
ax1.cla()
for i, regime in enumerate(regimes):
    offset = (i - 1) * w
    for j, (score, col, ec, lw_) in enumerate(
        zip(scores[regime], COLORS, EDGES, LW)
    ):
        hatch = {"−5 pen": "///", "−2 pen": "", "no-pen": "xxx"}[regime]
        ax1.bar(
            x[j] + offset, score,
            width=w, color=col, edgecolor=ec, linewidth=lw_,
            hatch=hatch, alpha=0.85,
            label=regime if j == 0 else "",
        )

ax1.set_xticks(x)
ax1.set_xticklabels(LABELS, fontsize=9)
ax1.set_ylim(0, 100)
style_ax(ax1, "Average Score by Penalty Regime  (per-question mean %)", "Score %")
ax1.legend(
    loc="upper right", fontsize=9,
    handles=[
        mpatches.Patch(facecolor="#ccc", hatch="///", label="−5 pen (full)"),
        mpatches.Patch(facecolor="#ccc", label="−2 pen (moderate)"),
        mpatches.Patch(facecolor="#ccc", hatch="xxx", label="no-pen (recall only)"),
    ],
)
# Annotate −5pen scores
for j, v in enumerate(scores["−5 pen"]):
    ax1.text(x[j] - w, v + 1.5, f"{v:.0f}%", ha="center", fontsize=8,
             fontweight="bold" if MODELS[j]=="claude-mcp" else "normal",
             color=MCP_EDGE if MODELS[j]=="claude-mcp" else DARK)

ax1.axhline(50, color="#999", linewidth=0.8, linestyle=":")


# ── Panel 2: Hallucination rate ────────────────────────────────────────────────
bars2 = ax2.bar(LABELS, hall_rate, color=COLORS, edgecolor=EDGES, linewidth=LW,
                alpha=0.88)
for bar, rate, total in zip(bars2, hall_rate, hall_total):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
             f"{rate:.1f}%\n({total})", ha="center", va="bottom", fontsize=8,
             fontweight="bold" if COLORS[bars2.index(bar)] == HIGHLIGHT else "normal",
             color=MCP_EDGE if COLORS[list(bars2).index(bar)] == HIGHLIGHT else DARK)
style_ax(ax2, "Hallucination Rate\n(hall / found+hall)", "Rate %")
ax2.set_ylim(0, 50)

# Annotate strength arrow
ax2.annotate("LOW ✓\n(strength)", xy=(2, hall_rate[2]),
             xytext=(2.3, hall_rate[2] + 14),
             fontsize=7.5, color=MCP_EDGE, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=MCP_EDGE, lw=1.2))


# ── Panel 3: Average response time ────────────────────────────────────────────
bars3 = ax3.bar(LABELS, avg_time, color=COLORS, edgecolor=EDGES, linewidth=LW,
                alpha=0.88)
for bar, t in zip(bars3, avg_time):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             f"{t}s", ha="center", va="bottom", fontsize=8.5)
style_ax(ax3, "Avg Response Time\nper Question (s)", "Seconds")
ax3.set_ylim(0, 155)
ax3.annotate("FASTEST ✓\n(strength)", xy=(2, avg_time[2]),
             xytext=(2.4, avg_time[2] + 30),
             fontsize=7.5, color=MCP_EDGE, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=MCP_EDGE, lw=1.2))


# ── Panel 4: Stacked bar — found / missed / hall ──────────────────────────────
x4 = np.arange(len(LABELS))
w4 = 0.55
b1 = ax4.bar(x4, files_found,  width=w4, label="Found",        color="#2ECC71", alpha=0.85, edgecolor=EDGES, linewidth=LW)
b2 = ax4.bar(x4, files_missed, width=w4, bottom=files_found,   label="Missed",  color="#E74C3C", alpha=0.75, edgecolor=EDGES, linewidth=LW)
b3 = ax4.bar(x4, files_hall,   width=w4,
             bottom=[f+m for f,m in zip(files_found, files_missed)],
             label="Hallucinated", color="#F39C12", alpha=0.75, edgecolor=EDGES, linewidth=LW)
ax4.set_xticks(x4)
ax4.set_xticklabels(LABELS, fontsize=8.5)
style_ax(ax4, "File Detection Profile\n(Found / Missed / Hallucinated)", "# Files")
ax4.legend(loc="upper right", fontsize=7.5)

# Annotate claude-mcp's missed count
ax4.annotate("10 missed\n(weakness)", xy=(2, files_found[2] + files_missed[2]/2),
             xytext=(2.55, 28),
             fontsize=7.5, color="#C0392B", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.2))


# ── Panel 6: Per-question −5pen% comparison ───────────────────────────────────
x6 = np.arange(len(tc_labels))
w6 = 0.35
ax6.bar(x6 - w6/2, dir_per_q, width=w6, label="claude-direct",
        color=C["claude-direct"], alpha=0.80, edgecolor="#3070A0", linewidth=0.8)
ax6.bar(x6 + w6/2, mcp_per_q, width=w6, label="claude-mcp ★",
        color=C["claude-mcp"],    alpha=0.88, edgecolor=MCP_EDGE, linewidth=1.8)

ax6.axhline(0, color=DARK, linewidth=0.8, linestyle="-")
ax6.set_xticks(x6)
ax6.set_xticklabels(tc_labels, fontsize=9)
ax6.set_ylim(-70, 115)
style_ax(ax6, "Per-Question −5pen%:  claude-direct  vs  claude-mcp ★", "Score %")
ax6.legend(loc="lower right", fontsize=9)

# Annotate key wins and losses for claude-mcp
annotations = {
    "TC007": ("claude-mcp\nbest win\n+25pp", 0, 65,  20,  85),
    "TC001": ("Both 100%\n(no-op ✓)", 0, 100, -0.3, 108),
    "TC004": ("MCP worst:\n2/6 files", 3, 30,  3.6, -55),
    "TC009": ("MCP 0%\nvs 90%", 8, 0,   8,  -55),
    "TC010": ("MCP −50%\n(hall+miss)", 9, -50, 8.5, -65),
}
for label, (xi_off, y_pt, x_txt, y_txt) in [
    ("TC007 win",  (0,  65,  0.3,  90)),
    ("TC004 loss", (3,  30,  3.6, -55)),
    ("TC009 loss", (8,   0,  8.3, -55)),
    ("TC010 loss", (9, -50,  8.8, -65)),
]:
    xi, y_pt, x_txt, y_txt = (
        {"TC007 win":  (6+0.5*w6,  65,  6.2,  95),
         "TC004 loss": (3+0.5*w6,  30,  3.8, -58),
         "TC009 loss": (8+0.5*w6,   0,  8.3, -52),
         "TC010 loss": (9+0.5*w6, -50,  8.6, -65),
        }[label]
    )
    color = MCP_EDGE if "win" in label else "#C0392B"
    btext = "★ MCP win\n+25pp" if "win" in label else (
        "MCP miss:\n2/6 files" if "TC004" in label else
        "MCP 0%\nvs 90%" if "TC009" in label else
        "MCP −50%\n(miss+hall)"
    )
    ax6.annotate(btext, xy=(xi, y_pt), xytext=(x_txt, y_txt),
                 fontsize=7, color=color, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=color, lw=1.0),
                 ha="center")

# ── Strength/Weakness legend strip ───────────────────────────────────────────
fig.text(0.06, 0.015,
    "★ STRENGTHS of claude-mcp:  Fastest avg time (79s) ·  Low hallucination rate (15.4%, 6 total)  ·  Reliable on no-op Qs (TC001, TC008)  ·  Best per-file quality on TC007",
    fontsize=8.5, color=MCP_EDGE, fontweight="bold", ha="left")
fig.text(0.06, 0.003,
    "✗ WEAKNESSES of claude-mcp:  10 missed files (vs 4 for direct)  ·  TC004 only 2/6 files  ·  TC009 & TC010 both scored 0% or worse",
    fontsize=8.5, color="#C0392B", fontweight="bold", ha="left")

# ── Save ─────────────────────────────────────────────────────────────────────
OUT = "/Users/deadbytes/Documents/ByteBell/public_evaluations/docs/charts/mcp_strengths_cons.png"
plt.savefig(OUT, dpi=160, bbox_inches="tight", facecolor=BG)
print(f"Saved → {OUT}")
