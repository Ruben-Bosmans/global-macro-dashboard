import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Macro Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROC = Path("data/processed")

COLORS = [
    "#2563EB","#DC2626","#16A34A","#D97706","#7C3AED",
    "#0891B2","#DB2777","#65A30D","#EA580C","#4F46E5",
    "#9333EA","#0D9488","#B45309","#1D4ED8","#BE123C",
]

# ── Data loading ──────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_summary():
    path = PROC / "summary.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

@st.cache_data(ttl=3600)
def load_series(name):
    path = PROC / f"{name}.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        return df.sort_values("date")
    except Exception:
        return None

# ── Chart helpers ─────────────────────────────────────────────────
def plot_line(df, col="value", title="", ylabel="",
              color="#2563EB", start=None, end=None):
    if df is None or df.empty:
        return go.Figure()
    d = df.copy()
    if start:
        d = d[d["date"] >= pd.Timestamp(start)]
    if end:
        d = d[d["date"] <= pd.Timestamp(end)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["date"], y=d[col], mode="lines",
        line=dict(color=color, width=2),
        hovertemplate="%{x|%Y-%m-%d}: %{y:.4f}<extra></extra>"
    ))
    fig.update_layout(
        title=title, yaxis_title=ylabel, hovermode="x unified",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
    )
    return fig


def plot_multi(series_dict, title="", ylabel="", start=None, end=None):
    """Multiple series on one chart — absolute values."""
    fig = go.Figure()
    for i, (label, df) in enumerate(series_dict.items()):
        if df is None or df.empty:
            continue
        d = df.copy()
        if start:
            d = d[d["date"] >= pd.Timestamp(start)]
        if end:
            d = d[d["date"] <= pd.Timestamp(end)]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["value"], name=label, mode="lines",
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            hovertemplate=f"{label}: %{{y:.4f}}<extra></extra>"
        ))
    fig.update_layout(
        title=title, yaxis_title=ylabel, hovermode="x unified",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
    )
    return fig


def plot_normalized(series_dict, title="", start=None, end=None):
    """
    Zero-baseline normalized chart.
    All series rebased to 0% at the start of the selected period.
    Above zero = gain, below zero = loss.
    """
    fig = go.Figure()
    fig.add_hline(y=0, line_color="#999999", line_width=1)

    for i, (label, df) in enumerate(series_dict.items()):
        if df is None or df.empty:
            continue
        d = df.copy()
        if start:
            d = d[d["date"] >= pd.Timestamp(start)]
        if end:
            d = d[d["date"] <= pd.Timestamp(end)]
        if d.empty or len(d) < 2:
            continue
        base = d["value"].iloc[0]
        if base == 0 or pd.isna(base):
            continue
        d["pct"] = ((d["value"] / base) - 1) * 100
        last = d["pct"].iloc[-1]
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["pct"],
            name=f"{label}  ({last:+.1f}%)",
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"{label}: %{{y:+.2f}}%<extra></extra>"
        ))
    fig.update_layout(
        title=title,
        yaxis_title="% change from start",
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0",
                   zeroline=True, zerolinecolor="#999999"),
    )
    return fig


def pct_fmt(v, decimals=2):
    if pd.isna(v):
        return "—"
    return f"{v:+.{decimals}f}%"

def abs_fmt(v, decimals=2):
    if pd.isna(v):
        return "—"
    return f"{v:+.{decimals}f}"


# ── Sidebar ───────────────────────────────────────────────────────
summary = load_summary()

st.sidebar.title("🌍 Global Macro")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate to", [
    "📊 Overview",
    "📈 Markets",
    "🏦 Rates & Bonds",
    "🔥 Inflation",
    "💼 Economy",
    "🔀 Compare",
])

st.sidebar.markdown("---")
st.sidebar.subheader("⏱ Time range")
range_options = {
    "1 month":  timedelta(days=30),
    "3 months": timedelta(days=90),
    "6 months": timedelta(days=180),
    "1 year":   timedelta(days=365),
    "3 years":  timedelta(days=365*3),
    "5 years":  timedelta(days=365*5),
    "10 years": timedelta(days=365*10),
    "All time": None,
}
sel_range = st.sidebar.selectbox("Show last", list(range_options.keys()), index=3)
end_dt    = datetime.today()
start_dt  = (end_dt - range_options[sel_range]) if range_options[sel_range] else None


# ══════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("📊 Global Macro — Overview")
    if not summary.empty:
        st.caption(f"Data last updated: {summary['last_date'].max()}")

    # ── Key metrics ────────────────────────────────────────────────
    st.subheader("Key Snapshot")
    key_metrics = [
        ("Fed Funds Rate",  "rate_us",          "last_value", "%"),
        ("ECB Rate",        "ecb_ecb_deposit",   "last_value", "%"),
        ("US 10Y Yield",    "us_10y_yield",      "last_value", "%"),
        ("US CPI YoY",      "cpi_us",            "yoy_pct",    "%"),
        ("S&P 500",         "sp500",             "last_value", "idx"),
        ("VIX",             "vix",               "last_value", "idx"),
        ("Gold",            "gold",              "last_value", "usd"),
        ("US HY Spread",    "credit_us_hy_oas",  "last_value", "bps"),
    ]
    delta_map = {
        "rate_us":          "chg_1m_abs",
        "ecb_ecb_deposit":  "chg_1m_abs",
        "us_10y_yield":     "chg_1m_abs",
        "cpi_us":           None,
        "sp500":            "chg_1w_pct",
        "vix":              "chg_1w_pct",
        "gold":             "chg_1w_pct",
        "credit_us_hy_oas": "chg_1w_abs",
    }

    cols = st.columns(4)
    for i, (label, name, val_col, unit) in enumerate(key_metrics):
        r = summary[summary["name"] == name]
        if r.empty:
            continue
        r = r.iloc[0]
        val  = r.get(val_col)
        dcol = delta_map.get(name)
        chg  = r.get(dcol) if dcol else None

        if unit == "%":
            val_str   = f"{val:.2f}%" if pd.notna(val) else "—"
            delta_str = f"{chg*100:+.1f} bps" if pd.notna(chg) else None
        elif unit == "idx":
            val_str   = f"{val:,.2f}" if pd.notna(val) else "—"
            delta_str = f"{chg:+.2f}%" if pd.notna(chg) else None
        elif unit == "usd":
            val_str   = f"${val:,.2f}" if pd.notna(val) else "—"
            delta_str = f"{chg:+.2f}%" if pd.notna(chg) else None
        else:
            val_str   = f"{val:.0f} bps" if pd.notna(val) else "—"
            delta_str = f"{chg:+.1f} bps" if pd.notna(chg) else None

        with cols[i % 4]:
            st.metric(label=label, value=val_str, delta=delta_str)

    st.markdown("---")

    # ── Biggest movers ─────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Top Gainers — This Week")
        if "chg_1w_pct" in summary.columns:
            top = (summary[summary["chg_1w_pct"].notna()]
                   .nlargest(10, "chg_1w_pct")
                   [["description","category","country","last_value","chg_1w_pct"]]
                   .copy())
            top["chg_1w_pct"] = top["chg_1w_pct"].map(lambda x: f"{x:+.2f}%")
            top.columns = ["Series","Category","Country","Last","1W %"]
            st.dataframe(top, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("📉 Top Losers — This Week")
        if "chg_1w_pct" in summary.columns:
            bot = (summary[summary["chg_1w_pct"].notna()]
                   .nsmallest(10, "chg_1w_pct")
                   [["description","category","country","last_value","chg_1w_pct"]]
                   .copy())
            bot["chg_1w_pct"] = bot["chg_1w_pct"].map(lambda x: f"{x:+.2f}%")
            bot.columns = ["Series","Category","Country","Last","1W %"]
            st.dataframe(bot, hide_index=True, use_container_width=True)

    st.markdown("---")

    # ── Full snapshot table ────────────────────────────────────────
    st.subheader("Full Current Snapshot")
    cat_filter = st.selectbox(
        "Filter by category",
        ["All"] + sorted(summary["category"].dropna().unique().tolist())
    )
    disp = summary.copy()
    if cat_filter != "All":
        disp = disp[disp["category"] == cat_filter]

    show_cols = [c for c in
        ["description","category","country","last_date","last_value",
         "chg_1w_pct","chg_1m_pct","chg_1y_pct","yoy_pct"]
        if c in disp.columns]

    st.dataframe(
        disp[show_cols].rename(columns={
            "description":"Series","category":"Category",
            "country":"Country","last_date":"Date",
            "last_value":"Value","chg_1w_pct":"1W %",
            "chg_1m_pct":"1M %","chg_1y_pct":"1Y %","yoy_pct":"YoY %"
        }),
        hide_index=True, use_container_width=True
    )


# ══════════════════════════════════════════════════════════════════
# PAGE: MARKETS
# ══════════════════════════════════════════════════════════════════
elif page == "📈 Markets":
    st.title("📈 Markets")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏛️ Equity Indices", "🏭 US Sectors",
        "🛢️ Commodities",    "₿ Crypto"
    ])

    # ── EQUITIES ──────────────────────────────────────────────────
    with tab1:
        st.subheader("Global Equity Indices")

        regions = {
            "United States": {
                "sp500":"S&P 500","nasdaq100":"Nasdaq 100",
                "dow_jones":"Dow Jones","russell2000":"Russell 2000","vix":"VIX"
            },
            "Europe": {
                "eurostoxx50":"Euro Stoxx 50","dax":"DAX","cac40":"CAC 40",
                "ftse100":"FTSE 100","ibex35":"IBEX 35","ftse_mib":"FTSE MIB",
                "aex":"AEX","bel20":"BEL 20","smi":"SMI"
            },
            "Asia-Pacific": {
                "nikkei":"Nikkei 225","hang_seng":"Hang Seng",
                "shanghai":"Shanghai","kospi":"KOSPI",
                "sensex":"Sensex","asx200":"ASX 200","nifty50":"Nifty 50"
            },
            "Americas (ex-US)": {
                "tsx":"TSX","bovespa":"Bovespa","ipc_mexico":"IPC Mexico"
            },
        }

        region = st.selectbox("Region", list(regions.keys()))
        idx_map = regions[region]

        selected_idx = st.multiselect(
            "Select indices",
            options=list(idx_map.keys()),
            default=list(idx_map.keys())[:4],
            format_func=lambda x: idx_map[x]
        )

        if selected_idx:
            m_cols = st.columns(len(selected_idx))
            for i, n in enumerate(selected_idx):
                r = summary[summary["name"] == n]
                if r.empty:
                    continue
                r = r.iloc[0]
                chg = r.get("chg_1w_pct")
                with m_cols[i]:
                    st.metric(
                        idx_map[n],
                        f"{r['last_value']:,.0f}",
                        f"{chg:+.2f}%" if pd.notna(chg) else None
                    )

            st.subheader("Performance — normalized to 0% from start of period")
            norm_data = {idx_map[n]: load_series(n) for n in selected_idx}
            fig = plot_normalized(norm_data, start=start_dt, end=end_dt)
            st.plotly_chart(fig, use_container_width=True)

    # ── SECTORS ───────────────────────────────────────────────────
    with tab2:
        st.subheader("US Sector Performance (S&P 500 SPDR ETFs)")

        sectors = {
            "sector_tech":          "Technology",
            "sector_financial":     "Financials",
            "sector_energy":        "Energy",
            "sector_health":        "Health Care",
            "sector_industrial":    "Industrials",
            "sector_comms":         "Communication",
            "sector_cons_disc":     "Cons. Discretionary",
            "sector_cons_staples":  "Cons. Staples",
            "sector_utilities":     "Utilities",
            "sector_realestate":    "Real Estate",
            "sector_materials":     "Materials",
        }

        sect_rows = []
        for n, lbl in sectors.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            sect_rows.append({
                "Sector": lbl,
                "Last": f"{r['last_value']:.2f}",
                "1W %": pct_fmt(r.get("chg_1w_pct")),
                "1M %": pct_fmt(r.get("chg_1m_pct")),
                "1Y %": pct_fmt(r.get("chg_1y_pct")),
                "YTD %": pct_fmt(r.get("ytd_pct")),
            })
        st.dataframe(pd.DataFrame(sect_rows), hide_index=True, use_container_width=True)

        selected_sect = st.multiselect(
            "Select sectors to compare",
            options=list(sectors.keys()),
            default=list(sectors.keys()),
            format_func=lambda x: sectors[x]
        )
        if selected_sect:
            fig = plot_normalized(
                {sectors[n]: load_series(n) for n in selected_sect},
                title="Sector Performance — normalized",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── COMMODITIES ───────────────────────────────────────────────
    with tab3:
        st.subheader("Commodities")

        comm_groups = {
            "Energy":      ["oil_wti","oil_brent","natural_gas","gasoline","heating_oil","coal_newcastle"],
            "Metals":      ["gold","copper","silver","platinum","palladium"],
            "Agriculture": ["wheat","corn","soybeans","coffee","cotton","sugar","cocoa","lumber"],
        }

        for grp, items in comm_groups.items():
            st.markdown(f"**{grp}**")
            g_cols = st.columns(len(items))
            for i, n in enumerate(items):
                r = summary[summary["name"] == n]
                if r.empty:
                    continue
                r = r.iloc[0]
                chg = r.get("chg_1w_pct")
                with g_cols[i]:
                    st.metric(
                        r["description"],
                        f"{r['last_value']:.2f}",
                        f"{chg:+.2f}%" if pd.notna(chg) else None
                    )

        all_comm = [n for g in comm_groups.values() for n in g]
        sel_comm = st.multiselect(
            "Compare commodities",
            options=all_comm,
            default=["gold","oil_wti","copper","wheat"],
            format_func=lambda x: summary[summary["name"]==x]["description"].iloc[0]
                        if not summary[summary["name"]==x].empty else x
        )
        if sel_comm:
            fig = plot_normalized(
                {summary[summary["name"]==n]["description"].iloc[0]: load_series(n)
                 for n in sel_comm if not summary[summary["name"]==n].empty},
                title="Commodity Performance — normalized",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── CRYPTO ────────────────────────────────────────────────────
    with tab4:
        st.subheader("Cryptocurrency")

        crypto_list = [
            "crypto_btc","crypto_eth","crypto_bnb","crypto_sol","crypto_xrp",
            "crypto_ada","crypto_avax","crypto_doge","crypto_dot","crypto_link",
            "crypto_ltc","crypto_xlm","crypto_atom","crypto_uni"
        ]

        c_cols = st.columns(4)
        for i, n in enumerate(crypto_list):
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            chg = r.get("chg_1w_pct")
            with c_cols[i % 4]:
                st.metric(
                    r["description"],
                    f"${r['last_value']:,.2f}",
                    f"{chg:+.2f}%" if pd.notna(chg) else None
                )

        sel_crypto = st.multiselect(
            "Compare cryptocurrencies",
            options=crypto_list,
            default=["crypto_btc","crypto_eth","crypto_sol"],
            format_func=lambda x: summary[summary["name"]==x]["description"].iloc[0]
                        if not summary[summary["name"]==x].empty else x
        )
        if sel_crypto:
            fig = plot_normalized(
                {summary[summary["name"]==n]["description"].iloc[0]: load_series(n)
                 for n in sel_crypto if not summary[summary["name"]==n].empty},
                title="Crypto Performance — normalized",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE: RATES & BONDS
# ══════════════════════════════════════════════════════════════════
elif page == "🏦 Rates & Bonds":
    st.title("🏦 Rates & Bonds")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏛️ Policy Rates","📜 Bond Yields","📐 Yield Curves","💳 Credit Spreads"
    ])

    # ── POLICY RATES ──────────────────────────────────────────────
    with tab1:
        st.subheader("Central Bank Policy Rates")

        policy = {
            "rate_us":         "Fed (US)",
            "ecb_ecb_deposit": "ECB (Eurozone)",
            "rate_uk":         "BoE (UK)",
            "rate_jp":         "BoJ (Japan)",
            "rate_ca":         "BoC (Canada)",
            "rate_br":         "BCB (Brazil)",
            "rate_in":         "RBI (India)",
            "rate_za":         "SARB (S. Africa)",
            "rate_cn":         "PBoC (China)",
        }

        pr_rows = []
        for n, lbl in policy.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            pr_rows.append({
                "Central Bank": lbl,
                "Rate (%)": f"{r['last_value']:.2f}",
                "1M Δ (bps)": abs_fmt(r.get("chg_1m_abs", None), 0)
                              if pd.notna(r.get("chg_1m_abs")) else "—",
                "1Y Δ (bps)": abs_fmt(r.get("chg_1y_abs", None), 0)
                              if pd.notna(r.get("chg_1y_abs")) else "—",
                "Last Update": r["last_date"],
            })
        st.dataframe(pd.DataFrame(pr_rows), hide_index=True, use_container_width=True)

        sel_policy = st.multiselect(
            "Select central banks",
            options=list(policy.keys()),
            default=["rate_us","ecb_ecb_deposit","rate_uk","rate_jp"],
            format_func=lambda x: policy[x]
        )
        if sel_policy:
            fig = plot_multi(
                {policy[n]: load_series(n) for n in sel_policy},
                title="Policy Rates (%)", ylabel="%",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── BOND YIELDS ───────────────────────────────────────────────
    with tab2:
        st.subheader("10-Year Government Bond Yields")

        bonds = {
            "us_10y_yield":"US","bond10y_de":"Germany","bond10y_uk":"UK",
            "bond10y_fr":"France","bond10y_it":"Italy","bond10y_jp":"Japan",
            "bond10y_es":"Spain","bond10y_nl":"Netherlands","bond10y_be":"Belgium",
            "bond10y_pt":"Portugal","bond10y_gr":"Greece","bond10y_ca":"Canada",
            "bond10y_au":"Australia","bond10y_ch":"Switzerland",
            "bond10y_se":"Sweden","bond10y_no":"Norway",
            "bond10y_kr":"S. Korea","bond10y_mx":"Mexico",
        }

        b_rows = []
        for n, lbl in bonds.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            chg_1m = r.get("chg_1m_abs")
            chg_1y = r.get("chg_1y_abs")
            b_rows.append({
                "Country": lbl,
                "Yield (%)": f"{r['last_value']:.3f}",
                "1M Δ (bps)": f"{chg_1m*100:+.1f}" if pd.notna(chg_1m) else "—",
                "1Y Δ (bps)": f"{chg_1y*100:+.1f}" if pd.notna(chg_1y) else "—",
            })
        st.dataframe(pd.DataFrame(b_rows), hide_index=True, use_container_width=True)

        sel_bonds = st.multiselect(
            "Select countries",
            options=list(bonds.keys()),
            default=["us_10y_yield","bond10y_de","bond10y_uk","bond10y_it"],
            format_func=lambda x: bonds[x]
        )
        if sel_bonds:
            fig = plot_multi(
                {bonds[n]: load_series(n) for n in sel_bonds},
                title="10Y Government Bond Yields (%)", ylabel="%",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── YIELD CURVES ──────────────────────────────────────────────
    with tab3:
        st.subheader("Yield Curve & Spreads")

        col1, col2 = st.columns(2)
        with col1:
            df = load_series("credit_spread_10y_2y")
            if df is not None:
                fig = plot_line(df, title="US Yield Curve — 10Y minus 2Y (%)",
                              ylabel="%", color="#2563EB",
                              start=start_dt, end=end_dt)
                fig.add_hline(y=0, line_dash="dash", line_color="red",
                             annotation_text="Inversion")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Negative = inverted curve → historically a recession signal.")

        with col2:
            df = load_series("ecb_yc_10y")
            if df is not None:
                fig = plot_line(df, title="ECB Yield Curve — 10Y Spot Rate (%)",
                              ylabel="%", color="#7C3AED",
                              start=start_dt, end=end_dt)
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Eurozone Sovereign Spreads vs Germany")
        eu_spreads = {
            "spread_it_de":"Italy","spread_es_de":"Spain",
            "spread_fr_de":"France","spread_pt_de":"Portugal",
            "spread_gr_de":"Greece","spread_be_de":"Belgium",
        }

        sp_rows = []
        for n, lbl in eu_spreads.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            sp_rows.append({
                "Country": lbl,
                "Spread (bps)": f"{r['last_value']:.1f}",
                "1M Δ (bps)": abs_fmt(r.get("chg_1m_abs"), 1)
                              if pd.notna(r.get("chg_1m_abs")) else "—",
            })
        st.dataframe(pd.DataFrame(sp_rows), hide_index=True, use_container_width=True)

        sel_sp = st.multiselect(
            "Select spreads",
            options=list(eu_spreads.keys()),
            default=list(eu_spreads.keys()),
            format_func=lambda x: eu_spreads[x]
        )
        if sel_sp:
            fig = plot_multi(
                {eu_spreads[n]: load_series(n) for n in sel_sp},
                title="Eurozone Spreads vs Germany (bps)", ylabel="bps",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Real Interest Rates (10Y − CPI YoY)")
        real = {
            "real_rate_us":"US","real_rate_de":"Germany",
            "real_rate_uk":"UK","real_rate_jp":"Japan",
            "real_rate_fr":"France","real_rate_it":"Italy",
            "real_rate_ca":"Canada","real_rate_au":"Australia",
        }
        sel_real = st.multiselect(
            "Select countries",
            options=list(real.keys()),
            default=list(real.keys()),
            format_func=lambda x: real[x]
        )
        if sel_real:
            fig = plot_multi(
                {real[n]: load_series(n) for n in sel_real},
                title="Real Interest Rates (%)", ylabel="%",
                start=start_dt, end=end_dt
            )
            fig.add_hline(y=0, line_dash="dash", line_color="#999999")
            st.plotly_chart(fig, use_container_width=True)

    # ── CREDIT SPREADS ────────────────────────────────────────────
    with tab4:
        st.subheader("Credit Spreads (OAS in basis points)")

        col1, col2 = st.columns(2)
        with col1:
            fig = plot_multi({
                "US HY Total": load_series("credit_us_hy_oas"),
                "BB":          load_series("credit_us_hy_bb"),
                "B":           load_series("credit_us_hy_b"),
                "CCC":         load_series("credit_us_hy_ccc"),
            }, title="US High Yield Spreads (bps)", ylabel="bps",
            start=start_dt, end=end_dt)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = plot_multi({
                "US IG Total": load_series("credit_us_ig_oas"),
                "AAA":         load_series("credit_us_ig_aaa"),
                "BBB":         load_series("credit_us_ig_bbb"),
            }, title="US Investment Grade Spreads (bps)", ylabel="bps",
            start=start_dt, end=end_dt)
            st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = plot_multi({
                "US HY": load_series("credit_us_hy_oas"),
                "EU HY": load_series("credit_eu_hy_oas"),
                "EM HY": load_series("credit_em_hy_oas"),
                "US IG": load_series("credit_us_ig_oas"),
            }, title="Global Credit Spreads (bps)", ylabel="bps",
            start=start_dt, end=end_dt)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = plot_multi({
                "TED Spread":  load_series("credit_ted_spread"),
                "SOFR":        load_series("credit_sofr_spread"),
                "Euribor 3M":  load_series("ecb_euribor_3m"),
            }, title="Money Market Rates (%)", ylabel="%",
            start=start_dt, end=end_dt)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Mortgage & Term Premium")
        col1, col2 = st.columns(2)
        with col1:
            df = load_series("credit_mortgage_30y")
            if df is not None:
                fig = plot_line(df, title="US 30Y Mortgage Rate (%)",
                              ylabel="%", color="#EA580C",
                              start=start_dt, end=end_dt)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            df = load_series("mortgage_spread")
            if df is not None:
                fig = plot_line(df, title="Mortgage Spread vs 10Y Treasury (bps)",
                              ylabel="bps", color="#9333EA",
                              start=start_dt, end=end_dt)
                st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE: INFLATION
# ══════════════════════════════════════════════════════════════════
elif page == "🔥 Inflation":
    st.title("🔥 Inflation")

    tab1, tab2 = st.tabs(["📊 CPI by Country", "🌡️ Real Rates"])

    with tab1:
        st.subheader("CPI Inflation — Year-on-Year %")

        cpi_map = {
            "cpi_us":"US","cpi_uk":"UK","cpi_de":"Germany",
            "cpi_fr":"France","cpi_it":"Italy","cpi_jp":"Japan",
            "cpi_ca":"Canada","cpi_au":"Australia","cpi_ch":"Switzerland",
            "cpi_se":"Sweden","cpi_no":"Norway","cpi_kr":"S. Korea",
            "cpi_cn":"China","cpi_br":"Brazil","cpi_mx":"Mexico",
        }

        inf_rows = []
        for n, lbl in cpi_map.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            inf_rows.append({
                "Country": lbl,
                "YoY Inflation (%)": f"{r['yoy_pct']:.2f}"
                                     if pd.notna(r.get("yoy_pct")) else "—",
                "Last Date": r["last_date"],
            })

        inf_df = pd.DataFrame(inf_rows)
        if not inf_df.empty and "YoY Inflation (%)" in inf_df.columns:
            inf_df["_sort"] = pd.to_numeric(
                inf_df["YoY Inflation (%)"].replace("—", None), errors="coerce"
            )
            inf_df = inf_df.sort_values("_sort", ascending=False).drop("_sort", axis=1)

        st.dataframe(inf_df, hide_index=True, use_container_width=True)

        sel_cpi = st.multiselect(
            "Select countries",
            options=list(cpi_map.keys()),
            default=["cpi_us","cpi_de","cpi_uk","cpi_jp"],
            format_func=lambda x: cpi_map[x]
        )
        if sel_cpi:
            cpi_series = {}
            for n in sel_cpi:
                df = load_series(n)
                if df is not None and "yoy_pct" in df.columns:
                    cpi_series[cpi_map[n]] = (
                        df[["date","yoy_pct"]]
                        .rename(columns={"yoy_pct":"value"})
                        .dropna()
                    )
            if cpi_series:
                fig = plot_multi(cpi_series, title="CPI Inflation YoY (%)",
                               ylabel="%", start=start_dt, end=end_dt)
                fig.add_hline(y=2, line_dash="dash", line_color="#999999",
                             annotation_text="2% target")
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Real Interest Rates")
        st.caption("Real rate = 10Y nominal yield − CPI YoY inflation. "
                   "Positive = restrictive, Negative = accommodative.")

        real_map = {
            "real_rate_us":"US","real_rate_de":"Germany",
            "real_rate_uk":"UK","real_rate_jp":"Japan",
            "real_rate_fr":"France","real_rate_it":"Italy",
            "real_rate_ca":"Canada","real_rate_au":"Australia",
        }

        rr_rows = []
        for n, lbl in real_map.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            rr_rows.append({
                "Country": lbl,
                "Real Rate (%)": f"{r['last_value']:.2f}",
                "1M Δ": abs_fmt(r.get("chg_1m_abs"), 2)
                        if pd.notna(r.get("chg_1m_abs")) else "—",
            })
        st.dataframe(pd.DataFrame(rr_rows), hide_index=True, use_container_width=True)

        sel_rr = st.multiselect(
            "Select countries",
            options=list(real_map.keys()),
            default=list(real_map.keys()),
            format_func=lambda x: real_map[x]
        )
        if sel_rr:
            fig = plot_multi(
                {real_map[n]: load_series(n) for n in sel_rr},
                title="Real Interest Rates (%)", ylabel="%",
                start=start_dt, end=end_dt
            )
            fig.add_hline(y=0, line_dash="dash", line_color="#999999")
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE: ECONOMY
# ══════════════════════════════════════════════════════════════════
elif page == "💼 Economy":
    st.title("💼 Economy")

    tab1, tab2, tab3 = st.tabs([
        "📈 GDP Growth", "👷 Labour Market", "💰 Money Supply"
    ])

    with tab1:
        st.subheader("GDP Growth — IMF Annual (%)")

        @st.cache_data(ttl=3600)
        def load_imf_gdp():
            raw = Path("data")
            countries = {
                "us":"US","uk":"UK","de":"Germany","fr":"France","jp":"Japan",
                "cn":"China","in":"India","br":"Brazil","ca":"Canada","au":"Australia",
                "kr":"S. Korea","mx":"Mexico","it":"Italy","es":"Spain","id":"Indonesia",
                "nl":"Netherlands","sa":"Saudi Arabia","tr":"Turkey","za":"S. Africa",
                "pl":"Poland","se":"Sweden","no":"Norway","be":"Belgium","at":"Austria",
            }
            rows = []
            for code, name in countries.items():
                path = raw / f"imf_gdp_growth_{code}.csv"
                if not path.exists():
                    continue
                try:
                    df = pd.read_csv(path, parse_dates=["date"]).dropna().sort_values("date")
                    last = df.iloc[-1]
                    rows.append({
                        "Country":        name,
                        "GDP Growth (%)": round(last["value"], 2),
                        "Year":           int(last["date"].year),
                    })
                except Exception:
                    pass
            return pd.DataFrame(rows).sort_values("GDP Growth (%)", ascending=False)

        gdp_df = load_imf_gdp()
        if gdp_df.empty:
            st.warning("No GDP data found.")
        else:
            st.dataframe(gdp_df, hide_index=True, use_container_width=True)

    with tab2:
        st.subheader("Unemployment Rate (%)")

        unemp_map = {
            "unemp_us":"US","unemp_uk":"UK","unemp_de":"Germany",
            "unemp_fr":"France","unemp_it":"Italy","unemp_jp":"Japan",
            "unemp_ca":"Canada","unemp_au":"Australia",
            "unemp_se":"Sweden","unemp_kr":"S. Korea",
        }

        u_rows = []
        for n, lbl in unemp_map.items():
            r = summary[summary["name"] == n]
            if r.empty:
                continue
            r = r.iloc[0]
            u_rows.append({
                "Country": lbl,
                "Unemployment (%)": f"{r['last_value']:.1f}",
                "1M Δ": abs_fmt(r.get("chg_1m_abs"), 1)
                        if pd.notna(r.get("chg_1m_abs")) else "—",
                "1Y Δ": abs_fmt(r.get("chg_1y_abs"), 1)
                        if pd.notna(r.get("chg_1y_abs")) else "—",
            })
        st.dataframe(pd.DataFrame(u_rows), hide_index=True, use_container_width=True)

        sel_unemp = st.multiselect(
            "Select countries",
            options=list(unemp_map.keys()),
            default=["unemp_us","unemp_de","unemp_uk","unemp_jp"],
            format_func=lambda x: unemp_map[x]
        )
        if sel_unemp:
            fig = plot_multi(
                {unemp_map[n]: load_series(n) for n in sel_unemp},
                title="Unemployment Rate (%)", ylabel="%",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Money Supply")

        money_map = {
            "m2_us":      "M2 US",
            "m2_uk":      "M2 UK",
            "m2_jp":      "M2 Japan",
            "m2_cn":      "M2 China",
            "ecb_m3_ea":  "M3 Eurozone",
            "ecb_m1_ea":  "M1 Eurozone",
        }

        sel_money = st.multiselect(
            "Select series",
            options=list(money_map.keys()),
            default=["m2_us","ecb_m3_ea","m2_cn"],
            format_func=lambda x: money_map[x]
        )
        if sel_money:
            fig = plot_normalized(
                {money_map[n]: load_series(n) for n in sel_money},
                title="Money Supply Growth — normalized to 0%",
                start=start_dt, end=end_dt
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# PAGE: COMPARE
# ══════════════════════════════════════════════════════════════════
elif page == "🔀 Compare":
    st.title("🔀 Custom Comparison")
    st.markdown(
        "Pick **any combination** of series — across categories, countries, or asset classes — "
        "and compare them on a single chart. Use the normalized view to see who's up and who's down."
    )

    all_meta = summary[["name","description","category","country"]].copy()
    all_meta["label"] = all_meta["description"] + "  [" + all_meta["country"] + "]"

    col1, col2 = st.columns([1, 3])

    with col1:
        cat_sel = st.multiselect(
            "Filter by category",
            options=sorted(summary["category"].dropna().unique()),
            default=[]
        )

    filtered_meta = all_meta[all_meta["category"].isin(cat_sel)] \
                    if cat_sel else all_meta

    with col2:
        sel_compare = st.multiselect(
            "Select series",
            options=filtered_meta["name"].tolist(),
            format_func=lambda x: all_meta[all_meta["name"]==x]["label"].iloc[0]
                        if not all_meta[all_meta["name"]==x].empty else x,
            default=filtered_meta["name"].tolist()[:3]
                    if not filtered_meta.empty else []
        )

    chart_mode = st.radio(
        "Chart mode",
        ["📊 Normalized — % change from start (zero baseline)",
         "📈 Absolute values"],
        horizontal=True
    )

    if sel_compare:
        compare_data = {}
        for n in sel_compare:
            row = all_meta[all_meta["name"] == n]
            lbl = row["label"].iloc[0] if not row.empty else n
            df  = load_series(n)
            if df is not None:
                compare_data[lbl] = df

        if compare_data:
            if "Normalized" in chart_mode:
                fig = plot_normalized(
                    compare_data,
                    title="Custom Comparison — % change from start of period",
                    start=start_dt, end=end_dt
                )
                st.caption(
                    "All series rebase to 0% at the start of your selected time range. "
                    "Above the line = gain, below = loss."
                )
            else:
                fig = plot_multi(
                    compare_data,
                    title="Custom Comparison — Absolute values",
                    start=start_dt, end=end_dt
                )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Current values")
            cmp_tbl = summary[summary["name"].isin(sel_compare)][
                [c for c in ["description","category","country","last_date",
                             "last_value","chg_1w_pct","chg_1m_pct",
                             "chg_1y_pct","yoy_pct"]
                 if c in summary.columns]
            ].rename(columns={
                "description":"Series","category":"Category",
                "country":"Country","last_date":"Date",
                "last_value":"Value","chg_1w_pct":"1W %",
                "chg_1m_pct":"1M %","chg_1y_pct":"1Y %","yoy_pct":"YoY %"
            })
            st.dataframe(cmp_tbl, hide_index=True, use_container_width=True)