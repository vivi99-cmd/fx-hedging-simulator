# Major pairs vs USD. yf_ticker follows yfinance's convention: EURUSD=X
# quotes USD per 1 unit of the foreign currency (i.e. foreign currency is
# the base, USD is the quote).
PAIRS = {
    "EUR": {"yf_ticker": "EURUSD=X", "name": "Euro"},
    "GBP": {"yf_ticker": "GBPUSD=X", "name": "British Pound"},
    "JPY": {"yf_ticker": "JPYUSD=X", "name": "Japanese Yen"},
    "CAD": {"yf_ticker": "CADUSD=X", "name": "Canadian Dollar"},
    "AUD": {"yf_ticker": "AUDUSD=X", "name": "Australian Dollar"},
}

HOME_CURRENCY = "USD"

# Approximate short-term policy rates, used for forward pricing (covered
# interest rate parity) and option pricing (Garman-Kohlhagen). These drift
# with central bank decisions -- treat as a placeholder to refresh
# periodically (e.g. from FRED or each central bank's site), not a live feed.
REFERENCE_RATES = {
    "USD": 0.0425,
    "EUR": 0.0215,
    "GBP": 0.0425,
    "JPY": 0.005,
    "CAD": 0.0275,
    "AUD": 0.0385,
}

# Trading-day lookback for the annualized volatility estimate used in VaR
# and option pricing.
VOL_LOOKBACK_DAYS = 252

# One-tailed z-scores for parametric VaR.
VAR_CONFIDENCE_Z = {
    "95%": 1.645,
    "99%": 2.326,
}

STRESS_SHOCKS_PCT = [-0.10, -0.05, 0.05, 0.10]
