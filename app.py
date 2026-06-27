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
# ══════════════════════════════════════════════════════════════════
# CENTRALE BANK MAPPINGS — voor de wereldkaart
# ══════════════════════════════════════════════════════════════════

COUNTRY_CB = {
    # Noord-Amerika
    "USA": ("FED",     "Federal Reserve"),
    "CAN": ("BOC",     "Bank of Canada"),
    "MEX": ("BANXICO", "Banco de México"),
    # Eurozone
    "AUT": ("ECB", "European Central Bank"),
    "BEL": ("ECB", "European Central Bank"),
    "HRV": ("ECB", "European Central Bank"),
    "CYP": ("ECB", "European Central Bank"),
    "EST": ("ECB", "European Central Bank"),
    "FIN": ("ECB", "European Central Bank"),
    "FRA": ("ECB", "European Central Bank"),
    "DEU": ("ECB", "European Central Bank"),
    "GRC": ("ECB", "European Central Bank"),
    "IRL": ("ECB", "European Central Bank"),
    "ITA": ("ECB", "European Central Bank"),
    "LVA": ("ECB", "European Central Bank"),
    "LTU": ("ECB", "European Central Bank"),
    "LUX": ("ECB", "European Central Bank"),
    "MLT": ("ECB", "European Central Bank"),
    "NLD": ("ECB", "European Central Bank"),
    "PRT": ("ECB", "European Central Bank"),
    "SVK": ("ECB", "European Central Bank"),
    "SVN": ("ECB", "European Central Bank"),
    "ESP": ("ECB", "European Central Bank"),
    # Overig Europa
    "GBR": ("BOE",      "Bank of England"),
    "CHE": ("SNB",      "Swiss National Bank"),
    "SWE": ("RIKSBANK", "Riksbank"),
    "NOR": ("NORGES",   "Norges Bank"),
    "DNK": ("DNB",      "Danmarks Nationalbank"),
    "POL": ("NBP",      "Narodowy Bank Polski"),
    "HUN": ("MNB",      "Magyar Nemzeti Bank"),
    "CZE": ("CNB",      "Czech National Bank"),
    "ROU": ("BNR",      "Banca Nationala a Romaniei"),
    "RUS": ("CBR",      "Bank of Russia"),
    "TUR": ("TCMB",     "Central Bank of Turkey"),
    "UKR": ("NBU",      "National Bank of Ukraine"),
    "ISL": ("CBI",      "Central Bank of Iceland"),
    # Azië-Pacific
    "JPN": ("BOJ",  "Bank of Japan"),
    "CHN": ("PBOC", "People's Bank of China"),
    "KOR": ("BOK",  "Bank of Korea"),
    "AUS": ("RBA",  "Reserve Bank of Australia"),
    "NZL": ("RBNZ", "Reserve Bank of New Zealand"),
    "IND": ("RBI",  "Reserve Bank of India"),
    "IDN": ("BI",   "Bank Indonesia"),
    "SGP": ("MAS",  "Monetary Authority of Singapore"),
    "HKG": ("HKMA", "Hong Kong Monetary Authority"),
    "THA": ("BOT",  "Bank of Thailand"),
    "MYS": ("BNM",  "Bank Negara Malaysia"),
    "PHL": ("BSP",  "Bangko Sentral ng Pilipinas"),
    "VNM": ("SBV",  "State Bank of Vietnam"),
    "BGD": ("BB",   "Bangladesh Bank"),
    "PAK": ("SBP",  "State Bank of Pakistan"),
    "TWN": ("CBC",  "Central Bank of the ROC"),
    # Amerika's
    "BRA": ("BCB",    "Banco Central do Brasil"),
    "ARG": ("BCRA",   "Banco Central de Argentina"),
    "CHL": ("BCCh",   "Banco Central de Chile"),
    "COL": ("BANREP", "Banco de la Republica"),
    "PER": ("BCRP",   "Banco Central de Reserva del Peru"),
    # Midden-Oosten & Afrika
    "SAU": ("SAMA",   "Saudi Central Bank"),
    "ARE": ("CBUAE",  "Central Bank of UAE"),
    "ISR": ("BOI",    "Bank of Israel"),
    "ZAF": ("SARB",   "SA Reserve Bank"),
    "NGA": ("CBN",    "Central Bank of Nigeria"),
    "EGY": ("CBE",    "Central Bank of Egypt"),
    "KEN": ("CBK",    "Central Bank of Kenya"),
    "GHA": ("BOG",    "Bank of Ghana"),
    "ETH": ("NBE",    "National Bank of Ethiopia"),
    "TZA": ("BOTTZ",  "Bank of Tanzania"),
    "MAR": ("BAM",    "Bank Al-Maghrib"),
    "KWT": ("CBK_KW", "Central Bank of Kuwait"),
    "QAT": ("QCB",    "Qatar Central Bank"),
}

CB_COLORS = {
    "FED":     "#1D4ED8", "ECB":     "#6D28D9", "BOE":     "#BE123C",
    "BOJ":     "#C2410C", "BOC":     "#B45309", "RBA":     "#166534",
    "RBNZ":    "#15803D", "SNB":     "#DC2626", "RIKSBANK":"#0E7490",
    "NORGES":  "#155E75", "DNB":     "#1E40AF", "NBP":     "#7C3AED",
    "MNB":     "#9333EA", "CNB":     "#A855F7", "BNR":     "#C084FC",
    "CBR":     "#991B1B", "TCMB":    "#7C2D12", "NBU":     "#1E3A8A",
    "CBI":     "#2563EB", "PBOC":    "#DC2626", "BOK":     "#2563EB",
    "RBI":     "#EA580C", "BI":      "#0D9488", "MAS":     "#065F46",
    "HKMA":    "#1E3A5F", "BOT":     "#7C3AED", "BNM":     "#047857",
    "BSP":     "#1D4ED8", "SBV":     "#BE123C", "BB":      "#064E3B",
    "SBP":     "#047857", "CBC":     "#BE185D", "BCB":     "#16A34A",
    "BCRA":    "#92400E", "BCCh":    "#0369A1", "BANREP":  "#CA8A04",
    "BCRP":    "#0891B2", "BANXICO": "#B45309", "SAMA":    "#065F46",
    "CBUAE":   "#0369A1", "BOI":     "#1D4ED8", "SARB":    "#7C2D12",
    "CBN":     "#166534", "CBE":     "#92400E", "CBK":     "#047857",
    "BOG":     "#B45309", "NBE":     "#064E3B", "BOTTZ":   "#065F46",
    "BAM":     "#1E40AF", "CBK_KW":  "#4338CA", "QCB":     "#7C3AED",
    "OTHER":   "#9CA3AF",
}

CB_RATE_SERIES = {
    "FED":      ("rate_us",         "FED"),
    "ECB":      ("ecb_ecb_deposit", "ECB"),
    "BOE":      ("rate_uk",         "BoE"),
    "BOJ":      ("rate_jp",         "BoJ"),
    "BOC":      ("rate_ca",         "BoC"),
    "RBA":      ("rate_au",         "RBA"),
    "RBNZ":     ("rate_nz",         "RBNZ"),
    "SNB":      ("rate_ch",         "SNB"),
    "RIKSBANK": ("rate_se",         "Riksbank"),
    "NORGES":   ("rate_no",         "Norges"),
    "BOK":      ("rate_kr",         "BoK"),
    "BANXICO":  ("rate_mx",         "Banxico"),
    "BCB":      ("rate_br",         "BCB"),
    "RBI":      ("rate_in",         "RBI"),
    "SARB":     ("rate_za",         "SARB"),
    "PBOC":     ("rate_cn",         "PBoC"),
    "TCMB":     ("rate_tr",         "TCMB"),
    "NBP":      ("rate_pl",         "NBP"),
    "MNB":      ("rate_hu",         "MNB"),
    "CNB":      ("rate_cz",         "CNB"),
    "BI":       ("rate_id",         "BI"),
    "HKMA":     ("rate_hk",         "HKMA"),
    "BOI":      ("rate_il",         "BoI"),
    "BCCh":     ("rate_cl",         "BCCh"),
}

# Lat/lon voor rate-labels op de kaart
CB_POSITIONS = {
    "FED":      (39.5,  -98.0), "ECB":     (50.5,   9.0),
    "BOE":      (54.5,  -2.5),  "BOJ":     (36.0,  138.0),
    "BOC":      (60.0,  -96.0), "RBA":     (-25.0, 133.0),
    "RBNZ":     (-41.5, 173.0), "SNB":     (47.0,    8.5),
    "RIKSBANK": (62.0,   16.0), "NORGES":  (64.5,   11.0),
    "PBOC":     (35.0,  103.0), "BOK":     (36.5,  128.0),
    "RBI":      (20.0,   79.0), "BCB":     (-14.0,  -53.0),
    "BANXICO":  (23.5, -102.0), "SARB":    (-29.0,   25.0),
    "CBR":      (61.0,  100.0), "TCMB":    (39.0,   35.0),
    "BI":       (-5.0,  120.0), "BCCh":    (-35.0,  -71.0),
    "BOI":      (31.0,   35.0), "SAMA":    (24.0,   45.0),
}

CB_BS_CONFIG = {
    "Federal Reserve (Fed)": {
        "code": "FED", "country": "United States",
        "bs_series": "bs_fed", "rate_series": "rate_us",
        "rate_label": "Fed Funds Rate",
        "display_unit": "Trillions USD", "scale": 1_000_000,
        "current": True,
    },
    "European Central Bank (ECB)": {
        "code": "ECB", "country": "Eurozone",
        "bs_series": "bs_ecb", "rate_series": "ecb_ecb_deposit",
        "rate_label": "ECB Deposit Rate",
        "display_unit": "Trillions EUR", "scale": 1_000_000,
        "current": True,
    },
    "Bank of Japan (BoJ)": {
        "code": "BOJ", "country": "Japan",
        "bs_series": "bs_boj", "rate_series": "rate_jp",
        "rate_label": "BoJ Policy Rate",
        "display_unit": "Trillions JPY", "scale": 1_000_000,
        "current": True,
    },
    "Bank of England (BoE)": {
        "code": "BOE", "country": "United Kingdom",
        "bs_series": "bs_boe", "rate_series": "rate_uk",
        "rate_label": "BoE Base Rate",
        "display_unit": "Billions GBP", "scale": 1_000,
        "current": False,
        "note": "Historical balance sheet data only (to 2016). No active FRED series available for BoE.",
    },
}

IMF_CA_COUNTRIES = {
    "ae": "ARE", "ar": "ARG", "at": "AUT", "au": "AUS",
    "bd": "BGD", "be": "BEL", "br": "BRA", "ca": "CAN",
    "ch": "CHE", "cl": "CHL", "cn": "CHN", "co": "COL",
    "cz": "CZE", "de": "DEU", "dk": "DNK", "eg": "EGY",
    "es": "ESP", "et": "ETH", "fi": "FIN", "fr": "FRA",
    "gh": "GHA", "gr": "GRC", "hk": "HKG", "hu": "HUN",
    "id": "IDN", "ie": "IRL", "il": "ISR", "in": "IND",
    "it": "ITA", "jp": "JPN", "ke": "KEN", "kr": "KOR",
    "kw": "KWT", "ma": "MAR", "mx": "MEX", "my": "MYS",
    "ng2":"NGA", "nl": "NLD", "no": "NOR", "nz": "NZL",
    "ph": "PHL", "pk": "PAK", "pl": "POL", "pt": "PRT",
    "qa": "QAT", "ro": "ROU", "ru": "RUS", "sa": "SAU",
    "se": "SWE", "sg": "SGP", "th": "THA", "tr": "TUR",
    "tz": "TZA", "ua": "UKR", "uk": "GBR", "us": "USA",
    "vn": "VNM", "za": "ZAF",
}

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
            df = pd.read_csv(path, parse_dates=["date"]).dropna()
            df["year"] = df["date"].dt.year
            df = df[df["year"] <= 2025]
            if df.empty:
                continue
            last = df.sort_values("date").iloc[-1]
            rows.append({
                "Country":        name,
                "GDP Growth (%)": round(float(last["value"]), 2),
                "Year":           int(last["year"]),
            })
        except Exception:
            pass
    if not rows:
        return pd.DataFrame(columns=["Country", "GDP Growth (%)", "Year"])
    return pd.DataFrame(rows).sort_values("GDP Growth (%)", ascending=False)

#@st.cache_data(ttl=3600)
def load_compass(region):
    """Laad JSON-kompasdata voor een regio (us / eu / global)."""
    import json
    path = PROC / f"compass_{region}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
    
@st.cache_data(ttl=3600)
def load_current_account_map():
    """Laad voorverwerkte current account kaartdata vanuit data/processed/."""
    path = PROC / "current_account_map.csv"
    if not path.exists():
        return pd.DataFrame(columns=["iso3", "value", "year"])
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=["iso3", "value", "year"])

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

def make_quadrant_chart(growth_dir, inflation_dir):
    """2×2 quadrant visualization with current position marker."""
    fig = go.Figure()

    # Quadrant backgrounds
    for x0, y0, x1, y1, color in [
        (-1,  0,  0,  1, "#DCFCE7"),  # Q1 Goldilocks — green
        ( 0,  0,  1,  1, "#FEF9C3"),  # Q2 Overheating — yellow
        ( 0, -1,  1,  0, "#FEE2E2"),  # Q3 Stagflation — red
        (-1, -1,  0,  0, "#DBEAFE"),  # Q4 Recession — blue
    ]:
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=color, opacity=0.9, line_width=0)

    # Quadrant labels + asset hints
    for x, y, title, hint in [
        (-0.5,  0.70, "<b>Q1 — Goldilocks</b>",  "Equities · Corp. Bonds"),
        ( 0.5,  0.70, "<b>Q2 — Overheating</b>", "Commodities · TIPS · Gold"),
        ( 0.5, -0.70, "<b>Q3 — Stagflation</b>", "Cash · Gold"),
        (-0.5, -0.70, "<b>Q4 — Recession</b>",   "Gov. Bonds · Defensive Eq."),
    ]:
        fig.add_annotation(x=x, y=y,       text=title, showarrow=False,
                           font=dict(size=11, color="#374151"), align="center")
        fig.add_annotation(x=x, y=y - 0.18, text=hint, showarrow=False,
                           font=dict(size=9,  color="#6B7280"), align="center")

    # Axes
    fig.add_shape(type="line", x0=-1, y0=0, x1=1, y1=0,
                  line=dict(color="#9CA3AF", width=1.5))
    fig.add_shape(type="line", x0=0, y0=-1, x1=0, y1=1,
                  line=dict(color="#9CA3AF", width=1.5))

    # Axis labels
    for x, y, txt, xanchor in [
        (-0.75, -1.15, "← Inflation falling", "center"),
        ( 0.75, -1.15, "Inflation rising →",  "center"),
        (-1.20,  0.50, "Growth ↑", "right"),
        (-1.20, -0.50, "Growth ↓", "right"),
    ]:
        fig.add_annotation(x=x, y=y, text=txt, showarrow=False,
                           font=dict(size=10, color="#6B7280"), xanchor=xanchor)

    # Current position — large black dot with label
    fig.add_trace(go.Scatter(
        x=[inflation_dir * 0.5], y=[growth_dir * 0.5],
        mode="markers+text",
        text=["  ◀ NOW"],
        textposition="middle right",
        textfont=dict(size=12, color="#000000", family="Arial Black"),
        marker=dict(size=32, color="#000000", symbol="circle",
                    line=dict(color="white", width=4)),
        showlegend=False,
        hovertemplate="Current position<extra></extra>",
    ))

    fig.update_layout(
        height=340, plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=65, r=20, t=20, b=55),
        xaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor="x", scaleratio=1),
    )
    return fig

def make_history_chart(history):
    """Colored timeline strip — one bar per month, colored by quadrant."""
    if not history:
        return go.Figure()

    q_color = {1: "#16A34A", 2: "#D97706", 3: "#DC2626",
               4: "#2563EB", 0: "#9CA3AF"}
    q_label = {1: "Q1 Goldilocks", 2: "Q2 Overheating",
               3: "Q3 Stagflation", 4: "Q4 Recession", 0: "Transition"}

    dates  = [h["date"]                          for h in history]
    colors = [q_color[h["quadrant"]]             for h in history]
    texts  = [q_label[h["quadrant"]]             for h in history]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates, y=[1] * len(dates),
        marker=dict(color=colors, line=dict(width=0.5, color="white")),
        customdata=texts,
        hovertemplate="%{x}: %{customdata}<extra></extra>",
        showlegend=False,
    ))

    # Legend entries (only for quadrants that actually appear)
    seen = set()
    for h in history:
        q = h["quadrant"]
        if q not in seen:
            seen.add(q)
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                marker_color=q_color[q],
                name=q_label[q],
                showlegend=True,
            ))

    fig.update_layout(
        height=110,
        margin=dict(l=0, r=0, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.05,
        yaxis=dict(showticklabels=False, showgrid=False,
                   zeroline=False, range=[0, 1.1]),
        xaxis=dict(showgrid=False, tickformat="%b %Y"),
        legend=dict(orientation="h", yanchor="bottom", y=-1.0, x=0),
    )
    return fig

def build_monetary_map(summary_df):
    """Choropleth gekleurd per centrale bank-zone met rentevoet-labels."""
    all_cbs = sorted(set(v[0] for v in COUNTRY_CB.values()))
    cb_to_idx = {cb: i for i, cb in enumerate(all_cbs)}
    n = len(all_cbs)

    locations, z_vals, cb_codes, hover_texts = [], [], [], []
    for iso3, (cb_code, cb_name) in COUNTRY_CB.items():
        locations.append(iso3)
        z_vals.append(cb_to_idx.get(cb_code, 0))
        cb_codes.append(cb_code)
        hover_texts.append(f"<b>{iso3}</b><br>{cb_name}")

    colorscale = []
    for i, cb in enumerate(all_cbs):
        color = CB_COLORS.get(cb, "#9CA3AF")
        colorscale.append([i / n, color])
        colorscale.append([(i + 1) / n, color])

    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=locations,
        z=z_vals,
        colorscale=colorscale,
        zmin=0, zmax=n,
        showscale=False,
        locationmode="ISO-3",
        customdata=cb_codes,
        text=hover_texts,
        hovertemplate="%{text}<extra></extra>",
        marker_line_color="white",
        marker_line_width=0.4,
    ))

    # Rentevoet-labels
    for cb_id, (lat, lon) in CB_POSITIONS.items():
        info = CB_RATE_SERIES.get(cb_id)
        if info is None:
            continue
        series_name, short = info
        row = summary_df[summary_df["name"] == series_name]
        if row.empty:
            continue
        rate = row.iloc[0].get("last_value")
        chg  = row.iloc[0].get("chg_1m_abs")
        if pd.isna(rate):
            continue
        arrow = " \u2192"
        if pd.notna(chg):
            arrow = " \u2191" if chg > 0.01 else (" \u2193" if chg < -0.01 else " \u2192")
        fig.add_trace(go.Scattergeo(
            lat=[lat], lon=[lon], mode="text",
            text=[f"<b>{short}<br>{rate:.2f}%{arrow}</b>"],
            textfont=dict(size=8, color="white"),
            showlegend=False, hoverinfo="skip",
        ))

    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="#CBD5E1", coastlinewidth=0.5,
            showland=True, landcolor="#F1F5F9",
            showocean=True, oceancolor="#DBEAFE",
            showlakes=False, projection_type="natural earth",
            bgcolor="white",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white", height=520,
    )
    return fig


def build_trade_map(ca_df):
    """Choropleth van lopende rekening % BBP."""
    if ca_df.empty:
        return go.Figure()
    fig = go.Figure(go.Choropleth(
        locations=ca_df["iso3"],
        z=ca_df["value"],
        colorscale=[
            [0.0,  "#DC2626"], [0.35, "#FCA5A5"],
            [0.5,  "#F3F4F6"], [0.65, "#86EFAC"],
            [1.0,  "#166534"],
        ],
        zmid=0, zmin=-15, zmax=15,
        locationmode="ISO-3",
        colorbar=dict(
            title=dict(text="Current Account<br>% of GDP", side="right"),
            ticksuffix="%", len=0.7,
        ),
        hovertemplate=(
            "<b>%{location}</b><br>"
            "Current Account: %{z:.1f}% of GDP<extra></extra>"
        ),
        marker_line_color="white", marker_line_width=0.4,
    ))
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="#CBD5E1", coastlinewidth=0.5,
            showland=True, landcolor="#F1F5F9",
            showocean=True, oceancolor="#DBEAFE",
            showlakes=False, projection_type="natural earth",
            bgcolor="white",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white", height=520,
    )
    return fig


def render_map_detail(iso3, summary_df, ca_df):
    """Rechterpaneel na klikken op een land."""
    if iso3 is None:
        st.markdown("### 👆 Click a country")
        st.caption("Select any country on the map to see its monetary and economic details.")
        return

    cb_info = COUNTRY_CB.get(iso3)
    if cb_info is None:
        st.markdown(f"### {iso3}")
        st.caption("No central bank data mapped for this country.")
        return

    cb_code, cb_full_name = cb_info
    cb_color = CB_COLORS.get(cb_code, "#9CA3AF")

    st.markdown(f"### {iso3}")
    st.markdown(
        f'<div style="background:{cb_color};color:white;padding:5px 12px;'
        f'border-radius:6px;display:inline-block;font-size:13px;'
        f'font-weight:bold;margin-bottom:8px;">{cb_code}</div>',
        unsafe_allow_html=True,
    )
    st.caption(cb_full_name)
    st.markdown("---")

    # Rentevoet
    rate_info = CB_RATE_SERIES.get(cb_code)
    if rate_info:
        series_name, rate_label = rate_info
        row = summary_df[summary_df["name"] == series_name]
        if not row.empty:
            rate_val = row.iloc[0].get("last_value")
            chg      = row.iloc[0].get("chg_1m_abs")
            arrow    = " \u2192"
            if pd.notna(chg):
                arrow = " \u2191" if chg > 0.01 else (" \u2193" if chg < -0.01 else " \u2192")
            st.metric(
                label=f"Policy Rate ({rate_label})",
                value=f"{rate_val:.2f}%{arrow}" if pd.notna(rate_val) else "—",
                delta=f"{chg*100:+.0f} bps vs last month" if pd.notna(chg) else None,
            )

    # Balans centrale bank
    bs_cfg = next(
        (cfg for cfg in CB_BS_CONFIG.values() if cfg["code"] == cb_code),
        None
    )
    if bs_cfg:
        bs_df = load_series(bs_cfg["bs_series"])
        if bs_df is not None and not bs_df.empty:
            scale = bs_cfg["scale"]
            last  = bs_df.iloc[-1]
            val   = float(last["value"]) / scale
            yoy   = last.get("yoy_pct")
            peak_pct = last.get("pct_from_peak")
            st.metric(
                label=f"Balance Sheet ({bs_cfg['display_unit']})",
                value=f"{val:,.2f}",
                delta=f"{yoy:+.1f}% YoY" if pd.notna(yoy) else None,
            )
            if pd.notna(peak_pct) and peak_pct < -0.5:
                st.caption(f"📉 {peak_pct:.1f}% below all-time peak")
            if not bs_cfg.get("current", True):
                st.caption("⚠️ Historical data only (to 2016)")

    st.markdown("---")

    # Lopende rekening
    if not ca_df.empty:
        ca_row = ca_df[ca_df["iso3"] == iso3]
        if not ca_row.empty:
            ca_val  = ca_row.iloc[0]["value"]
            ca_year = int(ca_row.iloc[0]["year"])
            icon    = "🟢" if ca_val >= 0 else "🔴"
            label   = "Surplus" if ca_val >= 0 else "Deficit"
            st.metric(
                label=f"Current Account % GDP ({ca_year})",
                value=f"{ca_val:+.1f}%",
                delta=f"{icon} {label}",
                delta_color="off",
            )


def render_cb_balance_tab(cb_name, config, start_dt, end_dt):
    """Balansblad en rentevoet voor één centrale bank."""
    if not config.get("current", True):
        st.warning(config.get("note", "Limited data available."))

    bs_df   = load_series(config["bs_series"])
    rate_df = load_series(config["rate_series"])

    if bs_df is None or bs_df.empty:
        st.info(
            f"Balance sheet data for {cb_name} not yet available. "
            "Run `python collectors/bs_collector.py` then `python process.py`."
        )
        return

    scale = config["scale"]
    bs_disp = bs_df.copy()
    bs_disp["value"] = bs_disp["value"] / scale

    last      = bs_df.iloc[-1]
    current   = float(last["value"]) / scale
    yoy       = last.get("yoy_pct")
    peak_pct  = last.get("pct_from_peak")
    peak_idx  = bs_df["value"].idxmax()
    peak_val  = float(bs_df.loc[peak_idx, "value"]) / scale
    peak_date = bs_df.loc[peak_idx, "date"]

    rate_val   = float(rate_df["value"].iloc[-1])  if rate_df is not None else None
    rate_chg   = float(rate_df["chg_1m"].iloc[-1]) if (rate_df is not None and "chg_1m" in rate_df.columns) else None
    rate_arrow = " \u2192"
    if rate_chg is not None:
        rate_arrow = " \u2191" if rate_chg > 0.01 else (" \u2193" if rate_chg < -0.01 else " \u2192")

    # Metrickaarten
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            config["rate_label"],
            f"{rate_val:.2f}%{rate_arrow}" if rate_val is not None else "—",
            delta=f"{rate_chg*100:+.0f} bps vs last month" if rate_chg is not None else None,
        )
    with c2:
        st.metric(
            f"Balance Sheet ({config['display_unit']})",
            f"{current:,.2f}",
            delta=f"{yoy:+.1f}% YoY" if pd.notna(yoy) else None,
        )
    with c3:
        st.metric(
            "All-Time Peak",
            f"{peak_val:,.2f}",
            delta=peak_date.strftime("%b %Y"),
            delta_color="off",
        )
    with c4:
        st.metric(
            "vs. Peak",
            f"{peak_pct:+.1f}%" if pd.notna(peak_pct) else "—",
            delta_color="off",
        )

    st.markdown("---")

    # Grafieken
    col_bs, col_rate = st.columns(2)
    with col_bs:
        fig = plot_line(
            bs_disp,
            title=f"Balance Sheet ({config['display_unit']})",
            ylabel=config["display_unit"],
            color="#2563EB",
            start=start_dt, end=end_dt,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_rate:
        if rate_df is not None:
            fig = plot_line(
                rate_df,
                title=f"{config['rate_label']} (%)",
                ylabel="%",
                color="#DC2626",
                start=start_dt, end=end_dt,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Rate data not available.")

    # YoY-verandering grafiek
    if "yoy_pct" in bs_df.columns:
        yoy_df = (bs_df[["date", "yoy_pct"]]
                  .dropna()
                  .rename(columns={"yoy_pct": "value"}))
        if start_dt:
            yoy_df = yoy_df[yoy_df["date"] >= pd.Timestamp(start_dt)]
        if not yoy_df.empty:
            st.markdown("---")
            fig2 = plot_line(
                yoy_df,
                title="Balance Sheet — Year-on-Year Change (%)",
                ylabel="%",
                color="#7C3AED",
            )
            fig2.add_hline(y=0, line_dash="dash", line_color="#9CA3AF")
            st.plotly_chart(fig2, use_container_width=True)

def render_compass(data):
    """Render one compass tab from JSON data."""
    if data is None:
        st.warning("Compass data not available. Check that compass.py ran correctly.")
        return

    q   = data["quadrant"]
    g   = data["growth"]
    inf = data["inflation"]

    # ── Regime header ──────────────────────────────────────────────
    q_num     = q["number"]
    stability = q["stability_months"]
    stab_txt  = f"{stability} {'month' if stability == 1 else 'months'}"
    msg = (f"**Quadrant {q_num} — {q['label']}** &nbsp;·&nbsp; "
           f"{q['description']} &nbsp;·&nbsp; Stability: {stab_txt}")

    if   q_num == 1: st.success(msg)
    elif q_num == 2: st.warning(msg)
    elif q_num == 3: st.error(msg)
    elif q_num == 4: st.info(msg)
    else:            st.info(f"**Transition** &nbsp;·&nbsp; {q['description']}")

    st.caption(f"Compass calculated: {data.get('timestamp', '—')}")

    # ── Quadrant chart + axis details ──────────────────────────────
    col_chart, col_axes = st.columns([3, 2])

    with col_chart:
        st.plotly_chart(make_quadrant_chart(g["direction"], inf["direction"]),
                        use_container_width=True)

    with col_axes:
        arrows = {1: "↑ Rising", -1: "↓ Falling", 0: "→ Flat"}
        st.markdown("##### Growth axis")
        st.metric(
            label=g["indicator"],
            value=f"{g['value']:.2f}" if g.get("value") is not None else "—",
            delta=arrows[g["direction"]],
            delta_color="off",
        )
        bev = g.get("confirmation", {})
        if bev.get("value") is not None:
            bev_arrow = {1: "↑", -1: "↓", 0: "→"}.get(bev.get("direction", 0), "→")
            st.caption(f"Confirmation — {bev['indicator']}: "
                       f"{bev_arrow} ({bev['value']:.1f})")

        st.markdown("---")
        st.markdown("##### Inflation axis")
        st.metric(
            label=inf["indicator"],
            value=f"{inf['value']:.2f}%" if inf.get("value") is not None else "—",
            delta=arrows[inf["direction"]],
            delta_color="off",
        )
        if inf.get("date"):
            st.caption(f"Last data point: {str(inf['date'])[:7]}")

    st.markdown("---")

    # ── Asset class compass ────────────────────────────────────────
    st.subheader("Asset Class Compass")
    st.caption("Directional guidance based on the active macro regime — not a trading signal.")

    icon = {1: "🟢 Favorable", 0: "🟡 Neutral", -1: "🔴 Unfavorable"}
    assets = data.get("asset_signals", {})
    a_cols = st.columns(4)
    for i, (asset_name, val) in enumerate(assets.items()):
        with a_cols[i % 4]:
            st.metric(label=asset_name, value=icon.get(val, "—"))

    st.markdown("---")

    # ── Validation signals ─────────────────────────────────────────
    st.subheader("Validation Signals")
    st.caption("Market signals that confirm or contradict the active quadrant.")

    val_signals = data.get("validation", {})
    if val_signals:
        sig_icon = {1: "🟢", 0: "🟡", -1: "🔴"}
        rows = []
        for s in val_signals.values():
            duration   = s.get("duration_months", 0)
            assessment = f"{sig_icon.get(s.get('signal', 0), '🟡')}  {s.get('status', '—')}"
            if duration > 1 and s.get("signal", 0) != 1:
                assessment += f"  ({duration}m)"
            rows.append({
                "Indicator":  s.get("label", "—"),
                "Value":      f"{s['value']} {s.get('unit', '')}",
                "Assessment": assessment,
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        st.caption("🟢 Normal / Favorable  ·  🟡 Elevated / Watch  ·  🔴 Stress / Warning")

    # ── Regime history ─────────────────────────────────────────────
    history = data.get("history", [])
    if history:
        st.markdown("---")
        st.subheader("Regime History — last 5 years")
        st.caption(
            "Monthly quadrant assignments based on OECD CLI + CPI trend. "
            "Use this to validate the compass against known historical periods."
        )
        st.plotly_chart(make_history_chart(history), use_container_width=True)
        st.caption(
            "Historical reference: 2022 typically Q3 Stagflation · "
            "2020 Q4 Recession · 2019 / mid-2023 Q1 Goldilocks"
        )

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
    "🧭 Macro Compass",
    "🏛️ Central Banks",
    "🗺️ World Map",
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
    st.info(
    "🚧 **Work in progress** — This dashboard is a personal hobby project "
    "in active development. Many extensions (and fixes) are planned: additional data sources, "
    "AI-generated weekly reports, deeper analysis tools and more. "
    "Feedback, suggestions or collaboration ideas are always welcome — "
    "connect with me on [LinkedIn](https://www.linkedin.com/in/ruben-bosmans) "
    "or open an issue on [GitHub](https://github.com/Ruben-Bosmans/global-macro-dashboard/issues).",
    icon="💡"
    )

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
        gdp_df = load_imf_gdp()
        if gdp_df.empty:
            st.info("GDP data is only available in the local version of this app.")
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

# ══════════════════════════════════════════════════════════════════
# PAGE: MACRO COMPASS
# ══════════════════════════════════════════════════════════════════
elif page == "🧭 Macro Kompas":
    st.title("🧭 Macro Compass")
    st.markdown(
        "Strategic macro regime detector based on **growth** (OECD CLI) "
        "and **inflation** (CPI trend). Use this as a monthly compass "
        "for asset allocation — not as a daily trading signal."
    )

    tab_us, tab_eu, tab_global = st.tabs(["🇺🇸 US", "🇪🇺 Eurozone", "🌍 Global"])

    with tab_us:
        render_compass(load_compass("us"))

    with tab_eu:
        render_compass(load_compass("eu"))

    with tab_global:
        render_compass(load_compass("global"))

        data_global = load_compass("global")
        if data_global and "divergence" in data_global:
            div = data_global["divergence"]
            st.markdown("---")
            st.subheader("🔄 US vs Eurozone — Divergence")
            if div.get("actief"):
                us_arrow = {1: "↑", -1: "↓", 0: "→"}.get(div.get("us_groei", 0), "→")
                eu_arrow = {1: "↑", -1: "↓", 0: "→"}.get(div.get("eu_groei", 0), "→")
                st.warning(
                    f"**Divergence active** — US growth {us_arrow} vs "
                    f"EU growth {eu_arrow}. Potential relative value opportunities "
                    f"between US and European assets."
                )
            else:
                st.success("US and EU moving **in sync** — no significant divergence detected.")

# ══════════════════════════════════════════════════════════════════
# PAGE: CENTRAL BANKS
# ══════════════════════════════════════════════════════════════════
elif page == "🏛️ Central Banks":
    st.title("🏛️ Central Banks — Balance Sheets & Policy Rates")
    st.markdown(
        "Balance sheet evolution and policy rates for the four major central banks. "
        "Select a tab to switch institution."
    )
    tabs = st.tabs(list(CB_BS_CONFIG.keys()))
    for tab, (cb_name, config) in zip(tabs, CB_BS_CONFIG.items()):
        with tab:
            render_cb_balance_tab(cb_name, config, start_dt, end_dt)


# ══════════════════════════════════════════════════════════════════
# PAGE: WORLD MAP
# ══════════════════════════════════════════════════════════════════
elif page == "🗺️ World Map":
    st.title("🗺️ World Map")

    map_mode = st.selectbox(
        "Map view",
        ["🏦 Monetary Policy — CB Zones & Rates", "📊 Current Account % GDP"],
    )

    if "map_country" not in st.session_state:
        st.session_state["map_country"] = None

    ca_df = load_current_account_map()

    col_map, col_panel = st.columns([7, 3])

    with col_map:
        if "Monetary" in map_mode:
            fig = build_monetary_map(summary)
            st.caption(
                "Colored by central bank zone. Labels show current policy rate + direction. "
                "Click any country to see details."
            )
        else:
            fig = build_trade_map(ca_df)
            st.caption(
                "Current account as % of GDP (IMF, most recent year ≤ 2025). "
                "🟢 Green = surplus / capital exporter  ·  🔴 Red = deficit / capital importer."
            )

        try:
            event = st.plotly_chart(
                fig,
                on_select="rerun",
                key=f"wm_{map_mode[:5]}",
                use_container_width=True,
            )
            if event and event.selection and event.selection.points:
                for pt in event.selection.points:
                    loc = pt.get("location")
                    if loc and len(loc) == 3:
                        st.session_state["map_country"] = loc
                        break
        except (TypeError, AttributeError):
            st.plotly_chart(fig, use_container_width=True)
            st.caption("_Tip: upgrade Streamlit for click-to-select functionality._")

    with col_panel:
        render_map_detail(
            st.session_state.get("map_country"),
            summary,
            ca_df,
        )