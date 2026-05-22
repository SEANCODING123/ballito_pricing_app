import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ────────────────────────────────────────────────
# APP CONFIG
# ────────────────────────────────────────────────
st.set_page_config(page_title="Ballito Creator Studio – Pricing Strategy Lab", layout="wide")

st.title("Ballito Creator Studio – Pricing Strategy Lab")
st.markdown(
    "Model **monthly memberships** and **casual studio bookings** separately, "
    "then see their combined impact on revenue, costs, margins, and breakeven."
)

# ────────────────────────────────────────────────
# SIDEBAR INPUTS
# ────────────────────────────────────────────────
with st.sidebar:
    st.header("Assumptions & Sliders")

    monthly_fixed_opex = st.number_input(
        "Monthly Fixed Operating Costs (rent, utils, etc.)", value=33500, step=500
    )
    monthly_loan = st.number_input("Monthly Loan Repayment", value=14843, step=100)
    total_monthly_fixed = monthly_fixed_opex + monthly_loan
    st.markdown(f"**Total monthly fixed costs: R{total_monthly_fixed:,.0f}**")

    st.markdown("---")
    st.subheader("Variable Costs")
    var_cost_per_member = st.number_input(
        "Variable cost per member (R/month)", value=728.5, step=10.0, format="%.1f"
    )
    var_cost_per_booking = st.number_input(
        "Variable cost per casual booking (R/session)",
        value=150.0,
        step=10.0,
        format="%.1f",
        help="Cleaning, utilities, coffee, etc. per studio session",
    )

    production_addon_pct = st.slider(
        "Production add-on (% of **membership fees only**)",
        0.0,
        0.50,
        0.25,
        step=0.05,
        help="Applies to membership revenue, not casual studio sales.",
    )

    st.markdown("---")
    st.subheader("Membership Tiers (Monthly)")
    st.caption("Recurring members — long-term studio occupancy.")

    tiers = [
        {"name": "Resident Creative", "price": 3300, "count": 2},
        {"name": "Creative Pro", "price": 7500, "count": 1},
        {"name": "Production Member", "price": 13500, "count": 0},
        {"name": "Agency Base", "price": 25000, "count": 0},
    ]

    prices = []
    counts = []
    for tier in tiers:
        col1, col2 = st.columns([3, 1])
        with col1:
            p = st.number_input(
                f"{tier['name']} – Monthly Price (R)",
                value=tier["price"],
                step=500,
                key=f"price_{tier['name']}",
            )
        with col2:
            c = st.number_input(
                "Count",
                value=tier["count"],
                min_value=0,
                step=1,
                key=f"count_{tier['name']}",
            )
        prices.append(p)
        counts.append(c)

    total_members = sum(counts)

    st.markdown("---")
    st.subheader("Casual Studio Sales (Monthly)")
    st.caption("Transactional bookings — separate from membership tiers.")

    booking_types = [
        {"name": "Full Day", "price": 5500, "count": 2},
        {"name": "Half Day", "price": 3800, "count": 4},
        {"name": "2-Hour", "price": 2600, "count": 8},
    ]

    booking_prices = []
    booking_counts = []
    for bt in booking_types:
        col1, col2 = st.columns([3, 1])
        with col1:
            bp = st.number_input(
                f"{bt['name']} – Price (R)",
                value=bt["price"],
                step=100,
                key=f"booking_price_{bt['name']}",
            )
        with col2:
            bc = st.number_input(
                "Bookings",
                value=bt["count"],
                min_value=0,
                step=1,
                key=f"booking_count_{bt['name']}",
            )
        booking_prices.append(bp)
        booking_counts.append(bc)

    total_bookings = sum(booking_counts)

# ────────────────────────────────────────────────
# CALCULATIONS
# ────────────────────────────────────────────────
membership_revenue = sum(p * c for p, c in zip(prices, counts))
production_revenue = membership_revenue * production_addon_pct
casual_revenue = sum(p * c for p, c in zip(booking_prices, booking_counts))

total_revenue_monthly = membership_revenue + production_revenue + casual_revenue

var_cost_members = var_cost_per_member * total_members
var_cost_bookings = var_cost_per_booking * total_bookings
total_variable_cost = var_cost_members + var_cost_bookings
total_cost_monthly = total_monthly_fixed + total_variable_cost

profit_monthly = total_revenue_monthly - total_cost_monthly

total_activity = total_members + total_bookings

if total_activity > 0:
    avg_revenue_per_unit = total_revenue_monthly / total_activity
    avg_var_cost_per_unit = total_variable_cost / total_activity
    contribution_per_unit = avg_revenue_per_unit - avg_var_cost_per_unit
    contribution_margin_pct = (
        contribution_per_unit / avg_revenue_per_unit if avg_revenue_per_unit > 0 else 0
    )
    breakeven_units = (
        total_monthly_fixed / contribution_per_unit
        if contribution_per_unit > 0
        else np.inf
    )
else:
    avg_revenue_per_unit = 0
    avg_var_cost_per_unit = 0
    contribution_per_unit = 0
    contribution_margin_pct = 0
    breakeven_units = np.inf

breakeven_revenue_needed = total_monthly_fixed + total_variable_cost

membership_share = membership_revenue / total_revenue_monthly if total_revenue_monthly else 0
casual_share = casual_revenue / total_revenue_monthly if total_revenue_monthly else 0

status = "Above breakeven ✓" if profit_monthly > 0 else "Below breakeven ✗"
status_color = "green" if profit_monthly > 0 else "red"

# ────────────────────────────────────────────────
# MAIN PAGE – SUMMARY METRICS
# ────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Members & Bookings",
        total_activity,
        help="Combined studio activity: recurring members + casual sessions",
    )
    st.caption(f"{total_members} members · {total_bookings} bookings / month")

with col2:
    st.metric("Total Monthly Revenue", f"R{total_revenue_monthly:,.0f}")
    st.caption(
        f"Membership R{membership_revenue:,.0f} · "
        f"Casual R{casual_revenue:,.0f} · "
        f"Production +R{production_revenue:,.0f}"
    )

with col3:
    st.metric("Total Monthly Costs", f"R{total_cost_monthly:,.0f}")
    st.caption(
        f"Fixed R{total_monthly_fixed:,.0f} · "
        f"Variable R{total_variable_cost:,.0f}"
    )

with col4:
    st.metric(
        "Net Monthly Profit",
        f"R{profit_monthly:,.0f}",
        delta=status,
        delta_color="normal" if profit_monthly >= 0 else "inverse",
    )

st.markdown(
    f"**Status:** <span style='color:{status_color}; font-weight:bold; font-size:1.2em;'>{status}</span>",
    unsafe_allow_html=True,
)

st.markdown("#### Revenue & cost breakdown")
rc1, rc2, rc3 = st.columns(3)
with rc1:
    st.markdown("**Membership**")
    st.markdown(f"- Fees: **R{membership_revenue:,.0f}** ({membership_share:.0%} of revenue)")
    st.markdown(
        f"- Production add-on ({production_addon_pct:.0%} of fees): **R{production_revenue:,.0f}**"
    )
with rc2:
    st.markdown("**Casual studio sales**")
    st.markdown(f"- Bookings revenue: **R{casual_revenue:,.0f}** ({casual_share:.0%} of revenue)")
    for bt, bp, bc in zip(booking_types, booking_prices, booking_counts):
        if bc > 0:
            st.markdown(f"  - {bt['name']}: {bc}× @ R{bp:,.0f} = R{bp * bc:,.0f}")
with rc3:
    st.markdown("**Costs & breakeven**")
    st.markdown(f"- Member variable: **R{var_cost_members:,.0f}**")
    st.markdown(f"- Booking variable: **R{var_cost_bookings:,.0f}**")
    st.markdown(f"- Revenue to break even (at current mix): **R{breakeven_revenue_needed:,.0f}**")
    if total_activity > 0:
        st.markdown(f"- Blended breakeven activity: **≈ {breakeven_units:.1f}** units")
        st.markdown(f"- Avg revenue / unit: **R{avg_revenue_per_unit:,.0f}**")
        st.markdown(f"- Contribution margin: **{contribution_margin_pct:.1%}**")

# ────────────────────────────────────────────────
# CHART 1: REVENUE vs COSTS (breakdown)
# ────────────────────────────────────────────────
st.subheader("Revenue vs Costs – Monthly Breakdown")

fig1 = go.Figure()

fig1.add_trace(
    go.Bar(
        name="Membership",
        x=["Revenue"],
        y=[membership_revenue],
        marker_color="royalblue",
        text=[f"R{membership_revenue:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Production add-on",
        x=["Revenue"],
        y=[production_revenue],
        marker_color="cornflowerblue",
        text=[f"R{production_revenue:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Casual sales",
        x=["Revenue"],
        y=[casual_revenue],
        marker_color="mediumseagreen",
        text=[f"R{casual_revenue:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Fixed costs",
        x=["Costs"],
        y=[total_monthly_fixed],
        marker_color="indianred",
        text=[f"R{total_monthly_fixed:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Variable (members)",
        x=["Costs"],
        y=[var_cost_members],
        marker_color="salmon",
        text=[f"R{var_cost_members:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Variable (bookings)",
        x=["Costs"],
        y=[var_cost_bookings],
        marker_color="lightcoral",
        text=[f"R{var_cost_bookings:,.0f}"],
        textposition="inside",
    )
)
fig1.add_trace(
    go.Bar(
        name="Net profit",
        x=["Profit"],
        y=[profit_monthly],
        marker_color="seagreen" if profit_monthly >= 0 else "tomato",
        text=[f"R{profit_monthly:,.0f}"],
        textposition="auto",
    )
)

fig1.update_layout(
    barmode="stack",
    title="Revenue sources vs cost structure",
    yaxis_title="Rand (R)",
    height=480,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

st.plotly_chart(fig1, use_container_width=True)

# ────────────────────────────────────────────────
# CHART 2: COST CURVES (blended mix)
# ────────────────────────────────────────────────
st.subheader("Cost Curves – Blended Members & Bookings")

max_q = max(20, int(total_activity * 2)) if total_activity > 0 else 20
q = np.arange(1, max_q + 1)

afc = total_monthly_fixed / q
avc = (
    np.full_like(q, avg_var_cost_per_unit, dtype=float)
    if total_activity > 0
    else np.zeros_like(q)
)
atc = afc + avc

breakeven_q_curve = (
    total_monthly_fixed / contribution_per_unit if contribution_per_unit > 0 else np.inf
)

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(x=q, y=afc, name="AFC (Average Fixed Cost)", line=dict(color="orange", dash="dash"))
)
fig2.add_trace(
    go.Scatter(x=q, y=avc, name="AVC (Blended variable cost)", line=dict(color="purple"))
)
fig2.add_trace(
    go.Scatter(x=q, y=atc, name="ATC (Average Total Cost)", line=dict(color="red", width=3))
)

if avg_revenue_per_unit > 0:
    fig2.add_trace(
        go.Scatter(
            x=q,
            y=[avg_revenue_per_unit] * len(q),
            name=f"Blended avg revenue / unit (R{avg_revenue_per_unit:,.0f})",
            line=dict(color="green", dash="dot", width=2.5),
        )
    )

if breakeven_q_curve < max_q and breakeven_q_curve > 0:
    fig2.add_vline(
        x=breakeven_q_curve,
        line_dash="dash",
        line_color="darkgreen",
        annotation_text=f"Breakeven ≈ {breakeven_q_curve:.1f} units",
        annotation_position="top right",
    )

if total_activity > 0:
    fig2.add_vline(
        x=total_activity,
        line_dash="dot",
        line_color="blue",
        annotation_text=f"Current: {total_members} members + {total_bookings} bookings",
        annotation_position="bottom right",
    )

fig2.update_layout(
    title="Fixed cost dilution at blended membership + booking mix",
    xaxis_title="Activity units (members + bookings)",
    yaxis_title="Cost / Revenue per unit (R)",
    height=550,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────────────────────────
# STRATEGY GUIDANCE
# ────────────────────────────────────────────────
st.subheader("Quick Strategy Insights")

if total_activity == 0:
    st.warning("Add members and/or casual bookings to see meaningful insights.")
else:
    if profit_monthly > 0:
        st.success(
            f"You're in profit territory — **R{profit_monthly:,.0f} / month** "
            f"from {total_members} members and {total_bookings} casual bookings."
        )
    else:
        st.error(f"You're short by **R{-profit_monthly:,.0f} / month** to break even.")

    if casual_share > membership_share and total_bookings > 0:
        st.info(
            f"Casual sales drive **{casual_share:.0%}** of revenue. "
            "Consider packaging repeat bookers into Resident Creative tiers for more predictable income."
        )
    elif membership_share >= 0.6 and total_members > 0:
        st.info(
            f"Memberships drive **{membership_share:.0%}** of revenue — strong recurring base. "
            "Use casual slots (half-day / 2-hour) to fill gaps without discounting member value."
        )

    if total_bookings > 0 and casual_revenue > 0:
        avg_booking = casual_revenue / total_bookings
        st.markdown(
            f"- Average casual booking value: **R{avg_booking:,.0f}** "
            f"(cost R{var_cost_per_booking:,.0f}/session → "
            f"**R{avg_booking - var_cost_per_booking:,.0f}** contribution each)"
        )

    st.markdown(
        """
        **What-if ideas:**
        - Push **Full Day** (R5,500) for corporate shoots — fewer sessions, higher margin
        - Bundle **2-Hour** blocks for content creators at volume (8+/month)
        - Grow **Resident Creative** count — lowers AFC on the cost curve fastest
        - Raise production add-on % on memberships only — does not affect casual pricing
        - Trim **variable cost per booking** (supplies, cleaning) to improve casual margins
        """
    )

st.markdown("---")
st.caption(
    "Membership tiers and casual studio sales are modelled as separate revenue streams. "
    "Production add-on applies to membership fees only."
)
