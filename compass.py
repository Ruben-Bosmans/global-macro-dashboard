import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import date

PROC = Path("data/processed")

# ══════════════════════════════════════════════════════════════════
# ASSET CLASS MATRIX PER KWADRANT
# +1 = gunstig  |  0 = neutraal  |  -1 = ongunstig
# ══════════════════════════════════════════════════════════════════

ASSET_MATRIX = {
    1: {"Equities (growth)": 1,  "Equities (defensive)": 1,  "Gov. Bonds": -1,
        "Corp. Bonds": 1,  "Commodities": 0,  "Gold": 0,  "Cash": -1, "Crypto": 1},
    2: {"Equities (growth)": 0,  "Equities (defensive)": 0,  "Gov. Bonds": -1,
        "Corp. Bonds": 0,  "Commodities": 1,  "Gold": 1,  "Cash": 0,  "Crypto": 0},
    3: {"Equities (growth)": -1, "Equities (defensive)": 0,  "Gov. Bonds": -1,
        "Corp. Bonds": -1, "Commodities": 1,  "Gold": 1,  "Cash": 1,  "Crypto": -1},
    4: {"Equities (growth)": -1, "Equities (defensive)": 1,  "Gov. Bonds": 1,
        "Corp. Bonds": 0,  "Commodities": -1, "Gold": 0,  "Cash": 0,  "Crypto": -1},
    0: {"Equities (growth)": 0,  "Equities (defensive)": 0,  "Gov. Bonds": 0,
        "Corp. Bonds": 0,  "Commodities": 0,  "Gold": 0,  "Cash": 0,  "Crypto": 0},
}

KWADRANT_INFO = {
    1: ("Goldilocks",     "Growth rising, inflation falling"),
    2: ("Overheating", "Growth rising, inflation rising"),
    3: ("Stagflation",     "Groei daalt, inflatie stijgt"),
    4: ("Recession",       "Growth falling, inflation falling"),
    0: ("Transition",      "No clear regime"),
}

# ══════════════════════════════════════════════════════════════════
# HELPERFUNCTIES
# ══════════════════════════════════════════════════════════════════

def load(filename):
    """Laad een processed CSV-bestand."""
    path = PROC / f"{filename}.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        return df.sort_values("date").dropna(subset=["value"]).reset_index(drop=True)
    except Exception:
        return None


def get_direction(series, window=3, threshold=0.15):
    """
    Vergelijk gemiddelde van laatste {window} waarden met vorige {window} waarden.
    Returns: richting (+1/-1/0), delta (grootte van verandering)
    """
    s = series.dropna()
    if len(s) < window * 2:
        return 0, 0.0
    recent   = s.tail(window).mean()
    previous = s.iloc[-(window * 2):-window].mean()
    delta    = recent - previous
    if delta > threshold:
        return 1, round(delta, 3)
    elif delta < -threshold:
        return -1, round(delta, 3)
    return 0, round(delta, 3)


def cli_signal(name, window=3, threshold=0.08):
    """Groei-as: richting van OECD CLI."""
    df = load(name)
    if df is None:
        return 0, 0.0, None, None
    direction, delta = get_direction(df["value"], window, threshold)
    return direction, delta, round(float(df["value"].iloc[-1]), 2), df["date"].iloc[-1]


def cpi_signal(name, window=3, threshold=0.15):
    """Inflatie-as: richting van CPI YoY%-trend."""
    df = load(name)
    if df is None or "yoy_pct" not in df.columns:
        return 0, 0.0, None, None
    df = df.dropna(subset=["yoy_pct"])
    if df.empty:
        return 0, 0.0, None, None
    direction, delta = get_direction(df["yoy_pct"], window, threshold)
    return direction, delta, round(float(df["yoy_pct"].iloc[-1]), 2), df["date"].iloc[-1]


def multi_cpi_signal(names, window=3, threshold=0.3):
    """Gecombineerd inflatiesignaal op basis van meerdere landen."""
    dirs, deltas, vals = [], [], []
    for name in names:
        d, delta, v, _ = cpi_signal(name, window, threshold)
        if v is not None:
            dirs.append(d)
            deltas.append(delta)
            vals.append(v)
    if not dirs:
        return 0, 0.0, None
    mean_dir = np.mean(dirs)
    final_dir = 1 if mean_dir > 0.3 else (-1 if mean_dir < -0.3 else 0)
    return final_dir, round(float(np.mean(deltas)), 3), round(float(np.mean(vals)), 2)


def assign_quadrant(growth_dir, inflation_dir):
    """Wijs kwadrant toe op basis van groei- en inflatiericpting."""
    if growth_dir == 1  and inflation_dir == -1: return 1
    if growth_dir == 1  and inflation_dir ==  1: return 2
    if growth_dir == -1 and inflation_dir ==  1: return 3
    if growth_dir == -1 and inflation_dir == -1: return 4
    return 0  # Transition


def regime_stability(cli_name, cpi_name, window=3, cli_thr=0.15, cpi_thr=0.3):
    """
    Hoeveel opeenvolgende maanden zijn we al in het huidige kwadrant?
    Kijkt maximaal 24 maanden terug in de historische data.
    """
    cli_df = load(cli_name)
    cpi_df = load(cpi_name)
    if cli_df is None or cpi_df is None:
        return 0
    if "yoy_pct" not in cpi_df.columns:
        return 0
    cpi_df = cpi_df.dropna(subset=["yoy_pct"]).reset_index(drop=True)

    min_pts = window * 2
    max_back = min(24, len(cli_df) - min_pts, len(cpi_df) - min_pts)
    if max_back < 0:
        return 0

    current_q = None
    stability  = 0

    for mb in range(max_back + 1):
        cli_trim = cli_df.iloc[:len(cli_df) - mb] if mb > 0 else cli_df
        cpi_trim = cpi_df.iloc[:len(cpi_df) - mb] if mb > 0 else cpi_df
        if len(cli_trim) < min_pts or len(cpi_trim) < min_pts:
            break

        g_dir, _ = get_direction(cli_trim["value"],       window, cli_thr)
        i_dir, _ = get_direction(cpi_trim["yoy_pct"],     window, cpi_thr)
        q         = assign_quadrant(g_dir, i_dir)

        if mb == 0:
            current_q = q
            if q == 0:
                return 0
            stability = 1
        else:
            if q == current_q:
                stability += 1
            else:
                break

    return stability


# ══════════════════════════════════════════════════════════════════
# VALIDATIESIGNALEN
# ══════════════════════════════════════════════════════════════════

def make_signal(label, value, unit, thresholds, interpretations):
    """
    Maak een gestandaardiseerd signaalobject.
    thresholds: (lage_grens, hoge_grens) — onder lage = positief, boven hoge = negatief
    """
    low, high = thresholds
    if value <= low:
        status, sig = interpretations[0], 1
    elif value >= high:
        status, sig = interpretations[2], -1
    else:
        status, sig = interpretations[1], 0
    return {"label": label, "value": value, "unit": unit,
            "status": status, "signal": sig}


def signals_us():
    out = {}
    mapping = [
        ("credit_spread_10y_2y", "Yieldcurve (10J-2J)",      "%",   (-0.25, 0.25),
         ["Normal", "Flat",         "Inverted"]),
        ("credit_us_hy_oas",     "US HY Spreads",             "bps", (350,   500),
         ["Normal", "Elevated",     "Stress"]),
        ("credit_us_ig_oas",     "US IG Spreads",             "bps", (120,   200),
         ["Normal", "Elevated",     "Stress"]),
        ("vix",                  "VIX (marktangst)",          "idx", (18,    28),
         ["Calm",  "Elevated",     "Fear"]),
        ("real_rate_us",         "Reële Rente VS",            "%",   (0.5,   2.0),
         ["Accommodative", "Neutral", "Restrictive"]),
    ]
    for fname, label, unit, thr, interp in mapping:
        df = load(fname)
        if df is not None:
            val = round(float(df["value"].iloc[-1]), 2)
            out[fname] = make_signal(label, val, unit, thr, interp)
    return out


def signals_eu():
    out = {}
    # BTP-Bund spread: lage grens = normaal, hoge grens = stress
    df = load("spread_it_de")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 1)
        out["spread_it_de"] = make_signal(
            "BTP-Bund Spread (IT-DE)", val, "bps", (130, 250),
            ["Normal", "Elevated", "Fragmentation risk"])
    df = load("credit_eu_hy_oas")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 1)
        out["credit_eu_hy_oas"] = make_signal(
            "EU HY Spreads", val, "bps", (380, 550),
            ["Normal", "Elevated", "Stress"])
    df = load("real_rate_de")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 2)
        out["real_rate_de"] = make_signal(
            "Reële Rente DE", val, "%", (0.5, 2.0),
            ["Accommodative", "Neutral", "Restrictive"])
    df = load("ecb_euribor_3m")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 3)
        dir_val, _ = get_direction(df["value"], window=3, threshold=0.05)
        out["ecb_euribor_3m"] = {
            "label": "Euribor 3M", "value": val, "unit": "%",
            "status": "Rising" if dir_val == 1 else ("Falling" if dir_val == -1 else "Stable"),
            "signal": 0,
        }
    return out


def signals_global():
    out = {}
    # DXY: stijgende dollar = druk op EM = negatief voor globale groei
    df = load("dxy")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 2)
        dir_val, _ = get_direction(df["value"], window=3, threshold=0.5)
        out["dxy"] = {
            "label": "Dollar Index (DXY)", "value": val, "unit": "idx",
            "status": "Rising" if dir_val == 1 else ("Falling" if dir_val == -1 else "Stable"),
            "signal": -dir_val,  # stijgende dollar is negatief voor EM/global
        }
    df = load("gold")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 0)
        dir_val, _ = get_direction(df["value"], window=3, threshold=15.0)
        out["gold"] = {
            "label": "Gold (USD/oz)", "value": val, "unit": "USD",
            "status": "Rising" if dir_val == 1 else ("Falling" if dir_val == -1 else "Stable"),
            "signal": dir_val,
        }
    df = load("credit_em_hy_oas")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 1)
        out["credit_em_hy_oas"] = make_signal(
            "EM HY Spreads", val, "bps", (400, 600),
            ["Normal", "Elevated", "Stress"])
    df = load("vix")
    if df is not None:
        val = round(float(df["value"].iloc[-1]), 1)
        out["vix"] = make_signal(
            "VIX", val, "idx", (18, 28),
            ["Calm", "Elevated", "Fear"])
    return out


# ══════════════════════════════════════════════════════════════════
# KOMPAS BUILDERS
# ══════════════════════════════════════════════════════════════════

def build_quadrant_history(cli_name, cpi_name, months_back=60,
                           window=3, cli_thr=0.15, cpi_thr=0.3):
    """
    Calculate the quadrant for each of the past N months.
    Returns a list of monthly regime assignments for the history chart.
    """
    cli_df = load(cli_name)
    cpi_df = load(cpi_name)
    if cli_df is None or cpi_df is None:
        return []

    cpi_df  = cpi_df.dropna(subset=["yoy_pct"]).reset_index(drop=True)
    min_pts = window * 2
    history = []

    for mb in range(months_back, -1, -1):
        end_cli = len(cli_df) - mb if mb > 0 else len(cli_df)
        end_cpi = len(cpi_df) - mb if mb > 0 else len(cpi_df)
        if end_cli < min_pts or end_cpi < min_pts:
            continue

        cli_trim = cli_df.iloc[:end_cli]
        cpi_trim = cpi_df.iloc[:end_cpi]

        g_dir, _ = get_direction(cli_trim["value"],    window, cli_thr)
        i_dir, _ = get_direction(cpi_trim["yoy_pct"],  window, cpi_thr)
        q         = assign_quadrant(g_dir, i_dir)

        history.append({
            "date":          str(cli_trim["date"].iloc[-1])[:7],
            "quadrant":      q,
            "label":         KWADRANT_INFO[q][0],
            "growth_dir":    g_dir,
            "inflation_dir": i_dir,
        })

    return history

def build_us():
    g_dir, g_delta, g_val, g_date = cli_signal("oecd_cli_usa")
    i_dir, i_delta, i_val, i_date = cpi_signal("cpi_us")
    ip_dir, _, ip_val, _          = cli_signal("ip_us", threshold=0.3)
    q_num   = assign_quadrant(g_dir, i_dir)
    q_label, q_desc = KWADRANT_INFO[q_num]
    stab    = regime_stability("oecd_cli_usa", "cpi_us")

    return {
        "region": "US", "timestamp": date.today().isoformat(),
        "growth": {
            "direction": g_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[g_dir],
            "indicator": "OECD CLI US",
            "value": g_val, "change_3m": g_delta,
            "date": g_date.isoformat() if g_date is not None else None,
            "confirmation": {
                "indicator": "Industrial Production US",
                "direction": ip_dir, "value": ip_val,
            },
        },
        "inflation": {
            "direction": i_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[i_dir],
            "indicator": "CPI US YoY%",
            "value": i_val, "change_3m": i_delta,
            "date": i_date.isoformat() if i_date is not None else None,
        },
        "quadrant": {
            "number": q_num, "label": q_label, "description": q_desc,
            "stability_months": stab,
        },
        "asset_signals": ASSET_MATRIX[q_num],
        "history":      build_quadrant_history("oecd_cli_usa", "cpi_us", months_back=60),
        "validation": signals_us(),
    }


def build_eu():
    g_dir, g_delta, g_val, g_date = cli_signal("oecd_cli_g4e")
    i_dir, i_delta, i_val         = multi_cpi_signal(["cpi_de", "cpi_fr", "cpi_it"])
    q_num   = assign_quadrant(g_dir, i_dir)
    q_label, q_desc = KWADRANT_INFO[q_num]
    stab    = regime_stability("oecd_cli_g4e", "cpi_de")

    return {
        "region": "EU", "timestamp": date.today().isoformat(),
        "growth": {
            "direction": g_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[g_dir],
            "indicator": "OECD CLI G4 Europe",
            "value": g_val, "change_3m": g_delta,
            "date": g_date.isoformat() if g_date is not None else None,
        },
        "inflation": {
            "direction": i_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[i_dir],
            "indicator": "CPI Average DE+FR+IT YoY%",
            "value": i_val, "change_3m": i_delta,
        },
        "quadrant": {
            "number": q_num, "label": q_label, "description": q_desc,
            "stability_months": stab,
        },
        "asset_signals": ASSET_MATRIX[q_num],
        "history":      build_quadrant_history("oecd_cli_g4e", "cpi_de", months_back=60),
        "validation": signals_eu(),
    }


def build_global():
    g_dir, g_delta, g_val, g_date = cli_signal("oecd_cli_g20")
    i_dir, i_delta, i_val         = multi_cpi_signal(
        ["cpi_us", "cpi_de", "cpi_jp", "cpi_cn", "cpi_uk"])
    q_num   = assign_quadrant(g_dir, i_dir)
    q_label, q_desc = KWADRANT_INFO[q_num]

    # Divergentie VS vs EU
    us_g, _, _, _ = cli_signal("oecd_cli_usa")
    eu_g, _, _, _ = cli_signal("oecd_cli_g4e")
    divergent     = (us_g != eu_g) and (us_g != 0) and (eu_g != 0)

    return {
        "region": "Global", "timestamp": date.today().isoformat(),
        "growth": {
            "direction": g_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[g_dir],
            "indicator": "OECD CLI G20",
            "value": g_val, "change_3m": g_delta,
            "date": g_date.isoformat() if g_date is not None else None,
        },
        "inflation": {
            "direction": i_dir,
            "direction_label": {1: "Rising", -1: "Falling", 0: "Flat"}[i_dir],
            "indicator": "CPI Average G5 YoY%",
            "value": i_val, "change_3m": i_delta,
        },
        "quadrant": {
            "number": q_num, "label": q_label, "description": q_desc,
            "stability_months": 0,
        },
        "asset_signals": ASSET_MATRIX[q_num],
        "history":      build_quadrant_history("oecd_cli_g20", "cpi_us", months_back=60),
        "validation": signals_global(),
        "divergence": {
            "actief": divergent,
            "us_groei": us_g,
            "eu_groei": eu_g,
            "label": "US and EU diverging" if divergent else "US and EU in sync",
        },
    }


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'='*60}")
    print(f"  Compass — Macro Regime Detector")
    print(f"{'='*60}\n")

    builders = [
        ("Global", build_global, "compass_global.json"),
        ("VS",     build_us,     "compass_us.json"),
        ("EU",     build_eu,     "compass_eu.json"),
    ]

    for region_name, builder, filename in builders:
        try:
            result  = builder()
            q       = result["quadrant"]
            g       = result["growth"]
            i_inf   = result["inflation"]
            g_arrow = {1: "↑", -1: "↓", 0: "→"}
            out_path = PROC / filename
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            print(f"  ✓  {region_name:8s} │ Kwadrant {q['number']} — {q['label']:15s} │ "
                  f"Groei {g_arrow[g['direction']]}  "
                  f"Inflatie {g_arrow[i_inf['direction']]}  │ "
                  f"Stabiliteit: {q['stability_months']}m")
        except Exception as e:
            print(f"  ✗  {region_name}: {e}")

    print(f"\n  Output: data/processed/compass_*.json")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
