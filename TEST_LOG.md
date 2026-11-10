[TEST_LOG (1).md](https://github.com/user-attachments/files/34613690/TEST_LOG.1.md)
# Test log
Count of tests run so far (for multiple-testing judgement): see the table. Include earlier work below.

| ID | Date | Idea | Expected | Result (stitched OOS Sharpe unless noted) | Verdict |
| --- | --- | --- | --- | --- | --- |
| E01 | 2026-10-18 | HBA 33 stocks, 72-config walk-forward | baseline | 1.360, median fold 1.282, 88% positive, holdout 0.316 | baseline |
| E02 | 2026-10-18 | 336-config cadence/regime/breadth/target-vol sweep | higher | 1.240 | worse, overfit |
| E03 | 2026-10-18 | MGA, 30 ETFs | diversify | 0.483 | fail |
| E04 | 2026-10-18 | Blend HBA/MGA | smoother | 1.366 at 90/10 vs 1.370 alone | no gain |
| E05 | 2026-10-18 | 86 stocks | breadth | 1.235 | worse |
| E06 | 2026-10-18 | + reversal / low-vol / overnight / all3 | lift | 1.245 / 1.240 / 1.293 / 1.277 | no gain; overnight halves drawdown |
| E07 | 2026-10-18 | Drawdown guard 8% | lower risk | fixed-config Sharpe 1.101 -> 0.934 | hurts |
| T001 | 2026-10-22 | Guard threshold 12/15/20% or off (fixed config, before 2025-08-29, full-history Sharpe) | looser guard keeps Sharpe near unguarded and keeps some drawdown benefit | off 1.153 (maxDD -24.3%); 8% 0.988; 12% 1.125 (-20.7%); 15% 1.066 (-26.8%); 20% 1.122 (-27.3%) | 8% clearly worst; 12% to 20% are within noise of off and not monotonic. Guard off or 12% are equivalent on this evidence. Note: hypothesis was written the same day as the run |
| T002 | 2026-11-10 | HBA 33 stocks (data/hba33, Yahoo split/dividend-adjusted OHLC to 2026-08-31). Base HBA score + 0.30 x Reversal Pressure long flag. Indicator: TradingView "Reversal Pressure [Harmony Algo]" (open-source Pine v6), ported in tools/revpress.py with all constants frozen (63 / 1.4 / 1.2 / 24 / 48). Flag = 1 while a Buy setup is in tracking (phase 2, side 1) at day t's close, else 0; used like the other score components (decision at close t, applied to t+1). Same 36-config grid, full_day only, 5 bps, identical walk-forward as t_second_signal_v8. One variant, no weight tuning. Script: tests/t002_revpress_flag.py | No gain, in line with E06 (+reversal 1.245 vs 1.360 base). Pass only if stitched Sharpe beats base in the same run AND median fold, % positive folds and max drawdown are no worse. Holdout looked at once. Pre-registered in chat and approved before the run (same day) | base 1.360 (CAGR 31.0%, max DD -37.0%, median fold 1.282, 88% positive, holdout 0.316, holdout DD -12.2%); +revpress 1.410 (33.5%, -32.1%, 1.326, 84% positive, holdout 0.146, holdout DD -11.9%). Daily OOS return correlation with base 0.957. Flag on avg 2.35 names/day, >=1 name flagged on 78% of days. Base row reproduces E01 exactly. Port not yet checked bar-by-bar against TradingView Data Window | FAIL on pre-registered bar (% positive folds 84% vs 88%, one fold of 25). Stitched +0.05 within noise, holdout worse. Retired, no variants or weight tuning pursued (each would be a new test on the same history). Survivorship caveat applies. |

Rows for new ideas: write the first six columns BEFORE running.

<!-- END OF FILE - TEST_LOG.md - 2026-11-10 -->
