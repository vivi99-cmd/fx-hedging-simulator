# FX Exposure & Hedging Simulator

A tool that models the FX hedging decision a corporate treasurer actually
faces: a company has a future foreign-currency payment or receipt, and needs
to decide whether to hedge it, and how.

**The problem it addresses**: any company with cross-border cash flow (an
importer paying overseas suppliers, an exporter billing overseas customers)
is exposed to currency risk between now and when that cash actually moves.
Firms like Kantox, HedgeFlows, and the FX desks of every major bank sell
tools and advisory services built around exactly this decision. This is a
simplified version of that decision-support layer.

## What it does

Given a foreign-currency exposure (currency, amount, payable/receivable,
days until settlement) and a risk tolerance, it:

1. **Quantifies unhedged risk** — parametric Value at Risk over the exposure's
   horizon, plus a stress table showing P&L impact under ±5%/±10% rate moves.
2. **Prices two hedge instruments** — a forward contract (via covered
   interest rate parity) and an at-the-money vanilla option (via the
   Garman-Kohlhagen model, the standard Black-Scholes variant for FX), and
   compares both against doing nothing.
3. **Recommends a hedge ratio** — the minimum fraction of the exposure to
   hedge with a forward to bring VaR down to the stated risk tolerance.

## Run it

```bash
cd workflows/fx-hedging-tool
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Pick a currency, enter an exposure, and
the risk/hedge numbers update live using real spot rates and volatility
pulled from Yahoo Finance.

## Methodology

- **Spot rates & volatility**: pulled live via `yfinance`. Volatility is the
  annualized standard deviation of daily log returns over a trailing
  252-trading-day window.
- **Forward pricing**: covered interest rate parity,
  `F = S * (1 + r_domestic*T) / (1 + r_foreign*T)`, using the reference
  rates in `config.py`.
- **Option pricing**: Garman-Kohlhagen (FX-adjusted Black-Scholes). Payables
  are hedged with a call (right to buy the foreign currency); receivables
  with a put (right to sell it). Strike is set at-the-money (today's spot)
  as the simplest baseline structure — a real desk would quote multiple
  strikes.
- **VaR**: parametric (variance-covariance) method, assumes normally
  distributed returns. This understates tail risk relative to FX's actual
  fat-tailed distribution — a known simplification, not a claim that FX
  returns are normal.
- **Hedge ratio recommendation**: a simple rule, not a real optimization —
  hedges just enough notional via forward to bring VaR down to the risk
  tolerance, assuming VaR scales linearly with hedged fraction (true for a
  forward, since it removes that fraction of the exposure outright).

## Known limitations (things a production version would need)

- **Reference interest rates are static placeholders** in `config.py`, not
  a live feed (e.g. FRED or a central bank API). They drift with policy
  decisions and should be refreshed periodically.
- **Parametric VaR assumes normal returns.** FX returns have fatter tails,
  especially around central bank surprises — a production tool would use
  historical simulation or a fat-tailed distribution.
- **Only vanilla, at-the-money options are priced.** Real corporate hedging
  programs use custom strikes, collars, and participating forwards.
- **No bid/ask spread or dealer margin** is modeled on the forward or
  option — quoted prices are the theoretical mid, not what a bank would
  actually quote.
- **Single exposure at a time.** A real treasury tool would net exposures
  across multiple currencies and settlement dates before hedging.

This is an educational model built to demonstrate the mechanics of
corporate FX risk management — not a pricing engine to size real trades on.

## Project structure

```
config.py           currency pairs, reference rates, VaR/stress parameters
data/market_data.py  spot rates + historical volatility (yfinance)
pricing/forward.py   covered interest rate parity
pricing/options.py   Garman-Kohlhagen call/put pricing
risk/var.py          parametric VaR + stress scenarios
risk/recommend.py    strategy comparison + hedge ratio recommendation
app.py               Streamlit UI
```
