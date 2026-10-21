# Tasks

## 1. Page shell and theme

- [x] 1.1 Create `index.html` with Inter, the light/dark token palette from design.md under `:root` and `prefers-color-scheme: dark`, base `0.875rem/1.5`, 16 px padding, `max-width: 420px` centered column, header with title, "updated" time and refresh button; verify in a browser at 320 px and 1920 px widths (no horizontal scroll; narrow centered column) and in both OS themes
- [x] 1.2 Add `manifest.webmanifest` and `icon.svg` and link them (plus `theme-color` and `apple-touch-icon`); verify the manifest shows no errors in Chrome DevTools → Application → Manifest

## 2. Data and rows

- [x] 2.1 Load `watchlist.json`, 13 × `/chart/{id}`, `/lendBorrow` and `history.csv` with `Promise.allSettled`; render rows grouped by platform with current supply APY (last `/chart` point) and current borrow APY (`/lendBorrow`, blank for deposit-only); verify 13 rows render against the live API and RockawayX shows no borrow value
- [x] 2.2 Draw the 30-day supply sparkline per row as inline SVG; skip it when fewer than 2 points; verify visually and by temporarily slicing one pool's data to 1 point
- [x] 2.3 Handle failures: a failed pool row shows "unavailable", total failure shows an error with a retry button; verify by blocking one `/chart` URL and then going offline in DevTools → Network
- [x] 2.4 Refresh button re-runs loading and updates the "updated" time; verify the time changes and values reload

## 3. Detail chart and export

- [x] 3.1 Tapping a row expands a 90-day chart (supply line in `--accent`; borrow line from `history.csv`, dashed `--muted`, only when ≥ 2 recorded days); only one row open at a time; verify with a pool that has borrow history (or a temporary local `history.csv` with fake rows) and one without
- [x] 3.2 Export button downloads `stablecoin-rates-YYYY-MM-DD.csv` (date, platform, market, chain, asset, supply_apy, borrow_apy) merged by pool and date; verify the file opens in a spreadsheet, has rows for all 13 pools, and borrow is blank on days without history

## 4. Deploy and install

- [x] 4.1 Enable GitHub Pages (default branch, root) with `gh api` or repo settings, then push; verify `https://<user>.github.io/defi-parse/` loads with live data
- [x] 4.2 Install from Chrome/Edge on Windows and add to the home screen on a phone; verify it opens standalone with its name and icon. If Chrome offers no install, add PNG icons and/or a minimal service worker per design Risks and re-verify

## 5. App window and deposit links

- [x] 5.1 Add `url` to all 13 `watchlist.json` entries per design; render "Open in {platform} ↗" (`target="_blank" rel="noopener"`) in the expanded detail when present; verify `python test_defi_parser.py` still passes, each of the 13 links loads its pool page, and an entry without `url` shows no link
- [x] 5.2 Add `display_override: ["window-controls-overlay"]`, title-bar-area header styling with `app-region: drag`/`no-drag`, and the one-time `resizeTo(400, 760)` on first installed launch; verify in a normal tab nothing changes (no resize, same layout), Chrome still reports no installability errors, and after reinstalling on Windows the app opens at phone size with the header as its title bar

## Workflow follow-up

- Tune palette values after seeing them on a real phone in both themes.
- Archive the change after it is deployed and installed on both devices.
