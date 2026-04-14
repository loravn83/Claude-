import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date


def get_iv_rank(ticker_obj, current_iv: float) -> float | None:
    """
    Approximate IV rank by comparing current IV against the range of
    30-day rolling realised volatility over the past year.
    """
    try:
        hist = ticker_obj.history(period="1y")
        if hist.empty or len(hist) < 30:
            return None
        returns = hist["Close"].pct_change().dropna()
        rolling_vol = returns.rolling(30).std() * np.sqrt(252) * 100
        vol_min = rolling_vol.min()
        vol_max = rolling_vol.max()
        if vol_max == vol_min:
            return 50.0
        iv_rank = (current_iv - vol_min) / (vol_max - vol_min) * 100
        return round(float(np.clip(iv_rank, 0, 100)), 1)
    except Exception:
        return None


def _get_current_price(ticker_obj) -> float | None:
    info = ticker_obj.info
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if price:
        return float(price)
    hist = ticker_obj.history(period="2d")
    if not hist.empty:
        return float(hist["Close"].iloc[-1])
    return None


def screen_ticker(symbol: str, dte_min: int = 21, dte_max: int = 45) -> list[dict]:
    """
    Return up to 3 covered call candidates for a single ticker.
    Works for US tickers and European tickers with suffix (e.g. NOVO-B.CO, AIR.PA).
    """
    try:
        ticker = yf.Ticker(symbol)
        current_price = _get_current_price(ticker)
        if not current_price:
            return []

        expiries = ticker.options
        if not expiries:
            return []

        today = date.today()
        candidates = []

        for expiry_str in expiries:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            dte = (expiry_date - today).days
            if dte < dte_min or dte > dte_max:
                continue

            chain = ticker.option_chain(expiry_str)
            calls = chain.calls
            if calls.empty:
                continue

            # OTM range: 0% to +15% above current price
            calls = calls[
                (calls["strike"] >= current_price * 1.00)
                & (calls["strike"] <= current_price * 1.15)
            ].copy()

            # Require some liquidity
            calls = calls[calls["volume"].fillna(0) > 0]
            if calls.empty:
                continue

            for _, row in calls.iterrows():
                bid = row.get("bid", 0) or 0
                ask = row.get("ask", 0) or 0
                last = row.get("lastPrice", 0) or 0
                premium = (bid + ask) / 2 if bid > 0 and ask > 0 else last
                if premium <= 0:
                    continue

                strike = float(row["strike"])
                iv = float(row.get("impliedVolatility", 0) or 0) * 100
                volume = int(row["volume"]) if pd.notna(row.get("volume")) else 0
                oi = int(row["openInterest"]) if pd.notna(row.get("openInterest")) else 0

                yield_pct = (premium / current_price) * 100
                annualised_yield = yield_pct * (365 / dte)
                otm_pct = ((strike - current_price) / current_price) * 100
                breakeven = current_price - premium

                iv_rank = get_iv_rank(ticker, iv)

                candidates.append(
                    {
                        "ticker": symbol,
                        "price": round(current_price, 2),
                        "strike": round(strike, 2),
                        "expiry": expiry_str,
                        "dte": dte,
                        "premium": round(premium, 2),
                        "yield_pct": round(yield_pct, 2),
                        "annualised_yield": round(annualised_yield, 1),
                        "otm_pct": round(otm_pct, 1),
                        "breakeven": round(breakeven, 2),
                        "iv": round(iv, 1),
                        "iv_rank": iv_rank,
                        "volume": volume,
                        "open_interest": oi,
                    }
                )

        candidates.sort(key=lambda x: x["annualised_yield"], reverse=True)
        return candidates[:3]

    except Exception:
        return []


def screen_tickers(symbols: list[str], dte_min: int = 21, dte_max: int = 45) -> dict:
    all_results = []
    errors = []

    for symbol in symbols:
        results = screen_ticker(symbol, dte_min, dte_max)
        if results:
            all_results.extend(results)
        else:
            errors.append(symbol)

    all_results.sort(key=lambda x: x["annualised_yield"], reverse=True)

    return {
        "results": all_results,
        "errors": errors,
        "count": len(all_results),
    }
