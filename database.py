import sqlite3
from datetime import date, datetime

DB_PATH = "positions.db"


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker            TEXT    NOT NULL,
                shares            INTEGER NOT NULL,
                stock_entry_price REAL,
                call_strike       REAL    NOT NULL,
                call_expiry       TEXT    NOT NULL,
                premium_per_share REAL    NOT NULL,
                total_premium     REAL    NOT NULL,
                entry_date        TEXT    NOT NULL,
                status            TEXT    NOT NULL DEFAULT 'open',
                close_price       REAL,
                close_date        TEXT,
                notes             TEXT    DEFAULT ''
            )
            """
        )


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------

def add_position(
    ticker: str,
    shares: int,
    call_strike: float,
    call_expiry: str,
    premium_per_share: float,
    stock_entry_price: float | None = None,
    notes: str = "",
) -> int:
    total_premium = premium_per_share * shares
    with _conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO positions
                (ticker, shares, stock_entry_price, call_strike, call_expiry,
                 premium_per_share, total_premium, entry_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker.upper(),
                shares,
                stock_entry_price,
                call_strike,
                call_expiry,
                premium_per_share,
                total_premium,
                date.today().isoformat(),
                notes,
            ),
        )
        return cur.lastrowid


def close_position(position_id: int, close_price: float):
    with _conn() as conn:
        conn.execute(
            "UPDATE positions SET status='closed', close_price=?, close_date=? WHERE id=?",
            (close_price, date.today().isoformat(), position_id),
        )


def delete_position(position_id: int):
    with _conn() as conn:
        conn.execute("DELETE FROM positions WHERE id=?", (position_id,))


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------

def get_positions(status: str | None = None) -> list[dict]:
    with _conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM positions WHERE status=? ORDER BY call_expiry",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM positions ORDER BY status ASC, call_expiry ASC"
            ).fetchall()
        return [_enrich(dict(r)) for r in rows]


def _enrich(pos: dict) -> dict:
    """Add derived fields (DTE, ITM flag) without network calls."""
    if pos["call_expiry"]:
        expiry = datetime.strptime(pos["call_expiry"], "%Y-%m-%d").date()
        pos["dte"] = (expiry - date.today()).days
    else:
        pos["dte"] = None
    pos["itm"] = None  # filled in by frontend via /prices endpoint
    return pos


def get_summary() -> dict:
    with _conn() as conn:
        open_count = conn.execute(
            "SELECT COUNT(*) FROM positions WHERE status='open'"
        ).fetchone()[0]
        open_premium = conn.execute(
            "SELECT COALESCE(SUM(total_premium),0) FROM positions WHERE status='open'"
        ).fetchone()[0]
        closed_premium = conn.execute(
            "SELECT COALESCE(SUM(total_premium),0) FROM positions WHERE status='closed'"
        ).fetchone()[0]

    return {
        "open_positions": open_count,
        "open_premium": round(open_premium, 2),
        "closed_premium": round(closed_premium, 2),
        "total_premium_all_time": round(open_premium + closed_premium, 2),
    }
