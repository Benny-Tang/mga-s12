"""Correlation-distance KMeans clustering with max-per-cluster cap."""
import numpy as np
import pandas as pd

try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

def corr_to_distance(corr: pd.DataFrame) -> pd.DataFrame:
    return np.sqrt(np.clip(2 * (1 - corr), 0, 4))

def assign_clusters(corr_row: pd.DataFrame, k: int = 4, seed: int = 42) -> pd.Series:
    tickers = corr_row.index.tolist()
    if not HAS_SKLEARN or len(tickers) < k:
        return pd.Series({t: i for i, t in enumerate(tickers)})
    dist = corr_to_distance(corr_row).values
    km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(dist)
    return pd.Series(km.labels_, index=tickers)

def select_with_cap(ranked: pd.Series, clusters: pd.Series, top_n: int, max_per_cluster: int = 1) -> list[str]:
    used: dict[int, int] = {}
    selected: list[str] = []
    for sym in ranked.index:
        if len(selected) >= top_n:
            break
        c = int(clusters.loc[sym])
        if used.get(c, 0) >= max_per_cluster:
            continue
        used[c] = used.get(c, 0) + 1
        selected.append(sym)
    return selected
