# Tasks

## 1. Collector

- [x] 1.1 Remove the Selenium-based `get_kamino_rates`, `get_euler_finance_rates` and the old `get_defillama_yields`, plus the `selenium`/`webdriver_manager`/`time`/`traceback` imports; verify `python -c "import ast; ast.parse(open('defi_parser.py', encoding='utf-8').read())"` succeeds and `grep -i selenium defi_parser.py` finds nothing
- [x] 1.2 Create `watchlist.json` with the 13 entries from design.md; verify it parses and has 13 unique ids
- [x] 1.3 Fetch `/pools` and `/lendBorrow` with `requests` (timeout, `raise_for_status`) and build today's rows by joining on pool id per the design column mapping; numbers stay numbers, missing values become empty; print `::warning::Missing pool: …` for each watchlist entry not found
- [x] 1.4 Append to `history.csv` next to the script (`Path(__file__).with_name`), replacing rows with today's date if present, and print today's table grouped by platform; verify by running twice from a different folder: `defi-parse\history.csv` has exactly 13 rows for today and nothing is written to the current folder
- [x] 1.5 Add `test_defi_parser.py` with plain asserts on the row-building and history-merge functions using small fake `/pools` + `/lendBorrow` dicts, covering: lending pool (all fields numeric, LTV 0.8 → 80), deposit-only vault (borrow/LTV/total borrow empty, total supply from `tvlUsd`), missing pool (warning, other rows kept), `USD₮0` labelled `USDT`, unlisted pool excluded, same-day re-run replaces only today's rows and keeps earlier dates; verify `python test_defi_parser.py` exits 0
- [x] 1.6 Make source errors exit non-zero before any file write (no catch-all wrapper); verify by pointing the URL at an unreachable host once, confirming non-zero exit and an unchanged `history.csv` hash, then revert
- [x] 1.7 Run `python defi_parser.py` against the live API; verify 13 rows for today, no warnings, numeric APY columns, and spot-check two values against kamino.com and app.euler.finance

## 2. Repository and daily job

- [x] 2.1 `git init`, add `.gitignore` (`__pycache__/`, `defi_rates.csv`, `Claude-DeFi*.json` unless the user opts in to publishing the chat export); verify `git status` lists only the intended files
- [x] 2.2 Add `.github/workflows/collect.yml` per design (daily cron + `workflow_dispatch`, `contents: write`, commit only on success and only if `history.csv` changed); verify the YAML parses
- [x] 2.3 Confirm with the user, then create the public GitHub repo with `gh repo create defi-parse --public` and push; verify the repo page shows the files
- [x] 2.4 Trigger the workflow once with `gh workflow run collect.yml`; verify the run succeeds and a bot commit adds today's rows to `history.csv`

## Workflow follow-up

- Check after the first week that daily commits keep appearing (cron is running and not disabled).
- Archive the change after it is applied and the first scheduled run has succeeded.
