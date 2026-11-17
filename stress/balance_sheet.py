"""
Simulated balance sheet of a payments / fintech firm ($ millions).
Customer balances behave like deposits, merchant settlement obligations
must be paid on time, and undrawn credit lines can be drawn under stress.
"""

# High-quality liquid assets: (amount, regulatory level)
HQLA = {
    "Cash and central bank reserves": (4_000, "L1"),
    "US Treasuries": (6_000, "L1"),
    "Agency MBS": (2_000, "L2A"),
    "Investment-grade corporate bonds": (1_000, "L2B"),
}

# Funding sources that can run off within 30 days ($M)
FUNDING = {
    "Retail balances, stable": 12_000,
    "Retail balances, less stable": 10_000,
    "Merchant operational balances": 8_000,
    "Wholesale funding": 5_000,
    "Merchant settlement payables": 5_000,
}

# Committed but undrawn facilities that customers can draw ($M)
COMMITMENTS = {
    "Consumer credit lines": 6_000,
    "Merchant credit facilities": 3_000,
}

# Contractual inflows due within 30 days ($M)
INFLOWS = {
    "Card network receivables": 2_000,
    "Loan repayments": 1_000,
}

MIN_OPERATING_CASH = 1_000   # buffer below which the firm can't operate normally
