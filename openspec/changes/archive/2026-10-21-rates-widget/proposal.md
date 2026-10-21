# Proposal

## Why

Checking stablecoin rates today means running a Python script and opening a CSV. The goal is a small "rate widget" that can be opened in one tap on desktop (narrow standalone window pinned to the taskbar) and on a phone (home-screen app), that shows current rates and **how they move over time**. Supply-APY history is free from DefiLlama. Borrow-APY history comes from the daily `history.csv` that the `switch-to-defillama-api` change starts recording.

## What Changes

- A single static web page (`index.html`), installable as a PWA (web app manifest + icon), hosted on GitHub Pages from the public `defi-parse` repo.
- Shows the 13 watchlisted pools (read from `watchlist.json`), grouped by platform: current supply APY, current borrow APY where it exists, and a 30-day supply sparkline per row.
- Tapping a row opens a 90-day chart of supply APY, plus borrow APY from `history.csv` once there are at least 2 recorded days.
- Refresh button and "updated" time; data is fetched live from DefiLlama on open and on refresh.
- CSV export of the merged daily history (supply from DefiLlama, borrow from `history.csv`).
- When installed on desktop, the window looks like a standalone app, not a browser window: the page's header becomes the title bar (no Chrome frame), and the first launch opens at phone proportions.
- Each pool's expanded row has a link to that pool's deposit page on the protocol (Kamino, Euler, Aave), so the user can go straight from a rate to lending.
- Phone-proportioned layout (designed at 360 px, works up to desktop widths without stretching), light/dark theme from the system setting, Inter font, design tokens `--bg --fg --soft --muted --line --surface --accent`, base text `0.875rem/1.5`, 16 px padding.

## Capabilities

### New Capabilities
- `rates-widget`: an installable web view of the watchlisted pools' current rates and rate trends, with CSV export.

### Modified Capabilities
<!-- none -->

## Impact

- New files: `index.html`, `manifest.webmanifest`, `icon.svg`.
- Depends on the `switch-to-defillama-api` change (needs `watchlist.json`, `history.csv`, and the public GitHub repo).
- GitHub Pages enabled on the repo (deploy from the default branch, root).
- `watchlist.json` gains a `url` field per pool (the collector ignores it).
- No build step, no backend, no new runtime dependencies. The browser calls `yields.llama.fi` directly (CORS allowed).
