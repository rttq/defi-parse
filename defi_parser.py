"""Daily collector: records USDC/USDT supply and borrow rates for the pools in
watchlist.json from DefiLlama's free yields API and appends them to history.csv."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).parent
HISTORY = HERE / "history.csv"
POOLS_URL = "https://yields.llama.fi/pools"
LEND_BORROW_URL = "https://yields.llama.fi/lendBorrow"
COLUMNS = [
    "date", "pool_id", "platform", "market", "chain", "asset",
    "supply_apy", "borrow_apy", "ltv", "total_supply_usd", "total_borrow_usd",
]


def fetch(url):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def build_rows(watchlist, pools, lend_borrow, date):
    """Join /pools (supply) and /lendBorrow (borrow) on pool id for each watchlist entry."""
    pools_by_id = {p["pool"]: p for p in pools}
    borrow_by_id = {b["pool"]: b for b in lend_borrow}
    rows = []
    for entry in watchlist:
        pool = pools_by_id.get(entry["id"])
        if pool is None:
            print(f"::warning::Missing pool: {entry['platform']} {entry['market']} {entry['asset']} ({entry['id']})")
            continue
        borrow = borrow_by_id.get(entry["id"], {})
        ltv = borrow.get("ltv")
        total_supply = borrow.get("totalSupplyUsd")
        if total_supply is None:
            # Deposit-only vaults are absent from /lendBorrow; their TVL equals deposits.
            total_supply = pool.get("tvlUsd")
        rows.append({
            "date": date,
            "pool_id": entry["id"],
            "platform": entry["platform"],
            "market": entry["market"],
            "chain": entry["chain"],
            "asset": entry["asset"],
            "supply_apy": pool.get("apy"),
            "borrow_apy": borrow.get("apyBaseBorrow"),
            "ltv": ltv * 100 if ltv is not None else None,
            "total_supply_usd": total_supply,
            "total_borrow_usd": borrow.get("totalBorrowUsd"),
        })
    return rows


def merge_history(history, rows, date):
    """Keep earlier dates untouched; replace this date's rows with the new ones."""
    new = pd.DataFrame(rows, columns=COLUMNS)
    if history is None or history.empty:
        return new
    kept = history[history["date"] != date]
    return new if kept.empty else pd.concat([kept, new], ignore_index=True)


def main():
    watchlist = json.loads((HERE / "watchlist.json").read_text(encoding="utf-8"))
    try:
        pools = fetch(POOLS_URL)["data"]
        lend_borrow = fetch(LEND_BORROW_URL)
    except requests.RequestException as e:
        sys.exit(f"::error::DefiLlama request failed: {e}")

    today = datetime.now(timezone.utc).date().isoformat()
    rows = build_rows(watchlist, pools, lend_borrow, today)
    history = pd.read_csv(HISTORY, dtype={"date": str, "pool_id": str}) if HISTORY.exists() else None
    merge_history(history, rows, today).to_csv(HISTORY, index=False)

    table = pd.DataFrame(rows, columns=COLUMNS)
    for platform, group in table.groupby("platform", sort=False):
        print(f"\n{platform}")
        print(group[["market", "chain", "asset", "supply_apy", "borrow_apy"]].round(2).to_string(index=False))
    print(f"\n{len(rows)} rows for {today} -> {HISTORY}")


if __name__ == "__main__":
    main()
