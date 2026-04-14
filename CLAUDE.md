# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working with this repository.

## Project Overview

- **Purpose**: Covered Call Dashboard — screen options opportunities and track positions
- **Language/Runtime**: Python 3.11+
- **Framework**: FastAPI + Jinja2 templates
- **Data**: Yahoo Finance via `yfinance` (US + European markets)
- **Storage**: SQLite (`positions.db`, created automatically on first run)

## Repository Structure

```
Claude-/
├── app.py              # FastAPI application — routes and entry point
├── screener.py         # Options screening logic (IV rank, yield calc)
├── database.py         # SQLite position tracking (CRUD)
├── requirements.txt    # Python dependencies
├── positions.db        # SQLite database (auto-created, not committed)
├── templates/
│   └── index.html      # Web dashboard (Tailwind CSS + vanilla JS)
└── CLAUDE.md           # This file
```

## Development Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the development server
python app.py
# → Open http://localhost:8000
```

## Common Commands

| Command | Description |
|---|---|
| `python app.py` | Start dev server on port 8000 with auto-reload |
| `uvicorn app:app --reload` | Alternative start command |

## How It Works

### Screener (`screener.py`)
- Accepts a comma-separated list of tickers (US: `AAPL`, European: `AIR.PA`, `NOVO-B.CO`)
- Fetches options chains via `yfinance`
- Filters for OTM calls within the requested DTE window (default 21–45 days)
- Calculates: premium yield, annualised yield, OTM%, breakeven, IV, IV rank
- Returns top 3 candidates per ticker sorted by annualised yield

### Position Tracker (`database.py`)
- SQLite-backed CRUD for open/closed covered call positions
- Tracks: ticker, shares, stock entry price, call strike, expiry, premium collected
- Derived fields: DTE (calculated), ITM status (enriched via live prices)

### Dashboard (`templates/index.html`)
- Summary cards: open positions, premium collected (open/closed/total)
- Screener form → results table
- Position management: add, close, delete
- Live prices fetched asynchronously after page load; refreshed every 5 minutes

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Dashboard HTML |
| `POST` | `/api/screen` | Run screener (`tickers`, `dte_min`, `dte_max`) |
| `GET` | `/api/positions` | List all positions |
| `POST` | `/api/positions` | Add a position |
| `POST` | `/api/positions/{id}/close` | Close a position (`close_price`) |
| `DELETE` | `/api/positions/{id}` | Delete a position |
| `GET` | `/api/prices?tickers=A,B` | Fetch current prices for tickers |
| `GET` | `/api/summary` | Summary stats |

## Development Workflow

### Branching Convention

- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`
- Claude-managed branches: `claude/<task-description>-<id>`
- Main branch: `main` (protected — do not push directly)

### Commit Messages

Write concise, imperative commit messages:
```
Add covered call screener with IV rank calculation
Fix DTE calculation for European market timezones
Update dashboard to show annualised yield column
```

### Pull Requests

- Keep PRs focused on a single concern
- Include a short description of what changed and why

## Code Conventions

- Python type hints on all function signatures
- `snake_case` for Python variables, functions, and files
- Keep functions small and single-purpose
- No ORM — raw SQLite via `sqlite3` is sufficient for this use case
- Frontend: vanilla JS + Tailwind CSS (no build step required)

## Known Limitations & Future Work

- **European options**: `yfinance` has limited options data for European stocks — screener works best for US markets
- **IBKR integration**: Live trading and real-time data via Interactive Brokers TWS API can be added using `ib_insync`
- **Historical IV**: IV rank is approximated from realised volatility, not true historical implied volatility
- **No authentication**: Dashboard has no login — run locally or add auth before exposing publicly
- **Portfolio P&L**: Stock-side P&L tracking requires adding a position entry price field (partially implemented)

## AI Assistant Guidelines

When working in this repository:

1. **Read before editing** — always read a file before modifying it
2. **Minimal changes** — make only the changes needed to fulfil the task
3. **No speculative features** — do not add code for hypothetical future requirements
4. **Security first** — never introduce SQL injection, XSS, or command injection vulnerabilities
5. **Commit and push** — after completing a task, commit with a clear message and push to the designated branch
6. **Update this file** — whenever the project structure, tooling, or conventions change, update CLAUDE.md
