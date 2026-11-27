# Pictures of the ngspice DDR3L simulation (si/ddr_sim.py): eye diagrams of the worst data line for writes and reads,
# the longest unterminated address line against the DDR3L overshoot limit, and the CK and DQS pairs with their
# crossings. The DDR3L (JESD79-3-1A) receiver levels are drawn on every plot: they are what a real memory input must
# see, so they are the yardstick for these waveforms. Usage: python3 si/ddr_plots.py -> si/plots/*.png
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ddr_sim import run, delay, length, prbs7, crossings, VDD, VTT, UI, TR
OUT = os.path.dirname(os.path.abspath(__file__)) + "/plots"; os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, AQUA, GREY, INK, INK2 = "#257de0", "#f47230", "#00b894", "#9c9c9c", "#191919", "#666666"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6})
VREF = VDD / 2
LEVELS = [(VREF + 0.135, "VIH(AC135)"), (VREF + 0.090, "VIH(DC90)"), (VREF - 0.090, "VIL(DC90)"), (VREF - 0.135, "VIL(AC135)")]
def levels(ax, x0, x1):
    # DDR3L receiver levels: AC135 must be reached, DC90 must then be held (labels: AC on the right, DC on the left)
    for v, name in LEVELS:
        ac = "AC" in name
        ax.axhline(v, color=ORANGE, lw=1, ls="--" if ac else ":", zorder=1)
        if ac: ax.text(x1, v, " " + name.replace("(AC135)", " AC135 (dotted: DC90)"), color=INK2, va="center", ha="left", fontsize=8, clip_on=False)
    ax.axhline(VREF, color=GREY, lw=0.8, zorder=1); ax.text(x1, VREF, " VREF", color=INK2, va="center", fontsize=8, clip_on=False)
def eye_plot(net, rs, term, rev, title, fname):
    bits = prbs7(127); t, v = run([net], bits, rs, term, 1.5, reverse=rev); v = v[0]; d = delay(net) + TR / 2
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    # fold into 2-UI windows centred on a bit
    for k in range(8, len(bits) - 2):
        t0 = d + (k - 0.5) * UI
        xs = [ti - t0 for ti in t if t0 <= ti <= t0 + 2 * UI]; ys = [vi for ti, vi in zip(t, v) if t0 <= ti <= t0 + 2 * UI]
        ax.plot(xs, ys, color=BLUE, lw=0.7, alpha=0.35)
    levels(ax, 0, 2 * UI)
    ax.set_xlim(0, 2 * UI); ax.set_ylim(-0.1, VDD + 0.1); ax.set_xlabel("time in a 2-bit window (ps)"); ax.set_ylabel("voltage at the receiver ball (V)")
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    fig.tight_layout(); fig.savefig(f"{OUT}/{fname}", dpi=150); plt.close(fig)
def addr_plot(net, fname):
    cb = [b for b in prbs7(127)[:64] for _ in (0, 1)]
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    for rs, col in ((40, BLUE), (34, ORANGE)):
        t, v = run([net], cb, rs, None, 2.0); w = [(ti, vi) for ti, vi in zip(t, v[0]) if 8 * UI < ti < 40 * UI]
        ax.plot([p[0] / 1000 for p in w], [p[1] for p in w], color=col, lw=1.4, label=f"processor drive {rs} ohm")
    for y, name in ((VDD + 0.4, "VDD + 0.4 V (overshoot limit)"), (-0.4, "-0.4 V (undershoot limit)")):
        ax.axhline(y, color="#c0392b", lw=1, ls="--"); ax.text(40 * UI / 1000, y, " " + name, color=INK2, va="center", fontsize=8, clip_on=False)
    levels(ax, 8 * UI / 1000, 40 * UI / 1000)
    ax.set_xlim(8 * UI / 1000, 40 * UI / 1000); ax.set_ylim(-0.55, VDD + 0.55)
    ax.set_xlabel("time (ns)"); ax.set_ylabel("voltage at the memory ball (V)"); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=8)
    ax.set_title(f"{net} ({length(net):.1f} mm, unterminated): command bits at 400 MT/s", loc="left", fontsize=11, color=INK)
    fig.tight_layout(); fig.savefig(f"{OUT}/{fname}", dpi=150); plt.close(fig)
def pair_plot(p, q, rs, term, rev, title, fname):
    ck = [k % 2 for k in range(100)]; t, v = run([p, q], ck, rs, term, 2.0 if term is None else 1.5, invert=(q,), reverse=rev)
    a, b = 20 * UI, 26 * UI; idx = [i for i, ti in enumerate(t) if a <= ti <= b]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.8, 5.8), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    tt = [t[i] / 1000 for i in idx]
    ax1.plot(tt, [v[0][i] for i in idx], color=BLUE, lw=1.4, label=p.replace("DDR_", "")); ax1.plot(tt, [v[1][i] for i in idx], color=ORANGE, lw=1.4, label=q.replace("DDR_", ""))
    th = (max(v[0][len(v[0]) // 3:]) + min(v[0][len(v[0]) // 3:])) / 2
    cp, cn = crossings(t, v[0], th), crossings(t, v[1], th); sk = [min(abs(x - y) for y in cn) for x in cp[10:80]]
    for x in [c for c in cp if a <= c <= b]: ax1.axvline(x / 1000, color=GREY, lw=0.6, ls=":")
    ax1.set_ylabel("single-ended (V)"); ax1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=8, ncol=2)
    fig.suptitle(f"{title}: P/N crossing skew {sum(sk) / len(sk):.2f} ps", x=0.02, ha="left", fontsize=11, color=INK)
    dif = [v[0][i] - v[1][i] for i in idx]; ax2.plot(tt, dif, color=AQUA, lw=1.4)
    for y in (0.27, -0.27): ax2.axhline(y, color=ORANGE, lw=1, ls="--")
    ax2.text(b / 1000, 0.27, " VIHdiff(AC) +0.27 V", color=INK2, va="center", fontsize=8, clip_on=False); ax2.text(b / 1000, -0.27, " VILdiff(AC) -0.27 V", color=INK2, va="center", fontsize=8, clip_on=False)
    ax2.set_ylabel("differential (V)"); ax2.set_xlabel("time (ns)"); ax2.set_xlim(a / 1000, b / 1000)
    fig.tight_layout(); fig.savefig(f"{OUT}/{fname}", dpi=150); plt.close(fig)
if __name__ == "__main__":
    eye_plot("DDR_D6", 40, 60, False, f"DDR_D6 write eye ({length('DDR_D6'):.1f} mm, worst data line): processor 40 ohm, memory ODT 60 ohm", "eye_d6_write.png")
    eye_plot("DDR_D6", 34, 60, True, f"DDR_D6 read eye: memory 34 ohm, processor termination 60 ohm", "eye_d6_read.png")
    addr_plot("DDR_A3", "addr_a3.png")
    pair_plot("DDR_CK", "DDR_CKn", 40, None, False, "Clock CK/CKn (unterminated, processor 40 ohm)", "pair_ck.png")
    pair_plot("DDR_DQS0", "DDR_DQSn0", 40, 60, False, "Strobe DQS0 write (processor 40 ohm, ODT 60 ohm)", "pair_dqs0.png")
    print("plots in", OUT)
