# Design

## Context

See proposal.md (Why). Current `defi_parser.py` has three independent fetchers; two depend on Selenium page layout and are broken. All three protocols are tracked by DefiLlama's free yields API (checked live 2026-10-21, all endpoints send `access-control-allow-origin: *`):

- `GET https://yields.llama.fi/pools` → `{"data": [...]}`, about 20k pools, 2.2 MB gzipped. Per pool: `pool` (uuid), `project`, `chain`, `symbol`, `poolMeta` (market or vault name), `apy` (supply, base + rewards, %), `tvlUsd`.
- `GET https://yields.llama.fi/lendBorrow` → list keyed by the same `pool` uuid: `apyBaseBorrow` (%), `ltv` (fraction 0..1), `totalSupplyUsd`, `totalBorrowUsd`. Only pools that support borrowing appear here; deposit-only vaults (e.g. RockawayX) do not.
- `GET https://yields.llama.fi/chart/{pool}` → free daily supply-APY/TVL history (used by the widget, not the collector).
- `GET https://yields.llama.fi/chartLendBorrow/{pool}` → **402 Payment Required**. This is why borrow history must be self-recorded.

For lending pools, `tvlUsd` in `/pools` is **available liquidity** (supply − borrow), not total supplied.

`defi-parse` is not a git repository yet.

## Goals / Non-Goals

**Goals:**
- One fetch path, one selection mechanism, numeric output.
- A daily, append-only history that starts accumulating as early as possible.

**Non-Goals:**
- Displaying the data (the `rates-widget` change does that).
- Backfilling borrow history before the first run (needs the paid API).
- Discovering new pools automatically (the watchlist is edited by hand).
- Reward-token breakdown (supply APY uses DefiLlama's combined `apy`; borrow APY uses `apyBaseBorrow` only).
- Fallback to protocol-native APIs (Kamino/Euler), which isn't needed while DefiLlama covers every watchlisted pool.

## Decisions

### Select every pool by pinned DefiLlama pool id, including Aave
Alternatives considered:
- *Match by `poolMeta` name*: Kamino renamed "Main Market" → "SOL/BTC Market" (same on-chain address `7u3HeHx…`). A name match would have silently lost that market. `eUSDC-2` also exists on several chains.
- *Rule-based filter for Aave (project + chain + symbol contains "usdc"/"usdt")*: this is what the old code did. On today's data it wrongly includes `SYRUPUSDT` and `USDTB` and misses Arbitrum USDT, which is now listed as `USD₮0`. Pinning six ids is shorter and exact.

Trade-off: a pool migration upstream needs a manual id update, which the missing-pool warning will flag.

### Watchlist lives in `watchlist.json`
A JSON array of `{id, platform, market, chain, asset}`. Python reads it with `json`, and the widget fetches it as a static file from the same GitHub Pages origin. This avoids keeping two copies of the 13 ids. JSON over CSV/YAML: both consumers parse it natively, no extra dependency.

### Watchlist (verified 2026-10-21)

| Platform | Market | Chain | Asset | DefiLlama pool id |
|---|---|---|---|---|
| Kamino | JLP Market | Solana | USDC | `62649c90-e61a-4ffc-ba31-3d754b7461fc` |
| Kamino | JLP Market | Solana | USDT | `2d284e9c-7ae4-486f-88be-1584bdc3dd11` |
| Kamino | SOL/BTC Market | Solana | USDC | `d2141a59-c199-4be7-8d4b-c8223954836b` |
| Kamino | SOL/BTC Market | Solana | USDT | `546b3c0c-138d-4190-b46b-efa1765f1dd3` |
| Kamino | RockawayX RWA USDC | Solana | USDC | `8c4bbc10-5763-5d5b-8450-05ddd24b1c33` |
| Euler | eUSDC-2 | Ethereum | USDC | `a0f53224-c152-416e-8599-4563e70c6040` |
| Euler | eUSDT-2 | Ethereum | USDT | `bc244917-e28c-4f10-bfa4-79bf90529023` |
| Aave v3 | Core | Ethereum | USDC | `aa70268e-4b52-42bf-a116-608b370f9501` |
| Aave v3 | Core | Ethereum | USDT | `f981a304-bb6c-45b8-b0c5-fd2f515ad23a` |
| Aave v3 | Core | Arbitrum | USDC | `d9fa8e14-0447-4207-9ae8-7810199dfa1f` |
| Aave v3 | Core | Arbitrum | USDT (`USD₮0`) | `3a6cc030-738d-4e19-8a40-e63e9c4d5a6f` |
| Aave v3 | Core | Avalanche | USDC | `c4b05318-88af-4536-a834-f5fc8940d2d3` |
| Aave v3 | Core | Avalanche | USDT | `e6692d08-85b6-4b50-952b-7c5c531862fe` |

Euler vault ids were matched to the user's URL by reading `name()`/`asset()` on-chain: `0x797D…48a9` = eUSDC-2 (USDC), `0x3136…2162` = eUSDT-2 (USDT).

### History format (`history.csv`)

Long format, one row per pool per UTC date:

```
date,pool_id,platform,market,chain,asset,supply_apy,borrow_apy,ltv,total_supply_usd,total_borrow_usd
2026-10-22,62649c90-…,Kamino,JLP Market,Solana,USDC,4.59,5.47,0,20639498,19319601
```

| Column | Source |
|---|---|
| supply_apy | `/pools.apy` |
| borrow_apy | `/lendBorrow.apyBaseBorrow` |
| ltv | `/lendBorrow.ltv × 100` |
| total_supply_usd | `/lendBorrow.totalSupplyUsd`, else `/pools.tvlUsd` (deposit-only vaults, where TVL = deposits) |
| total_borrow_usd | `/lendBorrow.totalBorrowUsd` |

Missing source values become empty cells. Long format over wide (one column per pool): adding or removing a watchlist pool never changes the header, and it filters easily by `pool_id` in the widget.

Same-day re-run: read the existing file, drop rows where `date == today`, append the new rows, and write. Growth is about 1 KB/day, so rewriting the whole file is fine.

### Keep `requests` + `pandas`
Both are already installed locally. pandas handles the read/filter/append/write and the console print. In CI they're installed with one `pip install` line, without a `requirements.txt`.

### Fail fast on source errors
`raise_for_status()` and let the exception exit the script (non-zero) before any file write. Drop the old catch-all `try/except` + `traceback` wrappers that turned failures into "no data" prints.

### Missing-pool warning format
Print `::warning::Missing pool: <platform> <market> <asset> (<id>)`. GitHub Actions turns that line into a visible run annotation; locally it is just a readable line.

### GitHub Actions workflow (`.github/workflows/collect.yml`)
- Triggers: `schedule: cron "0 6 * * *"` (06:00 UTC daily) and `workflow_dispatch`.
- `permissions: contents: write`.
- Steps: checkout → setup-python → `pip install requests pandas` → `python defi_parser.py` → if `history.csv` changed, commit as `github-actions[bot]` and push.
- The commit step only runs if the script succeeded, so a failed fetch never commits.

### Repository
`git init`, a `.gitignore` for `__pycache__/` and the old `defi_rates.csv`, a public GitHub repo created with `gh repo create`, then push. The chat export `Claude-DeFi парсер-*.json` is **excluded by default** because it contains local paths and the full conversation. The user can opt in before the first push.

## Risks / Trade-offs

- [DefiLlama outage or rate limit] → that day's run fails (visible in Actions, GitHub emails the owner). That day has no row, and later days continue. A manual `workflow_dispatch` re-run fills it the same day.
- [GitHub cron delay] → runs can start minutes to an hour late under load. Irrelevant for daily data.
- [Scheduled workflows in public repos are disabled after 60 days without repository activity] → the daily commit should count as activity. Verify after the first weeks.
- [DefiLlama `ltv` semantics differ per protocol adapter, e.g. `0` for Kamino isolated markets] → recorded as-is.
- [Pool ids change after a protocol migration] → the missing-pool warning names the entry. Fix by looking up the new id and editing `watchlist.json`.
