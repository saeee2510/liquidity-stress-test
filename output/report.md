# Liquidity Stress Test: Risk Report

Simulated payments/fintech balance sheet ($M). Simplified Basel III LCR plus a 90-day daily survival horizon.

## Scenario results

| Scenario | HQLA (post-haircut) | 30-day outflows | 30-day inflows | LCR | Survival days |
|---|---|---|---|---|---|
| Baseline | 12,200 | 11,200 | 2,500 | 140% (Green) | 90+ (Green) |
| Moderate: reputational event | 12,200 | 13,830 | 2,200 | 105% (Amber) | 21 (Red) |
| Severe: combined market and firm stress | 11,900 | 19,500 | 1,750 | 67% (Red) | 9 (Red) |

## Key risk indicators vs. limits (RAG)

| KRI | Limit (amber / red) | Baseline | Moderate: reputational event | Severe: combined market and firm stress |
|---|---|---|---|---|
| LCR | ≥ 110% / 100% | 140% Green | 105% Amber | 67% Red |
| Survival days | ≥ 45 / 30 days | 90+ Green | 21 Red | 9 Red |
| Level 1 share of HQLA | ≥ 70% / 60% | 82% Green | 82% Green | 84% Green |
| Largest funding source share | ≤ 35% / 45% | 30% Green | 30% Green | 30% Green |
| Undrawn commitments / HQLA | ≤ 60% / 80% | 74% Amber | 74% Amber | 76% Amber |

## Reverse stress test

- LCR falls below 100% at stress intensity **0.38** (0 = baseline, 1 = severe scenario).
- Survival horizon falls below 30 days at intensity **0.27**.

## Findings

- The firm meets the regulatory-style baseline with an LCR of 140%.
- A firm-specific reputational event takes the LCR to 105%: above the 100% minimum but below the 110% internal limit (Amber).
- **The LCR alone understates this risk.** Under the same reputational event the firm runs below minimum operating cash on day 21, because outflows are front-loaded and the LCR only measures the 30-day total. Survival horizon should be monitored alongside the LCR, not instead of it.
- The severe combined scenario breaches both limits: LCR 67% and only 9 days of survival, driven mainly by merchant balance outflows, full wholesale runoff and credit line drawdowns.
- Undrawn commitments are 76% of post-haircut HQLA, a structural exposure that grows exactly when liquidity is scarce.

## Recommendations

- Reduce reliance on merchant operational balances and wholesale funding, the two largest stressed outflows.
- Review the size and terms of undrawn credit commitments, or pre-position collateral against them.
- Set an early-warning trigger well before the reverse-stress breach point, e.g. daily merchant balance outflows above a set threshold, to activate the contingency funding plan.
