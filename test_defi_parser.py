import io
from contextlib import redirect_stdout

import pandas as pd

from defi_parser import build_rows, merge_history

WATCHLIST = [
    {"id": "lend", "platform": "Euler", "market": "eUSDC-2", "chain": "Ethereum", "asset": "USDC"},
    {"id": "vault", "platform": "Kamino", "market": "RockawayX", "chain": "Solana", "asset": "USDC"},
    {"id": "usdt0", "platform": "Aave v3", "market": "Core", "chain": "Arbitrum", "asset": "USDT"},
    {"id": "gone", "platform": "Euler", "market": "eUSDT-2", "chain": "Ethereum", "asset": "USDT"},
]
POOLS = [
    {"pool": "lend", "symbol": "USDC", "apy": 7.2, "tvlUsd": 100},
    {"pool": "vault", "symbol": "USDC", "apy": 5.2, "tvlUsd": 6000},
    {"pool": "usdt0", "symbol": "USD₮0", "apy": 3.0, "tvlUsd": 50},
    {"pool": "unlisted", "symbol": "USDC", "apy": 99.0, "tvlUsd": 1},
]
LEND_BORROW = [
    {"pool": "lend", "apyBaseBorrow": 8.8, "ltv": 0.8, "totalSupplyUsd": 2000, "totalBorrowUsd": 1900},
    {"pool": "usdt0", "apyBaseBorrow": 4.1, "ltv": 0.75, "totalSupplyUsd": 900, "totalBorrowUsd": 850},
]

out = io.StringIO()
with redirect_stdout(out):
    rows = build_rows(WATCHLIST, POOLS, LEND_BORROW, "2026-10-21")
by_id = {r["pool_id"]: r for r in rows}

# Lending pool: every field numeric, LTV fraction -> percent.
lend = by_id["lend"]
assert (lend["supply_apy"], lend["borrow_apy"], lend["ltv"]) == (7.2, 8.8, 80.0)
assert (lend["total_supply_usd"], lend["total_borrow_usd"]) == (2000, 1900)

# Deposit-only vault: no borrow side, total supply falls back to TVL.
vault = by_id["vault"]
assert vault["borrow_apy"] is None and vault["ltv"] is None and vault["total_borrow_usd"] is None
assert vault["total_supply_usd"] == 6000 and vault["supply_apy"] == 5.2

# Asset label comes from the watchlist, not the upstream symbol.
assert by_id["usdt0"]["asset"] == "USDT"

# Missing pool warns, the rest are kept; unlisted pools never appear.
assert "::warning::Missing pool: Euler eUSDT-2 USDT (gone)" in out.getvalue()
assert set(by_id) == {"lend", "vault", "usdt0"}

# Same-day re-run replaces only today's rows; earlier dates stay untouched.
first = merge_history(None, rows, "2026-10-21")
yesterday = first.assign(date="2026-10-20", supply_apy=1.0)
history = pd.concat([yesterday, first], ignore_index=True)
rerun = [dict(r, supply_apy=9.9) for r in rows]
merged = merge_history(history, rerun, "2026-10-21")
assert len(merged) == 6
assert (merged[merged["date"] == "2026-10-20"]["supply_apy"] == 1.0).all()
assert (merged[merged["date"] == "2026-10-21"]["supply_apy"] == 9.9).all()

print("ok")
