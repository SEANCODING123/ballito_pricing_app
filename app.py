import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# APP CONFIG
# ────────────────────────────────────────────────
st.set_page_config(page_title="Ballito Creator Studio – Pricing Strategy Lab", layout="wide")

st.title("Ballito Creator Studio – Pricing Strategy Lab")
st.markdown("Adjust membership prices, member counts, and other assumptions to see real-time breakeven, revenue, margins and key cost curves.")

# ────────────────────────────────────────────────
# SIDEBAR INPUTS
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("Assumptions & Sliders")

    # Fixed costs
    monthly_fixed_opex = st.number_input("Monthly Fixed Operating Costs (rent, utils, etc.)", value=33500, step=500)
    monthly_loan = st.number_input("Monthly Loan Repayment", value=14843, step=100)
    total_monthly_fixed = monthly_fixed_opex + monthly_loan
    st.markdown(f"**Total monthly amount to cover:  R{total_monthly_fixed:,.0f}**")

    # Variable costs
    var_cost_per_member = st.number_input("Variable cost per member (R/month)", value=728.5, step=10.0, format="%.1f")

    # Production add-on
    production_addon_pct = st.slider("Production add-on revenue (% of membership fees)", 0.0, 0.50, 0.25, step=0.05)

    st.markdown("---")
    st.subheader("Membership Tiers – Prices & Counts")

    # Tiers
    tiers = [
        {"name": "Resident Creative", "price": 3300, "count": 2},
        {"name": "Creative Pro",      "price": 7500, "count": 1},
        {"name": "Production Member", "price": 13500,"count": 0},
        {"name": "Agency Base",       "price": 25000,"count": 0},
    ]

    prices = []
    counts = []
    for tier in tiers:
        col1, col2 = st.columns([3,1])
        with col1:
            p = st.number_input(f"{tier['name']} – Monthly Price (R)", value=tier["price"], step=500, key=f"price_{tier['name']}")
        with col2:
            c = st.number_input("Count", value=tier["count"], min_value=0, step=1, key=f"count_{tier['name']}")
        prices.append(p)
        counts.append(c)

    total_members = sum(counts)

# ────────────────────────────────────────────────
# CALCULATIONS
# ────────────────────────────────────────────────
membership_revenue = sum(p * c for p, c in zip(prices, counts))
production_revenue = membership_revenue * production_addon_pct
total_revenue_monthly = membership_revenue + production_revenue

total_variable_cost = var_cost_per_member * total_members
total_cost_monthly = total_monthly_fixed + total_variable_cost

profit_monthly = total_revenue_monthly - total_cost_monthly
breakeven_revenue = total_monthly_fixed / (1 + production_addon_pct)   # membership rev needed

if membership_revenue > 0:
    avg_price_per_member = membership_revenue / total_members
    contribution_margin_pct = (avg_price_per_member - var_cost_per_member) / avg_price_per_member
    breakeven_members = breakeven_revenue / avg_price_per_member if avg_price_per_member > 0 else np.inf
else:
    avg_price_per_member = 0
    contribution_margin_pct = 0
    breakeven_members = np.inf

status = "Above breakeven ✓" if profit_monthly > 0 else "Below breakeven ✗"
color = "green" if profit_monthly > 0 else "red"

# ────────────────────────────────────────────────
# MAIN PAGE – SUMMARY METRICS
# ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Members", total_members)
with col2:
    st.metric("Monthly Revenue", f"R{total_revenue_monthly:,.0f}", delta=None)
with col3:
    st.metric("Monthly Costs", f"R{total_cost_monthly:,.0f}")
with col4:
    st.metric("Monthly Profit", f"R{profit_monthly:,.0f}", delta_color="normal")

st.markdown(f"**Status:** <span style='color:{color}; font-weight:bold; font-size:1.2em;'>{status}</span>", unsafe_allow_html=True)

st.markdown(f"- Breakeven membership revenue needed: **R{breakeven_revenue:,.0f} / month**")
if total_members > 0:
    st.markdown(f"- Implied breakeven members (at current avg mix): **{breakeven_members:.1f}**")
    st.markdown(f"- Average revenue per member: **R{avg_price_per_member:,.0f}**")
    st.markdown(f"- Contribution margin per member: **{contribution_margin_pct:.1%}**")

# ────────────────────────────────────────────────
# CHART 1: REVENUE vs TOTAL COSTS (simple bar comparison)
# ────────────────────────────────────────────────
st.subheader("Revenue vs Total Costs – Monthly")

fig1 = go.Figure()

fig1.add_trace(go.Bar(
    x=["Revenue", "Costs", "Profit / Loss"],
    y=[total_revenue_monthly, total_cost_monthly, profit_monthly],
    marker_color=["royalblue", "crimson", "seagreen" if profit_monthly >= 0 else "tomato"],
    text=[f"R{total_revenue_monthly:,.0f}", f"R{total_cost_monthly:,.0f}", f"R{profit_monthly:,.0f}"],
    textposition="auto",
))

fig1.update_layout(
    title="Monthly Snapshot",
    yaxis_title="Rand (R)",
    height=450,
    bargap=0.4
)

st.plotly_chart(fig1, use_container_width=True)

# ────────────────────────────────────────────────
# CHART 2: COST CURVES (AFC, AVC, ATC + Avg Revenue)
# ────────────────────────────────────────────────
st.subheader("Cost Curves per Member + Average Revenue Line")

if total_members > 0:
    max_q = max(20, total_members * 2)
else:
    max_q = 20

q = np.arange(1, max_q + 1)

afc = total_monthly_fixed / q
avc = np.full_like(q, var_cost_per_member, dtype=float)
atc = afc + avc

if avg_price_per_member > 0:
    breakeven_q_curve = total_monthly_fixed / (avg_price_per_member - var_cost_per_member)
else:
    breakeven_q_curve = np.inf

fig2 = go.Figure()

fig2.add_trace(go.Scatter(x=q, y=afc, name="AFC (Average Fixed Cost)", line=dict(color="orange", dash="dash")))
fig2.add_trace(go.Scatter(x=q, y=avc, name="AVC (Average Variable Cost)", line=dict(color="purple")))
fig2.add_trace(go.Scatter(x=q, y=atc, name="ATC (Average Total Cost)", line=dict(color="red", width=3)))

# Average revenue line (horizontal)
if avg_price_per_member > 0:
    fig2.add_trace(go.Scatter(
        x=q, y=[avg_price_per_member] * len(q),
        name=f"Avg Revenue / member  (R{avg_price_per_member:,.0f})",
        line=dict(color="green", dash="dot", width=2.5)
    ))

# Breakeven point annotation
if breakeven_q_curve < max_q and breakeven_q_curve > 0:
    fig2.add_vline(x=breakeven_q_curve, line_dash="dash", line_color="darkgreen", annotation_text=f"Breakeven ≈ {breakeven_q_curve:.1f} members", annotation_position="top right")

fig2.update_layout(
    title="How Fixed Costs get Diluted + Breakeven Point",
    xaxis_title="Number of Members",
    yaxis_title="Cost / Revenue per Member (R)",
    height=550,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────────────────────────
# STRATEGY GUIDANCE
# ────────────────────────────────────────────────
st.subheader("Quick Strategy Insights")

if total_members == 0:
    st.warning("Add at least a few members to see meaningful insights.")
else:
    if profit_monthly > 0:
        st.success(f"You're in profit territory! At current settings you generate R{profit_monthly:,.0f} / month.")
    else:
        gap = -profit_monthly
        st.error(f"You're short by **R{gap:,.0f} / month** to break even.")

    st.markdown("""
    **Quick what-if ideas to test right now:**
    - Increase Agency Base price to R30,000–35,000 → fewer members needed
    - Lower Resident Creative to R2,800–3,000 and aim for 12–15 residents
    - Raise production add-on % (if realistic) → effectively lowers breakeven
    - Reduce fixed costs (negotiate rent/utilities) → biggest lever early on
    """)

st.markdown("---")
st.caption("This interactive tool concept and code was developed directly from Ballito Creator Studio’s detailed NPV model and sensitivity analysis.")
