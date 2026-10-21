# Proposal

## Why

`defi_parser.py` scrapes Kamino and Euler pages with headless Chrome and reads table cells by position. Both scrapers now return wrong data without raising errors: Kamino rows come back as `Unknown Market` with `Supply APY: +1` / `Borrow APY: Deposit`, and the Euler URL no longer exists. DefiLlama's free yields API already publishes supply and borrow rates for all three protocols, so the scraping layer can be removed instead of repaired.

The goal is also changing from a "run by hand, look at a CSV" script to a **rate history**. DefiLlama keeps free supply-APY history per pool, but borrow-APY history is a paid endpoint (`/chartLendBorrow` → 402). The only free way to get a borrow trend is to record the current values ourselves every day, starting now. The `rates-widget` change reads this history.

## What Changes

- Replace both Selenium scrapers (Kamino, Euler) and the existing Aave query with one data source: DefiLlama `/pools` (supply side) joined with `/lendBorrow` (borrow side) on pool id.
- Track an explicit watchlist of pools in a shared `watchlist.json` (also read by the widget) instead of scraping pages or matching symbols:
  - Kamino (Solana): JLP Market USDC/USDT, SOL/BTC Market USDC/USDT (formerly "Main Market"), RockawayX RWA USDC vault.
  - Euler v2 (Ethereum): eUSDC-2 and eUSDT-2 vaults, the pair at `app.euler.finance/borrow/0x797D…48a9/0x3136…2162`.
  - Aave v3 core market: USDC/USDT on Ethereum, Arbitrum, Avalanche.
- **BREAKING** Kamino "Jito Market" is dropped (it has no USDC/USDT pools now). Aave on Optimism is dropped (DefiLlama has no core-market USDC/USDT pool there).
- Fill in fields that are `N/A` today: borrow APY, LTV, total supplied and total borrowed in USD.
- **BREAKING** Output changes from an overwritten snapshot `defi_rates.csv` to an append-only `history.csv` next to the script: one row per pool per UTC day, numeric values. Re-running on the same day replaces that day's rows.
- Run the collector daily on GitHub Actions and commit `history.csv` back to the repository. A manual run trigger is also available.
- Put the project under git and publish it as a **public** GitHub repository (also required for the widget's GitHub Pages hosting).
- Warn when a watchlist pool is missing from the API response instead of silently dropping it.
- Remove `selenium`, `webdriver-manager`, and the Chrome requirement, along with `--ignore-certificate-errors`.

## Capabilities

### New Capabilities
- `stablecoin-rates`: collecting USDC/USDT supply and borrow rates for a fixed watchlist of lending pools once a day and keeping them as an append-only history file.

### Modified Capabilities
<!-- none: no existing specs -->

## Impact

- `defi_parser.py`: rewritten as the collector.
- New files: `watchlist.json`, `history.csv`, `.github/workflows/collect.yml`, `.gitignore`.
- Dependencies: drops `selenium` and `webdriver-manager`; keeps `requests` and `pandas`. Chrome is no longer needed.
- New external dependencies: `yields.llama.fi` availability and its pool ids staying stable, GitHub Actions scheduled runs.
- Repository becomes public on GitHub.
