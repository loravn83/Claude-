from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yfinance as yf
import uvicorn

import database as db
from screener import screen_tickers

app = FastAPI(title="Covered Call Dashboard")
templates = Jinja2Templates(directory="templates")

db.init_db()


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    positions = db.get_positions()
    summary = db.get_summary()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "positions": positions, "summary": summary},
    )


# ---------------------------------------------------------------------------
# Screener
# ---------------------------------------------------------------------------

@app.post("/api/screen")
async def screen(
    tickers: str = Form(...),
    dte_min: int = Form(21),
    dte_max: int = Form(45),
):
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not symbols:
        raise HTTPException(status_code=400, detail="No tickers provided")
    return screen_tickers(symbols, dte_min, dte_max)


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------

@app.post("/api/positions")
async def add_position(
    ticker: str = Form(...),
    shares: int = Form(...),
    call_strike: float = Form(...),
    call_expiry: str = Form(...),
    premium_per_share: float = Form(...),
    stock_entry_price: float = Form(None),
    notes: str = Form(""),
):
    position_id = db.add_position(
        ticker, shares, call_strike, call_expiry,
        premium_per_share, stock_entry_price, notes,
    )
    return {"id": position_id, "status": "created"}


@app.post("/api/positions/{position_id}/close")
async def close_position(position_id: int, close_price: float = Form(...)):
    db.close_position(position_id, close_price)
    return {"status": "closed"}


@app.delete("/api/positions/{position_id}")
async def delete_position(position_id: int):
    db.delete_position(position_id)
    return {"status": "deleted"}


@app.get("/api/positions")
async def list_positions(status: str | None = None):
    return db.get_positions(status)


@app.get("/api/summary")
async def summary():
    return db.get_summary()


# ---------------------------------------------------------------------------
# Live prices for open positions (called from frontend)
# ---------------------------------------------------------------------------

@app.get("/api/prices")
async def get_prices(tickers: str):
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                prices[symbol] = round(float(hist["Close"].iloc[-1]), 2)
        except Exception:
            pass
    return prices


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
