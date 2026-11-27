"""Feature construction — S4 momentum score verbatim."""
import numpy as np
import pandas as pd

ANNUALIZATION = 252

def rank01(x: pd.DataFrame) -> pd.DataFrame:
    return x.rank(axis=1, pct=True)

def make_features(prices: pd.DataFrame) -> dict:
    ret = prices.pct_change()
    mom21 = prices / prices.shift(21) - 1
    mom63 = prices / prices.shift(63) - 1
    mom126 = prices / prices.shift(126) - 1
    vol63 = ret.rolling(63, min_periods=40).std() * np.sqrt(ANNUALIZATION)
    risk_mom = mom63 / vol63.replace(0, np.nan)
    trend100 = prices > prices.rolling(100, min_periods=60).mean()
    trend200 = prices > prices.rolling(200, min_periods=120).mean()

    score = (
        0.35 * (rank01(mom126) - 0.5)
        + 0.25 * (rank01(mom63) - 0.5)
        + 0.15 * (rank01(mom21) - 0.5)
        + 0.15 * (rank01(risk_mom) - 0.5)
        + 0.10 * (rank01(trend100.astype(float)) - 0.5)
    )
    breadth = trend200.mean(axis=1, skipna=True)
    corr = ret.rolling(63, min_periods=40).corr()

    return {
        "ret": ret, "mom21": mom21, "mom63": mom63, "mom126": mom126,
        "vol63": vol63, "score": score, "trend200": trend200,
        "breadth": breadth, "corr": corr,
    }
