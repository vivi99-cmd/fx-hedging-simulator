"""Parametric VaR and stress scenarios for an unhedged FX exposure."""
from math import sqrt

import config


def parametric_var(notional_usd: float, annual_vol: float, days_out: int, confidence: str = "95%") -> float:
    """
    One-tailed parametric VaR in USD: the loss that a normal-distribution
    model says should not be exceeded with the given confidence, over the
    exposure's horizon.
    """
    z = config.VAR_CONFIDENCE_Z[confidence]
    horizon_vol = annual_vol * sqrt(days_out / 365)
    return notional_usd * z * horizon_vol


def stress_scenarios(spot: float, notional_foreign: float, direction: str,
                      shocks_pct=None) -> list[dict]:
    """
    P&L impact (USD, relative to today's spot) of a set of rate shocks.

    direction: "payable" (must buy foreign currency later -- hurt by the
    foreign currency strengthening) or "receivable" (must sell foreign
    currency later -- hurt by it weakening).
    """
    shocks_pct = shocks_pct or config.STRESS_SHOCKS_PCT
    baseline_usd = notional_foreign * spot
    rows = []
    for shock in shocks_pct:
        shocked_spot = spot * (1 + shock)
        shocked_usd = notional_foreign * shocked_spot
        if direction == "payable":
            pnl = -(shocked_usd - baseline_usd)  # costs more USD = negative P&L
        else:
            pnl = shocked_usd - baseline_usd  # receive less USD = negative P&L
        rows.append({
            "shock_pct": shock,
            "shocked_spot": shocked_spot,
            "pnl_usd": pnl,
        })
    return rows
