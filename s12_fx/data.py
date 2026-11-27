"""Download daily OHLCV for the S12 FX/Gold universe via yfinance."""
from pathlib import Path
import pandas as pd
import yfinance as yf

from s12_fx.universe import INSTRUMENTS

DATA_DIR = Path("data/fx")
START = "2010-01-01"

def _fetch(sym: str) -> pd.DataFrame | None:
    for yf_sym in INSTRUMENTS[sym]["yf"]:
        try:
            d = yf.download(yf_sym, start=START, auto_adjust=True, progress=False)
            if d is None or len(d) == 0:
                continue
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            d = d[["Open", "High", "Low", "Close", "Volume"]].dropna()
            if len(d) < 200:
                continue
            d.index.name = "Date"
            return d
        except Exception:
            continue
    return None

def download_all() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for sym in INSTRUMENTS:
        d = _fetch(sym)
        if d is None:
            rows.append((sym, "FAIL", 0, "", ""))
            print(f"{sym}: FAIL")
            continue
        d.to_csv(DATA_DIR / f"{sym}.csv")
        rows.append((sym, "OK", len(d), d.index.min().date(), d.index.max().date()))
        print(f"{sym}: {len(d)} rows, {d.index.min().date()} -> {d.index.max().date()}")
    manifest = pd.DataFrame(rows, columns=["Ticker", "Status", "Rows", "Start", "End"])
    manifest.to_csv(DATA_DIR / "manifest.csv", index=False)
    return manifest

if __name__ == "__main__":
    download_all()
