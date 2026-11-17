"""Liquidity metrics: LCR (simplified Basel III), daily survival horizon, and KRIs."""
import numpy as np

from . import balance_sheet as bs

HORIZON_DAYS = 90


def hqla_value(scn):
    """Post-haircut HQLA with Basel caps: Level 2 <= 40% and Level 2B <= 15% of total."""
    by_level = {"L1": 0.0, "L2A": 0.0, "L2B": 0.0}
    for amount, level in bs.HQLA.values():
        by_level[level] += amount * (1 - scn["haircut"][level])
    l1, l2a, l2b = by_level["L1"], by_level["L2A"], by_level["L2B"]
    l2b = min(l2b, 15 / 85 * (l1 + l2a))                 # L2B cap
    l2 = min(l2a + l2b, 2 / 3 * l1)                      # total L2 cap
    return l1 + l2, {"L1": l1, "L2A": l2a, "L2B": l2b}


def outflows_30d(scn):
    funding = sum(bs.FUNDING[k] * scn["runoff"][k] for k in bs.FUNDING)
    draws = sum(bs.COMMITMENTS[k] * scn["drawdown"][k] for k in bs.COMMITMENTS)
    return funding + draws


def inflows_30d(scn):
    return sum(bs.INFLOWS[k] * scn["inflow"][k] for k in bs.INFLOWS)


def lcr(scn):
    """HQLA / net cash outflows over 30 days; inflows capped at 75% of outflows."""
    out = outflows_30d(scn)
    inflow = min(inflows_30d(scn), 0.75 * out)
    hqla, _ = hqla_value(scn)
    return hqla / (out - inflow)


def daily_buffer(scn, days=HORIZON_DAYS):
    """
    Day-by-day liquidity buffer. Outflows are front-loaded (half of the 30-day
    runoff in the first ~7 days), then continue at a slower pace after day 30.
    Inflows arrive evenly over 30 days.
    """
    d = np.arange(1, days + 1)
    weights = np.exp(-d / 10)
    weights[:30] = weights[:30] / weights[:30].sum()     # 30-day runoff fully realised by day 30
    weights[30:] = weights[29] * 0.5                     # slower ongoing runoff afterwards
    out = outflows_30d(scn) * weights
    inflow = np.where(d <= 30, inflows_30d(scn) / 30, 0.0)
    hqla, _ = hqla_value(scn)
    return hqla - np.cumsum(out - inflow)


def survival_days(scn, days=HORIZON_DAYS):
    """First day the buffer falls below minimum operating cash (horizon+ if never)."""
    buf = daily_buffer(scn, days)
    below = np.where(buf < bs.MIN_OPERATING_CASH)[0]
    return int(below[0] + 1) if len(below) else days


def kris(scn):
    hqla, levels = hqla_value(scn)
    total_funding = sum(bs.FUNDING.values())
    return {
        "LCR": lcr(scn),
        "Survival days": survival_days(scn),
        "Level 1 share of HQLA": levels["L1"] / hqla,
        "Largest funding source share": max(bs.FUNDING.values()) / total_funding,
        "Undrawn commitments / HQLA": sum(bs.COMMITMENTS.values()) / hqla,
    }


# (amber threshold, red threshold, direction): "min" = must stay above, "max" = must stay below
LIMITS = {
    "LCR": (1.10, 1.00, "min"),
    "Survival days": (45, 30, "min"),
    "Level 1 share of HQLA": (0.70, 0.60, "min"),
    "Largest funding source share": (0.35, 0.45, "max"),
    "Undrawn commitments / HQLA": (0.60, 0.80, "max"),
}


def rag(name, value):
    amber, red, direction = LIMITS[name]
    if direction == "min":
        return "Red" if value < red else "Amber" if value < amber else "Green"
    return "Red" if value > red else "Amber" if value > amber else "Green"
