"""Spot rates and historical volatility for the supported FX pairs."""
import numpy as np
import yfinance as yf

import config


def get_spot_rate(currency: str) -> float:
    """USD per 1 unit of `currency`."""
    ticker = config.PAIRS[currency]["yf_ticker"]
    hist = yf.Ticker(ticker).history(period="5d")
    if hist.empty:
        raise ValueError(f"No spot data returned for {ticker}")
    return float(hist["Close"].iloc[-1])


def get_annualized_volatility(currency: str, lookback_days: int = None) -> float:
    """Annualized volatility of daily log returns over the lookback window."""
    lookback_days = lookback_days or config.VOL_LOOKBACK_DAYS
    ticker = config.PAIRS[currency]["yf_ticker"]
    hist = yf.Ticker(ticker).history(period=f"{lookback_days + 10}d")
    if len(hist) < 20:
        raise ValueError(f"Not enough history for {ticker} to estimate volatility")
    closes = hist["Close"].tail(lookback_days + 1)
    log_returns = np.log(closes / closes.shift(1)).dropna()
    daily_vol = log_returns.std()
    return float(daily_vol * np.sqrt(252))


def get_market_snapshot(currency: str) -> dict:
    return {
        "currency": currency,
        "spot": get_spot_rate(currency),
        "annual_vol": get_annualized_volatility(currency),
    }
