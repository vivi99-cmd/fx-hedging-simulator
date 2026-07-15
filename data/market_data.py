"""Spot rates and historical volatility for the supported FX pairs.

Cached and rate-limit-tolerant: Streamlit Cloud shares egress IPs across
many deployed apps, and Yahoo Finance rate-limits those IPs more
aggressively than a home connection. A bare st.cache_data(ttl=...) also
fixes the bigger issue underneath that: every widget interaction triggers a
full Streamlit rerun, and without caching that meant a fresh yfinance
request per rerun even when nothing about the currency changed.
"""
import time

import numpy as np
import streamlit as st
import yfinance as yf

import config


def _fetch_history(ticker: str, days: int):
    last_error = None
    for attempt in range(3):
        hist = yf.Ticker(ticker).history(period=f"{days}d")
        if not hist.empty:
            return hist
        last_error = ValueError(f"No data returned for {ticker}")
        time.sleep(2 ** attempt)  # 1s, 2s, 4s backoff for transient rate limits
    raise last_error


@st.cache_data(ttl=900, show_spinner="Fetching market data...")
def get_market_snapshot(currency: str) -> dict:
    ticker = config.PAIRS[currency]["yf_ticker"]
    lookback_days = config.VOL_LOOKBACK_DAYS
    hist = _fetch_history(ticker, lookback_days + 10)
    if len(hist) < 20:
        raise ValueError(f"Not enough history for {ticker} to estimate volatility")

    spot = float(hist["Close"].iloc[-1])
    closes = hist["Close"].tail(lookback_days + 1)
    log_returns = np.log(closes / closes.shift(1)).dropna()
    annual_vol = float(log_returns.std() * np.sqrt(252))

    return {"currency": currency, "spot": spot, "annual_vol": annual_vol}
