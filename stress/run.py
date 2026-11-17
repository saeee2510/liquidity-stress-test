"""
Runs the liquidity stress test across scenarios, evaluates KRIs against limits,
performs a reverse stress test and writes a risk report plus dashboard.

Run: python -m stress.run
"""
import json

import numpy as np

from . import metrics as m
from .scenarios import SCENARIOS, blend


def reverse_stress(target_lcr=1.0, target_survival=30):
    """Find the stress intensity (0 = baseline, 1 = severe) at which each limit is first breached."""
    ts = np.linspace(0, 1.5, 301)
    lcrs = np.array([m.lcr(blend(t)) for t in ts])
    surv = np.array([m.survival_days(blend(t)) for t in ts])
    t_lcr = float(ts[np.argmax(lcrs < target_lcr)]) if (lcrs < target_lcr).any() else None
    t_surv = float(ts[np.argmax(surv < target_survival)]) if (surv < target_survival).any() else None
    return ts, lcrs, surv, t_lcr, t_surv


def main():
    results = {}
    for name, scn in SCENARIOS.items():
        k = m.kris(scn)
        results[name] = {"description": scn["description"],
                         "hqla": m.hqla_value(scn)[0], "outflows_30d": m.outflows_30d(scn),
                         "inflows_30d": m.inflows_30d(scn),
                         "kris": {n: {"value": v, "status": m.rag(n, v)} for n, v in k.items()}}
    ts, lcrs, surv, t_lcr, t_surv = reverse_stress()
    out = {"scenarios": results, "reverse_stress": {"lcr_breach_intensity": t_lcr,
                                                    "survival_breach_intensity": t_surv}}
    with open("output/results.json", "w") as fh:
        json.dump(out, fh, indent=2, default=float)
    write_report(out)
    dashboard(results, ts, lcrs, t_lcr)
    return out


def fmt(name, v):
    if name == "Survival days":
        return f"{v}+" if v >= m.HORIZON_DAYS else f"{v}"
    return f"{v:.0%}" if name != "LCR" else f"{v:.0%}"


def write_report(out):
    sc, rs = out["scenarios"], out["reverse_stress"]
    names = list(sc)
    lines = ["# Liquidity Stress Test: Risk Report", "",
             "Simulated payments/fintech balance sheet ($M). Simplified Basel III LCR plus a 90-day daily survival horizon.", "",
             "## Scenario results", "",
             "| Scenario | HQLA (post-haircut) | 30-day outflows | 30-day inflows | LCR | Survival days |",
             "|---|---|---|---|---|---|"]
    for n in names:
        r, k = sc[n], sc[n]["kris"]
        lines.append(f"| {n} | {r['hqla']:,.0f} | {r['outflows_30d']:,.0f} | {r['inflows_30d']:,.0f} | "
                     f"{k['LCR']['value']:.0%} ({k['LCR']['status']}) | "
                     f"{fmt('Survival days', k['Survival days']['value'])} ({k['Survival days']['status']}) |")
    lines += ["", "## Key risk indicators vs. limits (RAG)", "",
              "| KRI | Limit (amber / red) | " + " | ".join(names) + " |",
              "|---|---|" + "---|" * len(names)]
    for kri, (amber, red, direction) in m.LIMITS.items():
        lim = (f"≥ {amber:.0%} / {red:.0%}" if kri != "Survival days" else f"≥ {amber} / {red} days") \
            if direction == "min" else f"≤ {amber:.0%} / {red:.0%}"
        cells = [f"{fmt(kri, sc[n]['kris'][kri]['value'])} {sc[n]['kris'][kri]['status']}" for n in names]
        lines.append(f"| {kri} | {lim} | " + " | ".join(cells) + " |")
    lines += ["", "## Reverse stress test", "",
              f"- LCR falls below 100% at stress intensity **{rs['lcr_breach_intensity']:.2f}** "
              "(0 = baseline, 1 = severe scenario).",
              f"- Survival horizon falls below 30 days at intensity **{rs['survival_breach_intensity']:.2f}**.",
              "", "## Findings", ""]
    sev = sc[names[-1]]["kris"]
    mod = sc[names[1]]["kris"]
    lines += [
        f"- The firm meets the regulatory-style baseline with an LCR of {sc[names[0]]['kris']['LCR']['value']:.0%}.",
        f"- A firm-specific reputational event takes the LCR to {mod['LCR']['value']:.0%}: above the 100% minimum "
        f"but below the 110% internal limit (Amber).",
        f"- **The LCR alone understates this risk.** Under the same reputational event the firm runs below minimum "
        f"operating cash on day {mod['Survival days']['value']}, because outflows are front-loaded and the LCR only "
        "measures the 30-day total. Survival horizon should be monitored alongside the LCR, not instead of it.",
        f"- The severe combined scenario breaches both limits: LCR {sev['LCR']['value']:.0%} and only "
        f"{sev['Survival days']['value']} days of survival, driven mainly by merchant balance outflows, "
        "full wholesale runoff and credit line drawdowns.",
        f"- Undrawn commitments are {sev['Undrawn commitments / HQLA']['value']:.0%} of post-haircut HQLA, "
        "a structural exposure that grows exactly when liquidity is scarce.",
        "", "## Recommendations", "",
        "- Reduce reliance on merchant operational balances and wholesale funding, the two largest stressed outflows.",
        "- Review the size and terms of undrawn credit commitments, or pre-position collateral against them.",
        "- Set an early-warning trigger well before the reverse-stress breach point, e.g. daily merchant balance outflows "
        "above a set threshold, to activate the contingency funding plan.",
    ]
    with open("output/report.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def dashboard(results, ts, lcrs, t_lcr):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(results)
    short = ["Baseline", "Moderate", "Severe"]
    colors = {"Green": "#27ae60", "Amber": "#f39c12", "Red": "#c0392b"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    ax = axes[0, 0]
    vals = [results[n]["kris"]["LCR"]["value"] for n in names]
    ax.bar(short, vals, color=[colors[results[n]["kris"]["LCR"]["status"]] for n in names])
    ax.axhline(1.10, ls="--", color="#f39c12", label="Internal limit 110%")
    ax.axhline(1.00, ls="--", color="#c0392b", label="Regulatory minimum 100%")
    ax.set(title="Liquidity coverage ratio by scenario", ylabel="LCR")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    days = np.arange(1, m.HORIZON_DAYS + 1)
    for n, s in zip(names, short):
        ax.plot(days, m.daily_buffer(SCENARIOS[n]), label=s)
    ax.axhline(m.bs.MIN_OPERATING_CASH, color="#c0392b", ls=":", label="Minimum operating cash")
    ax.set(title="Liquidity buffer over 90 days", xlabel="Day", ylabel="$M")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.axis("off")
    kris = list(m.LIMITS)
    cell = [[f"{results[n]['kris'][k]['value']:.0%}" if k != "Survival days"
             else str(results[n]["kris"][k]["value"]) for n in names] for k in kris]
    table = ax.table(cellText=cell, rowLabels=kris, colLabels=short, loc="center", cellLoc="center")
    for i, k in enumerate(kris):
        for j, n in enumerate(names):
            table[i + 1, j].set_facecolor(colors[results[n]["kris"][k]["status"]])
            table[i + 1, j].get_text().set_color("white")
    table.scale(1, 1.6)
    ax.set_title("KRI status vs. limits")

    ax = axes[1, 1]
    ax.plot(ts, lcrs, color="#2c3e50")
    ax.axhline(1.0, color="#c0392b", ls="--")
    if t_lcr is not None:
        ax.axvline(t_lcr, color="#c0392b", ls=":", label=f"Breach at intensity {t_lcr:.2f}")
    ax.set(title="Reverse stress test: LCR vs. stress intensity", xlabel="Intensity (0 = baseline, 1 = severe)",
           ylabel="LCR")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig("output/dashboard.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
