# Spec Delta

## Purpose

Collects USDC/USDT supply and borrow rates for a fixed watchlist of DeFi lending pools (Kamino, Euler, Aave) once a day and keeps them as an append-only history, so rate trends can be shown later.

## ADDED Requirements

### Requirement: Watchlist defines which pools are recorded
The system SHALL record exactly the pools on its watchlist. Each watchlist entry SHALL identify one pool by its stable source id and carry a human-readable platform, market, chain and asset label. Pools not on the watchlist SHALL NOT be recorded, even if they hold USDC or USDT.

#### Scenario: Watchlisted pool is recorded
- **WHEN** a run completes and the source returns the Kamino JLP Market USDC pool
- **THEN** the history gains one row for it labelled platform `Kamino`, market `JLP Market`, chain `Solana`, asset `USDC`

#### Scenario: Similar but unlisted pool is excluded
- **WHEN** the source also returns an Euler `eUSDC-2` vault on Arbitrum, or an Aave `SYRUPUSDT` pool on Ethereum
- **THEN** no row for that pool is recorded

#### Scenario: Asset label is normalized
- **WHEN** the source names the Arbitrum Aave USDT pool `USD₮0`
- **THEN** its row shows asset `USDT`

### Requirement: Watchlist is shared data
The watchlist SHALL be stored as a data file in the repository, separate from code, so that other consumers (the rates widget) read the same list.

#### Scenario: Adding a pool
- **WHEN** a new entry is added to the watchlist file
- **THEN** the next collector run records it without any code change

### Requirement: Initial watchlist content
The watchlist SHALL contain: Kamino (Solana) JLP Market USDC and USDT, SOL/BTC Market USDC and USDT, the RockawayX RWA USDC vault; Euler v2 (Ethereum) eUSDC-2 and eUSDT-2; Aave v3 core market USDC and USDT on Ethereum, USDC and USDT on Arbitrum, and USDC and USDT on Avalanche.

#### Scenario: Full run against a healthy source
- **WHEN** the source returns every watchlisted pool
- **THEN** the run records 13 rows: 5 Kamino, 2 Euler, 6 Aave

### Requirement: Rates come from a public data API
The system SHALL obtain all rates and amounts from a public HTTP JSON API without rendering web pages, running a browser, or disabling TLS certificate verification.

#### Scenario: No browser needed
- **WHEN** the collector runs on a machine without Chrome installed
- **THEN** it completes and records the rows

### Requirement: Recorded fields are numeric
Each row SHALL contain the UTC date, pool id, platform, market, chain, asset, supply APY (%), borrow APY (%), max LTV (%), total supplied (USD) and total borrowed (USD). Rates and amounts SHALL be numbers. A field the source does not provide for that pool SHALL be empty, not a placeholder string.

#### Scenario: Lending market pool
- **WHEN** the source provides supply and borrow data for the Euler eUSDC-2 vault
- **THEN** its row has numeric supply APY, borrow APY, total supplied and total borrowed

#### Scenario: Deposit-only vault
- **WHEN** the RockawayX RWA USDC vault has no borrow data
- **THEN** its borrow APY, LTV and total borrowed fields are empty and its supply APY is numeric

### Requirement: History is append-only with one row per pool per day
The system SHALL append each run's rows to `history.csv` in the directory that contains the tool, regardless of the current working directory. Rows from earlier dates SHALL never be changed. A run on a date that already has rows SHALL replace that date's rows, so each pool has at most one row per UTC date.

#### Scenario: First run of the day
- **WHEN** `history.csv` holds rows up to yesterday and the collector runs
- **THEN** 13 rows dated today are appended and all earlier rows are unchanged

#### Scenario: Second run on the same day
- **WHEN** the collector runs again on the same UTC date
- **THEN** today's rows are replaced with the new values and the file still has 13 rows for today

#### Scenario: Run from another folder
- **WHEN** the collector is started from `C:\code` while it lives in `defi-parse\`
- **THEN** `defi-parse\history.csv` is updated and nothing is written to `C:\code`

### Requirement: Missing watchlist pools are reported
When a watchlisted pool is absent from the source response, the system SHALL print a warning that names that pool and SHALL still record rows for every pool that was found. In GitHub Actions the warning SHALL appear as a run annotation.

#### Scenario: One pool disappears upstream
- **WHEN** the source response does not contain the Euler eUSDT-2 pool
- **THEN** a warning naming `Euler eUSDT-2` is shown, and the other 12 rows are recorded

### Requirement: Source failure does not corrupt history
If the source cannot be reached or returns an HTTP error, the system SHALL print an error, SHALL exit with a non-zero exit code, and SHALL NOT modify `history.csv`.

#### Scenario: API unreachable
- **WHEN** the API request times out
- **THEN** an error is printed, the exit code is non-zero, and `history.csv` is unchanged

### Requirement: Collector runs daily without manual action
The repository SHALL run the collector once per day on a schedule and SHALL commit the updated `history.csv` back to the default branch. It SHALL also allow a manual run. A failed run SHALL show as failed in GitHub Actions and SHALL NOT commit.

#### Scenario: Scheduled run
- **WHEN** the daily schedule fires and the source is healthy
- **THEN** a commit updating `history.csv` with today's rows appears on the default branch

#### Scenario: Failed scheduled run
- **WHEN** the daily schedule fires and the source returns an HTTP error
- **THEN** the run is marked failed and no commit is made
