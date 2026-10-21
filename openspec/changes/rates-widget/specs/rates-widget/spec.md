# Spec Delta

## Purpose

An installable, phone-sized web view that shows current supply and borrow rates for the watchlisted stablecoin pools and how those rates moved over time, usable on both desktop and mobile.

## ADDED Requirements

### Requirement: Shows current rates for every watchlisted pool
The widget SHALL show one row per watchlist pool, grouped by platform, with market, chain, asset and current supply APY. It SHALL show current borrow APY for pools that have one and SHALL show no borrow value for deposit-only pools.

#### Scenario: Normal open
- **WHEN** the widget is opened and the data source is healthy
- **THEN** 13 rows are shown under Kamino, Euler and Aave v3, each with a supply APY in percent

#### Scenario: Deposit-only vault
- **WHEN** the RockawayX RWA USDC row is shown
- **THEN** it has a supply APY and no borrow APY

### Requirement: Watchlist is read from the shared file
The widget SHALL take the pool list from the repository's watchlist file and SHALL NOT keep its own copy of pool ids.

#### Scenario: Pool added to the watchlist
- **WHEN** a new entry is added to the watchlist file and the page is reloaded
- **THEN** the new pool appears as a row without any change to the widget's code

### Requirement: Supply trend per row
Each row SHALL show a sparkline of the pool's daily supply APY for the last 30 days, using the data source's free per-pool history.

#### Scenario: Pool with long history
- **WHEN** a pool has more than 30 days of history
- **THEN** its sparkline covers the last 30 days only

#### Scenario: Pool with short history
- **WHEN** a pool has fewer than 2 days of history
- **THEN** no sparkline is drawn for that row and the current value is still shown

### Requirement: Detail chart with borrow trend
Selecting a row SHALL open a chart of the last 90 days of supply APY for that pool. When the recorded history file has at least 2 days of borrow APY for that pool, the chart SHALL also show borrow APY over the same period.

#### Scenario: Borrow history available
- **WHEN** the user selects Euler eUSDC-2 and the history file has 10 days of its borrow APY
- **THEN** the chart shows the supply line for 90 days and the borrow line for those 10 days

#### Scenario: No borrow history yet
- **WHEN** the user selects a pool with fewer than 2 recorded borrow days
- **THEN** the chart shows the supply line only

### Requirement: Live refresh with timestamp
The widget SHALL fetch data when opened and when the user presses refresh, and SHALL show the local time of the last successful update.

#### Scenario: Manual refresh
- **WHEN** the user presses refresh
- **THEN** values are re-fetched and the "updated" time changes to the current time

### Requirement: Partial failure is visible
If data for some pools cannot be loaded, the widget SHALL still show the rows it could load and SHALL mark the failed rows. If nothing can be loaded, it SHALL show an error message with a retry action.

#### Scenario: One pool's history fails
- **WHEN** the history request for one pool fails and the others succeed
- **THEN** 12 rows render normally and the failed row shows an "unavailable" marker

#### Scenario: Offline
- **WHEN** the device has no network connection
- **THEN** an error message with a retry button is shown instead of an empty list

### Requirement: CSV export of history
The widget SHALL let the user download a CSV with one row per pool per day: date, platform, market, chain, asset, supply APY and borrow APY. Borrow APY SHALL be empty on days without a recorded value.

#### Scenario: Export
- **WHEN** the user presses export
- **THEN** a CSV file downloads containing daily rows for all 13 pools

### Requirement: Installable on desktop and phone
The widget SHALL be served over HTTPS and SHALL be installable as a standalone app with its own name and icon from Chromium-based desktop browsers and from mobile home-screen "add" flows.

#### Scenario: Desktop install
- **WHEN** the user installs it from Chrome or Edge on Windows
- **THEN** it opens in its own window without browser UI and can be pinned to the taskbar

#### Scenario: Phone install
- **WHEN** the user adds it to the home screen on Android or iOS
- **THEN** it launches full-screen from its icon

### Requirement: Installed desktop window looks like an app
When installed and opened as a desktop app, the widget SHALL draw its own title bar (its header, draggable, with the system window buttons) instead of the browser's frame where the browser supports it. On the first launch as an installed app it SHALL size its window to phone proportions. Later launches SHALL keep the size the user chose.

#### Scenario: First launch on Windows
- **WHEN** the user opens the installed app for the first time in Chrome or Edge
- **THEN** the window is about 400×760 px and shows no browser title bar, only the widget header with the system minimize/maximize/close buttons

#### Scenario: User resized the window
- **WHEN** the user resizes the window and reopens the app
- **THEN** it opens at the user's size, not 400×760

#### Scenario: Opened in a normal browser tab
- **WHEN** the page is opened in a regular tab
- **THEN** no window resizing happens and the layout is unchanged

### Requirement: Link to the pool's deposit page
Each pool's expanded detail SHALL include a link that opens that pool's deposit page on the lending protocol in a new tab or the system browser. The link target SHALL come from the shared watchlist file.

#### Scenario: Open Kamino pool
- **WHEN** the user expands the Kamino JLP Market USDC row and follows its link
- **THEN** the Kamino USDC reserve page of the JLP Market opens

#### Scenario: Pool without a link
- **WHEN** a watchlist entry has no link
- **THEN** its detail shows no link and nothing else changes

### Requirement: Phone-first layout
The layout SHALL be designed for a 360 px wide viewport with 16 px side padding, SHALL have no horizontal scrolling down to 320 px, and SHALL cap its content width on wide screens instead of stretching.

#### Scenario: Small phone
- **WHEN** the widget is viewed at 320 px width
- **THEN** all row values are visible without horizontal scrolling

#### Scenario: Desktop browser tab
- **WHEN** the widget is opened in a 1920 px wide window
- **THEN** content stays in a narrow centered column

### Requirement: Follows system light/dark theme
The widget SHALL use a light palette by default and a dark palette when the system prefers dark, both defined through the same set of color tokens.

#### Scenario: Dark mode
- **WHEN** the operating system is set to dark mode
- **THEN** the widget renders with the dark palette without a reload
