"""Compares unhedged / forward / option strategies and suggests a hedge ratio."""
import config
from pricing.forward import forward_rate
from pricing.options import call_price, put_price


def compare_strategies(currency: str, notional_foreign: float, direction: str,
                        days_out: int, spot: float, annual_vol: float) -> dict:
    r_domestic = config.REFERENCE_RATES[config.HOME_CURRENCY]
    r_foreign = config.REFERENCE_RATES[currency]

    fwd_rate = forward_rate(spot, r_domestic, r_foreign, days_out)
    forward_locked_usd = notional_foreign * fwd_rate

    # Payable -> hedge with a call (right to buy foreign currency at strike).
    # Receivable -> hedge with a put (right to sell foreign currency at strike).
    # Strike = today's spot (at-the-money), the simplest baseline structure.
    strike = spot
    if direction == "payable":
        premium_per_unit = call_price(spot, strike, r_domestic, r_foreign, annual_vol, days_out)
        option_worst_case_usd = notional_foreign * strike + notional_foreign * premium_per_unit
    else:
        premium_per_unit = put_price(spot, strike, r_domestic, r_foreign, annual_vol, days_out)
        option_worst_case_usd = notional_foreign * strike - notional_foreign * premium_per_unit

    option_premium_usd = notional_foreign * premium_per_unit
    unhedged_baseline_usd = notional_foreign * spot

    return {
        "unhedged_baseline_usd": unhedged_baseline_usd,
        "forward_rate": fwd_rate,
        "forward_locked_usd": forward_locked_usd,
        "option_strike": strike,
        "option_premium_usd": option_premium_usd,
        "option_worst_case_usd": option_worst_case_usd,
    }


def recommend_hedge_ratio(unhedged_var_usd: float, risk_tolerance_usd: float) -> float:
    """
    Simplest workable rule: hedge enough of the exposure to bring VaR down
    to the stated risk tolerance. Assumes VaR scales linearly with the
    hedged fraction (true for a forward, since it removes that fraction of
    the exposure outright).
    """
    if unhedged_var_usd <= 0:
        return 0.0
    ratio = 1 - (risk_tolerance_usd / unhedged_var_usd)
    return max(0.0, min(1.0, ratio))
