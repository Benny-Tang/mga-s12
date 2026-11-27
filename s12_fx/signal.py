"""Daily S12 FX/Gold signal generator. Emits a markdown trade sheet."""
import argparse
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from s12_fx.universe import INSTRUMENTS
from s12_fx.features import make_features
from s12_fx.clusters import assign_clusters, select_with_cap

DATA_DIR = Path("data/fx")

CFG = dict(
    top_n=2,
    rebalance_every=5,
    target_vol=0.15,
    max_exposure=1.0,
    min_breadth=0.50,
    k_clusters=4,
    max_per_cluster=1,
    equity=100_000.0,
)

def load_prices() -> pd.DataFrame:
    frames = {}
    for sym in INSTRUMENTS:
        p = DATA_DIR / f"{sym}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p, parse_dates=["Date"]).set_index("Date").sort_index()
        frames[sym] = d["Close"]
    return pd.concat(frames, axis=1).sort_index()

def lots_for(sym: str, notional_usd: float, price: float) -> float:
    meta = INSTRUMENTS[sym]
    cu = meta["contract_units"]

    if meta["type"] == "metal":
        contract_notional = cu * price
    elif meta["type"] == "index":
        contract_notional = cu * price
    else:  # FX
        if meta["quote"] == "USD":
            contract_notional = cu * price
        elif meta["base"] == "USD":
            contract_notional = cu
        else:
            contract_notional = cu * price
            
    if contract_notional <= 0:
        return 0.0
    return round(notional_usd / contract_notional, 2)

def build_signal(prices: pd.DataFrame, feats: dict, today: date) -> dict:
    last = prices.index[-1]
    breadth = feats["breadth"].iloc[-1]
    regime_on = bool(pd.notna(breadth) and breadth >= CFG["min_breadth"])

    out = {
        "date": str(today), "bar_date": str(last.date()),
        "breadth": float(breadth) if pd.notna(breadth) else None,
        "regime_on": regime_on, "orders": [], "skipped": [],
    }
    if not regime_on:
        out["reason"] = f"breadth {breadth:.2f} < {CFG['min_breadth']:.2f} — 100% cash"
        return out

    score_row = feats["score"].iloc[-1]
    mom126 = feats["mom126"].iloc[-1]
    mom63 = feats["mom63"].iloc[-1]
    vol_row = feats["vol63"].iloc[-1]

    eligible = score_row.dropna().copy()
    eligible = eligible[(mom126[eligible.index] > 0) & (mom63[eligible.index] > 0)]
    if len(eligible) == 0:
        out["reason"] = "no instruments pass positive-momentum filter — 100% cash"
        return out

    ranked = eligible.sort_values(ascending=False)
    
    ret = feats["ret"]
    corr = ret.tail(63).corr()
    
    clusters = assign_clusters(corr, k=CFG["k_clusters"])
    selected = select_with_cap(ranked, clusters, CFG["top_n"], CFG["max_per_cluster"])

    if not selected:
        out["reason"] = "cluster cap eliminated all candidates"
        return out

    vol = vol_row[selected].replace(0, np.nan).dropna()
    if len(vol) == 0:
        out["reason"] = "vol unavailable for selected names"
        return out
    inv = 1.0 / vol
    weights = inv / inv.sum()

    port_vol = float((weights * vol).sum())
    scale = min(CFG["target_vol"] / port_vol, CFG["max_exposure"]) if port_vol > 0 else 0.0
    weights = weights * scale

    price_row = prices.iloc[-1]
    for sym, w in weights.items():
        notional = float(w) * CFG["equity"]
        px = float(price_row[sym])
        lots = lots_for(sym, notional, px)
        if lots < 0.01:
            out["skipped"].append({"sym": sym, "weight": float(w), "notional": notional, "reason": "<0.01 lots"})
            continue
        out["orders"].append({
            "symbol": sym, "side": "BUY", "lots": lots,
            "weight": round(float(w), 4), "notional_usd": round(notional, 2),
            "price": px, "cluster": int(clusters.loc[sym]),
            "score": round(float(score_row[sym]), 4),
        })
    return out

def render_markdown(sig: dict) -> str:
    lines = [f"# S12 FX/Gold Signal — {sig['date']} (bar {sig['bar_date']})", ""]
    lines.append(f"**Account:** XM Paper A ($100,000)  ")
    lines.append(f"**Breadth:** {sig['breadth']:.3f}" if sig['breadth'] is not None else "**Breadth:** n/a")
    lines.append(f"**Regime:** {'ON' if sig['regime_on'] else 'OFF — CASH'}  ")
    if "reason" in sig:
        lines.append(f"**Reason:** {sig['reason']}  ")
    lines.append("")
    if sig["orders"]:
        lines.append("## ORDERS")
        lines.append("| Symbol | Side | Lots | Notional USD | Weight | Price | Cluster | Score |")
        lines.append("|--------|------|------|--------------|--------|-------|---------|-------|")
        for o in sig["orders"]:
            lines.append(f"| {o['symbol']} | {o['side']} | {o['lots']:.2f} | {o['notional_usd']:,.2f} | {o['weight']:.4f} | {o['price']:.5f} | {o['cluster']} | {o['score']:.4f} |")
    else:
        lines.append("_No orders today._")
    lines.append("")
    lines.append("_Contracts assumed: GOLD 100oz, SILVER 5,000oz, FX 100k, US30/US500 1 point/unit._")
    lines.append("_**CRITICAL: Switch your MT5 order ticket to 'Lots' before entering these numbers.**_")
    return "\n".join(lines)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="signals")
    args = ap.parse_args()

    prices = load_prices()
    if prices.empty:
        raise SystemExit("No data in data/fx — run `python -m s12_fx.data` first.")
    feats = make_features(prices)
    sig = build_signal(prices, feats, today=date.today())
    md = render_markdown(sig)

    outdir = Path(args.output); outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"SIGNAL_{sig['date']}.md"
    path.write_text(md)
    print(md)
