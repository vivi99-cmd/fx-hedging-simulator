"""Forward FX rates via covered interest rate parity."""


def forward_rate(spot: float, r_domestic: float, r_foreign: float, days_out: int) -> float:
    """
    Forward rate (USD per 1 unit of foreign currency), simple-interest CIP.

    spot: USD per 1 unit of foreign currency
    r_domestic: USD reference rate
    r_foreign: foreign currency reference rate
    days_out: settlement horizon in days
    """
    t = days_out / 365
    return spot * (1 + r_domestic * t) / (1 + r_foreign * t)
