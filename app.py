import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config
from data.market_data import get_market_snapshot
from risk.recommend import compare_strategies, recommend_hedge_ratio
from risk.var import parametric_var, stress_scenarios

st.set_page_config(page_title="FX Exposure & Hedging Simulator", layout="wide")

st.title("FX Exposure & Hedging Simulator")
st.caption(
    "Model a company's foreign-currency exposure and compare doing nothing "
    "vs. hedging with a forward contract vs. hedging with an option."
)

with st.sidebar:
    st.header("Exposure")
    currency = st.selectbox(
        "Foreign currency",
        options=list(config.PAIRS.keys()),
        format_func=lambda c: f"{c} - {config.PAIRS[c]['name']}",
    )
    direction = st.radio(
        "Exposure type",
        options=["payable", "receivable"],
        format_func=lambda d: "Payable (we owe foreign currency)" if d == "payable"
        else "Receivable (we're owed foreign currency)",
    )
    notional_foreign = st.number_input(
        f"Notional ({currency})", min_value=1_000.0, value=500_000.0, step=10_000.0
    )
    days_out = st.slider("Days until settlement", min_value=7, max_value=365, value=90)
    st.header("Risk tolerance")
    risk_tolerance_pct = st.slider(
        "Max acceptable loss (% of exposure, at your chosen confidence level)",
        min_value=1, max_value=20, value=5,
    )
    confidence = st.selectbox("VaR confidence level", options=list(config.VAR_CONFIDENCE_Z.keys()))

try:
    snapshot = get_market_snapshot(currency)
except Exception as e:
    st.error(f"Couldn't load market data for {currency}: {e}")
    st.stop()

spot = snapshot["spot"]
annual_vol = snapshot["annual_vol"]
baseline_usd = notional_foreign * spot

col1, col2, col3 = st.columns(3)
col1.metric("Spot rate (USD per unit)", f"{spot:.4f}")
col2.metric("Annualized volatility", f"{annual_vol:.1%}")
col3.metric("Exposure value today", f"${baseline_usd:,.0f}")

st.divider()

# --- Risk on the unhedged exposure ---
st.subheader("Unhedged risk")

var_usd = parametric_var(baseline_usd, annual_vol, days_out, confidence)
risk_tolerance_usd = baseline_usd * (risk_tolerance_pct / 100)

rcol1, rcol2 = st.columns(2)
rcol1.metric(f"Value at Risk ({confidence}, {days_out}d horizon)", f"${var_usd:,.0f}")
rcol2.metric("Your stated risk tolerance", f"${risk_tolerance_usd:,.0f}")

if var_usd > risk_tolerance_usd:
    st.warning(
        f"Unhedged VaR (\\${var_usd:,.0f}) exceeds your stated risk tolerance "
        f"(\\${risk_tolerance_usd:,.0f}) — some hedging is warranted."
    )
else:
    st.success(
        f"Unhedged VaR (\\${var_usd:,.0f}) is already within your stated risk "
        f"tolerance (\\${risk_tolerance_usd:,.0f})."
    )

stress = stress_scenarios(spot, notional_foreign, direction)
stress_df = pd.DataFrame(stress)
stress_df["shock_pct"] = stress_df["shock_pct"].map(lambda x: f"{x:+.0%}")
stress_df["shocked_spot"] = stress_df["shocked_spot"].map(lambda x: f"{x:.4f}")
stress_df["pnl_usd"] = stress_df["pnl_usd"].map(lambda x: f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}")
stress_df.columns = ["Rate shock", "Shocked spot", "P&L vs. today (unhedged)"]
st.table(stress_df)

st.divider()

# --- Hedge comparison ---
st.subheader("Hedge comparison")

strategies = compare_strategies(currency, notional_foreign, direction, days_out, spot, annual_vol)

comparison_rows = [
    {
        "Strategy": "Do nothing",
        "USD outcome": f"${strategies['unhedged_baseline_usd']:,.0f} (today's spot; actual will vary)",
        "Cost today": "$0",
        "Risk removed": "None",
    },
    {
        "Strategy": "Forward contract",
        "USD outcome": f"${strategies['forward_locked_usd']:,.0f} (locked, certain)",
        "Cost today": "$0 (rate is built into the forward)",
        "Risk removed": "All rate risk on the hedged amount",
    },
    {
        "Strategy": f"{'Call' if direction == 'payable' else 'Put'} option (ATM, strike {strategies['option_strike']:.4f})",
        "USD outcome": f"Worst case ${strategies['option_worst_case_usd']:,.0f}, "
                        f"keeps upside if the rate moves in your favor",
        "Cost today": f"${strategies['option_premium_usd']:,.0f} premium",
        "Risk removed": "Downside capped, upside kept",
    },
]
st.table(pd.DataFrame(comparison_rows))

st.divider()

# --- Recommendation ---
st.subheader("Suggested hedge ratio")

hedge_ratio = recommend_hedge_ratio(var_usd, risk_tolerance_usd)
st.metric("Recommended % of exposure to hedge", f"{hedge_ratio:.0%}")
st.caption(
    "Rule of thumb, not investment advice: hedges just enough of the notional "
    "with a forward to bring VaR down to your stated risk tolerance. Assumes "
    "VaR scales linearly with the hedged fraction, which holds for a forward "
    "since it removes that fraction of the exposure outright."
)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=["Unhedged VaR", "Risk tolerance", f"VaR after {hedge_ratio:.0%} hedge"],
    y=[var_usd, risk_tolerance_usd, var_usd * (1 - hedge_ratio)],
    marker_color=["#d62728", "#2ca02c", "#1f77b4"],
))
fig.update_layout(yaxis_title="USD", height=350)
st.plotly_chart(fig, width="stretch")

st.divider()
st.caption(
    "Methodology and assumptions are documented in the README. This is a "
    "simplified educational model, not a pricing engine for real trades."
)
