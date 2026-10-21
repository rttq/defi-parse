# Design

## Context

See proposal.md (Why). Depends on `switch-to-defillama-api`, which provides `watchlist.json`, a daily `history.csv`, and the public GitHub repo. Verified 2026-10-21:

- `yields.llama.fi` sends `access-control-allow-origin: *`, so the browser can call it directly.
- `/chart/{pool}` returns the full daily history: 3 KB gzipped for a 5-month pool, 28 KB gzipped (1354 points since 2023-02) for the oldest Aave pool. All 13 pools together are a few hundred KB.
- `/pools` is 2.2 MB gzipped. It's too heavy to download on every open on a phone and isn't needed: the latest `/chart` point gives current supply APY and TVL.
- `/lendBorrow` is 168 KB gzipped and gives current borrow APY.

## Goals / Non-Goals

**Goals:**
- One static page, no build step, no backend, no JS dependencies.
- Feels like a small native utility on a phone and in a narrow desktop window.

**Non-Goals:**
- Offline mode or caching (data is only useful when fresh; no service worker unless installability needs one, see Risks).
- OS home-screen widgets or a real system-tray icon (both need native code).
- Push notifications or rate alerts.
- Editing the watchlist from the UI.

## Decisions

### Files and hosting
`index.html` (markup + inline CSS + inline JS), `manifest.webmanifest`, `icon.svg`, all at repo root. GitHub Pages deploys from the default branch, root, so the page, `watchlist.json` and `history.csv` share one origin and need no CORS. Every daily collector commit also redeploys Pages, so `history.csv` stays current.

Alternative considered: a `docs/` folder or a separate Pages branch. Rejected because the widget then can't fetch `../watchlist.json` from the same Pages site without copying it.

### Data loading on open/refresh
```
watchlist.json ------------------------------+
/chart/{id} x 13   (parallel, allSettled) ---+--> rows: current supply = last point,
/lendBorrow        (one call) ---------------+          sparkline = last 30 points,
history.csv        (same origin) ------------+          borrow now = lendBorrow,
                                                         borrow trend = history.csv
```
`Promise.allSettled` so one failed pool doesn't block the others (spec: partial failure). `history.csv` is fetched with `cache: "no-store"` so a fresh daily commit is picked up.

### Charts: hand-drawn inline SVG
Sparkline = one `<polyline>` scaled to min/max of the 30 points. Detail chart = two polylines (supply, borrow), min/max labels and start/end dates on the axes. No chart library: two line shapes don't justify a dependency, and inline SVG inherits `currentColor` and CSS variables for theming.

### Detail view
Tapping a row expands it in place (an accordion row) instead of navigating to a new page. That keeps a single page and needs no routing. Only one row is open at a time.

### CSV export
Built client-side. Supply rows come from the `/chart` data already loaded (full history, daily), merged with `borrow_apy` from `history.csv` by `(pool_id, date)`. The file downloads as `stablecoin-rates-YYYY-MM-DD.csv` via a `Blob` + `<a download>`.

### Design tokens
Inter from Google Fonts (`wght@400;500;600`), falling back to `system-ui, sans-serif`. Base `font: 0.875rem/1.5 Inter`. 16 px padding on page and row edges. Content `max-width: 420px`, centered. Numbers use `font-variant-numeric: tabular-nums` so columns of rates line up.

Proposed palette (the user gave token names; these values are a starting point to tune):

| Token | Role | Light | Dark |
|---|---|---|---|
| `--bg` | page background | `#f6f7f9` | `#0e0f12` |
| `--surface` | cards / row groups | `#ffffff` | `#17191d` |
| `--fg` | primary text, rates | `#111317` | `#eceef2` |
| `--soft` | secondary text (market, chain) | `#41454d` | `#b9bdc6` |
| `--muted` | tertiary (labels, timestamps) | `#7a7f89` | `#7d828c` |
| `--line` | dividers, sparkline baseline | `#e3e5e9` | `#262930` |
| `--accent` | supply line, refresh, focus | `#0f766e` | `#2dd4bf` |

The borrow line uses `--muted` (dashed), so supply stays the visual focus. Dark values sit under `@media (prefers-color-scheme: dark)` on `:root`.

### PWA manifest
`name: "Stablecoin Rates"`, `short_name: "Rates"`, `display: "standalone"`, `start_url: "./"`, `background_color`/`theme_color` from the light palette, icon `icon.svg` (`sizes: "any"`). Add `<meta name="theme-color">` per color scheme and `apple-touch-icon` for iOS.

## Risks / Trade-offs

- [Chrome's install prompt may require PNG icons or a service worker] → verified during apply. If it does, add 192/512 PNG icons and/or a minimal pass-through service worker, nothing more.
- [iOS does not support SVG for `apple-touch-icon`] → a 180 px PNG is needed for a nice iOS icon. Add it in the same step if missing.
- [14 requests per open] → small payloads, parallel. Acceptable on mobile data. If it feels slow, a later change can have the collector publish a prebuilt `latest.json`.
- [Borrow trend is empty at launch] → expected. It starts filling from the collector's first run, and the detail chart falls back to supply only.
- [GitHub Pages caches files for ~10 min] → `history.csv` may lag the daily commit by a few minutes. Irrelevant for daily data.
