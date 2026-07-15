"""Vanilla FX option pricing via Garman-Kohlhagen (Black-Scholes for FX)."""
from math import exp, log, sqrt

from scipy.stats import norm


def _d1_d2(spot, strike, r_domestic, r_foreign, sigma, t):
    d1 = (log(spot / strike) + (r_domestic - r_foreign + 0.5 * sigma ** 2) * t) / (sigma * sqrt(t))
    d2 = d1 - sigma * sqrt(t)
    return d1, d2


def call_price(spot: float, strike: float, r_domestic: float, r_foreign: float,
                sigma: float, days_out: int) -> float:
    """Price (in USD per unit of foreign currency) of a call on the foreign currency."""
    t = days_out / 365
    d1, d2 = _d1_d2(spot, strike, r_domestic, r_foreign, sigma, t)
    return spot * exp(-r_foreign * t) * norm.cdf(d1) - strike * exp(-r_domestic * t) * norm.cdf(d2)


def put_price(spot: float, strike: float, r_domestic: float, r_foreign: float,
               sigma: float, days_out: int) -> float:
    """Price (in USD per unit of foreign currency) of a put on the foreign currency."""
    t = days_out / 365
    d1, d2 = _d1_d2(spot, strike, r_domestic, r_foreign, sigma, t)
    return strike * exp(-r_domestic * t) * norm.cdf(-d2) - spot * exp(-r_foreign * t) * norm.cdf(-d1)
