"""
Stress scenarios: 30-day runoff, drawdown and inflow rates, plus HQLA haircuts.
Baseline uses simplified Basel III LCR-style rates; the stresses are internal
scenarios, deliberately harsher than the regulatory baseline.
"""

SCENARIOS = {
    "Baseline": {
        "description": "Regulatory-style 30-day stress (simplified Basel III LCR assumptions)",
        "runoff": {"Retail balances, stable": 0.05, "Retail balances, less stable": 0.10,
                   "Merchant operational balances": 0.25, "Wholesale funding": 0.40,
                   "Merchant settlement payables": 1.00},
        "drawdown": {"Consumer credit lines": 0.05, "Merchant credit facilities": 0.10},
        "inflow": {"Card network receivables": 1.00, "Loan repayments": 0.50},
        "haircut": {"L1": 0.00, "L2A": 0.15, "L2B": 0.50},
    },
    "Moderate: reputational event": {
        "description": "Firm-specific stress: negative news drives customers and merchants to move balances",
        "runoff": {"Retail balances, stable": 0.05, "Retail balances, less stable": 0.15,
                   "Merchant operational balances": 0.35, "Wholesale funding": 0.60,
                   "Merchant settlement payables": 1.00},
        "drawdown": {"Consumer credit lines": 0.08, "Merchant credit facilities": 0.15},
        "inflow": {"Card network receivables": 0.90, "Loan repayments": 0.40},
        "haircut": {"L1": 0.00, "L2A": 0.15, "L2B": 0.50},
    },
    "Severe: combined market and firm stress": {
        "description": "Reputational event during a market-wide shock: deposit run, credit line drawdowns, wider haircuts",
        "runoff": {"Retail balances, stable": 0.10, "Retail balances, less stable": 0.25,
                   "Merchant operational balances": 0.50, "Wholesale funding": 1.00,
                   "Merchant settlement payables": 1.00},
        "drawdown": {"Consumer credit lines": 0.15, "Merchant credit facilities": 0.30},
        "inflow": {"Card network receivables": 0.75, "Loan repayments": 0.25},
        "haircut": {"L1": 0.00, "L2A": 0.25, "L2B": 0.60},
    },
}


def blend(t, base=SCENARIOS["Baseline"], severe=SCENARIOS["Severe: combined market and firm stress"]):
    """
    Scenario at intensity t: 0 = baseline, 1 = severe, >1 = beyond severe.
    Rates are capped to [0, 1]. Used for reverse stress testing.
    """
    out = {}
    for key in ("runoff", "drawdown", "inflow", "haircut"):
        out[key] = {k: min(1.0, max(0.0, base[key][k] + t * (severe[key][k] - base[key][k])))
                    for k in base[key]}
    return out
