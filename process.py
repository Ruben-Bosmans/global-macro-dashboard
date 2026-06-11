import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime

RAW  = Path("data")
PROC = Path("data/processed")
PROC.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# CATALOGUS — classificeert elk bestand
# Formaat: bestandsnaam (zonder .csv): (categorie, subcategorie, eenheid, land, beschrijving)
# ══════════════════════════════════════════════════════════════════

DAILY_PRICE = {
    # Aandelenindices — VS
    "sp500":            ("equities", "us",      "index", "US",  "S&P 500"),
    "nasdaq100":        ("equities", "us",      "index", "US",  "Nasdaq 100"),
    "dow_jones":        ("equities", "us",      "index", "US",  "Dow Jones"),
    "russell2000":      ("equities", "us",      "index", "US",  "Russell 2000"),
    "vix":              ("equities", "us",      "index", "US",  "VIX Volatility"),
    # Europa
    "eurostoxx50":      ("equities", "europe",  "index", "EU",  "Euro Stoxx 50"),
    "dax":              ("equities", "europe",  "index", "DE",  "DAX"),
    "cac40":            ("equities", "europe",  "index", "FR",  "CAC 40"),
    "ftse100":          ("equities", "europe",  "index", "UK",  "FTSE 100"),
    "ibex35":           ("equities", "europe",  "index", "ES",  "IBEX 35"),
    "ftse_mib":         ("equities", "europe",  "index", "IT",  "FTSE MIB"),
    "aex":              ("equities", "europe",  "index", "NL",  "AEX"),
    "bel20":            ("equities", "europe",  "index", "BE",  "BEL 20"),
    "smi":              ("equities", "europe",  "index", "CH",  "SMI"),
    # Azië-Pacific
    "nikkei":           ("equities", "asia",    "index", "JP",  "Nikkei 225"),
    "hang_seng":        ("equities", "asia",    "index", "HK",  "Hang Seng"),
    "shanghai":         ("equities", "asia",    "index", "CN",  "Shanghai Composite"),
    "csi300":           ("equities", "asia",    "index", "CN",  "CSI 300"),
    "kospi":            ("equities", "asia",    "index", "KR",  "KOSPI"),
    "sensex":           ("equities", "asia",    "index", "IN",  "Sensex"),
    "nifty50":          ("equities", "asia",    "index", "IN",  "Nifty 50"),
    "asx200":           ("equities", "asia",    "index", "AU",  "ASX 200"),
    "straits_times":    ("equities", "asia",    "index", "SG",  "Straits Times"),
    # Overig
    "tsx":              ("equities", "americas","index", "CA",  "TSX"),
    "bovespa":          ("equities", "americas","index", "BR",  "Bovespa"),
    "ipc_mexico":       ("equities", "americas","index", "MX",  "IPC Mexico"),
    # Sectoren
    "sector_tech":          ("equities", "sectors", "index", "US", "Technologie"),
    "sector_financial":     ("equities", "sectors", "index", "US", "Financials"),
    "sector_energy":        ("equities", "sectors", "index", "US", "Energy"),
    "sector_health":        ("equities", "sectors", "index", "US", "Health Care"),
    "sector_industrial":    ("equities", "sectors", "index", "US", "Industrials"),
    "sector_comms":         ("equities", "sectors", "index", "US", "Communication Services"),
    "sector_cons_disc":     ("equities", "sectors", "index", "US", "Consumer Discretionary"),
    "sector_cons_staples":  ("equities", "sectors", "index", "US", "Consumer Staples"),
    "sector_utilities":     ("equities", "sectors", "index", "US", "Utilities"),
    "sector_realestate":    ("equities", "sectors", "index", "US", "Real Estate"),
    "sector_materials":     ("equities", "sectors", "index", "US", "Materials"),
    # Grondstoffen — energie
    "gold":             ("commodities", "metals",  "USD",  "GL", "Gold"),
    "oil_wti":          ("commodities", "Energy",  "USD",  "GL", "WTI Oil"),
    "oil_brent":        ("commodities", "Energy",  "USD",  "GL", "Brent Oil"),
    "natural_gas":      ("commodities", "Energy",  "USD",  "GL", "Natural Gas"),
    "gasoline":         ("commodities", "Energy",  "USD",  "GL", "Gasoline"),
    "heating_oil":      ("commodities", "Energy",  "USD",  "GL", "Heating Oil"),
    "coal_newcastle":   ("commodities", "Energy",  "USD",  "GL", "Coal (Newcastle)"),
    # Grondstoffen — metalen
    "copper":           ("commodities", "metals",  "USD",  "GL", "Copper"),
    "silver":           ("commodities", "metals",  "USD",  "GL", "Silver"),
    "platinum":         ("commodities", "metals",  "USD",  "GL", "Platinum"),
    "palladium":        ("commodities", "metals",  "USD",  "GL", "Palladium"),
    # Grondstoffen — landbouw
    "wheat":            ("commodities", "agriculture", "USD",  "GL", "Wheat"),
    "corn":             ("commodities", "agriculture", "USD",  "GL", "Corn"),
    "soybeans":         ("commodities", "agriculture", "USD",  "GL", "Soybeans"),
    "coffee":           ("commodities", "agriculture", "USD",  "GL", "Coffee"),
    "cotton":           ("commodities", "agriculture", "USD",  "GL", "Cotton"),
    "sugar":            ("commodities", "agriculture", "USD",  "GL", "Sugar"),
    "cocoa":            ("commodities", "agriculture", "USD",  "GL", "Cocoa"),
    "lumber":           ("commodities", "agriculture", "USD",  "GL", "Lumber"),
    # Valuta
    "dxy":              ("currencies", "indices", "%",   "GL", "Dollar Index (DXY)"),
    # Crypto
    "crypto_btc":  ("crypto", "major", "USD", "GL", "Bitcoin"),
    "crypto_eth":  ("crypto", "major", "USD", "GL", "Ethereum"),
    "crypto_bnb":  ("crypto", "major", "USD", "GL", "BNB"),
    "crypto_sol":  ("crypto", "major", "USD", "GL", "Solana"),
    "crypto_xrp":  ("crypto", "major", "USD", "GL", "XRP"),
    "crypto_ada":  ("crypto", "major", "USD", "GL", "Cardano"),
    "crypto_avax": ("crypto", "major", "USD", "GL", "Avalanche"),
    "crypto_doge": ("crypto", "major", "USD", "GL", "Dogecoin"),
    "crypto_dot":  ("crypto", "major", "USD", "GL", "Polkadot"),
    "crypto_link": ("crypto", "major", "USD", "GL", "Chainlink"),
    "crypto_ltc":  ("crypto", "major", "USD", "GL", "Litecoin"),
    "crypto_xlm":  ("crypto", "major", "USD", "GL", "Stellar"),
    "crypto_atom": ("crypto", "major", "USD", "GL", "Cosmos"),
    "crypto_uni":  ("crypto", "major", "USD", "GL", "Uniswap"),
}

# Dagelijkse data die al in % of basispunten staat
DAILY_PCT = {
    "credit_us_hy_oas":     ("credit", "high_yield", "bps", "US", "US HY Spread"),
    "credit_us_hy_bb":      ("credit", "high_yield", "bps", "US", "US HY BB Spread"),
    "credit_us_hy_b":       ("credit", "high_yield", "bps", "US", "US HY B Spread"),
    "credit_us_hy_ccc":     ("credit", "high_yield", "bps", "US", "US HY CCC Spread"),
    "credit_us_ig_oas":     ("credit", "inv_grade",  "bps", "US", "US IG Spread"),
    "credit_us_ig_aaa":     ("credit", "inv_grade",  "bps", "US", "US IG AAA Spread"),
    "credit_us_ig_aa":      ("credit", "inv_grade",  "bps", "US", "US IG AA Spread"),
    "credit_us_ig_a":       ("credit", "inv_grade",  "bps", "US", "US IG A Spread"),
    "credit_us_ig_bbb":     ("credit", "inv_grade",  "bps", "US", "US IG BBB Spread"),
    "credit_eu_hy_oas":     ("credit", "high_yield", "bps", "EU", "EU HY Spread"),
    "credit_em_hy_oas":     ("credit", "high_yield", "bps", "EM", "EM HY Spread"),
    "credit_em_ig_oas":     ("credit", "inv_grade",  "bps", "EM", "EM IG Spread"),
    "credit_em_corp_oas":   ("credit", "inv_grade",  "bps", "EM", "EM Corp Spread"),
    "credit_us_fin_oas":    ("credit", "sector",     "bps", "US", "US Financial Spread"),
    "credit_ted_spread":    ("credit", "money_market",  "%",   "US", "TED Spread"),
    "credit_sofr_spread":   ("credit", "money_market",  "%",   "US", "SOFR Rate"),
    "credit_spread_10y_2y": ("rates",  "yield_curve", "%",   "US", "10Y-2Y Spread"),
    "credit_spread_10y_3m": ("rates",  "yield_curve", "%",   "US", "10Y-3M Spread"),
    "credit_spread_aaa_10y":("credit", "inv_grade",  "%",   "US", "AAA Corp - 10Y"),
    "credit_term_prem_10y": ("rates",  "yield_curve", "%",   "US", "Term Premium 10Y"),
    "credit_mortgage_30y":  ("rates",  "mortgage",  "%",   "US", "30Y Mortgage Rate"),
}

# Maandelijkse data — al in % (rentes, werkloosheid)
MONTHLY_RATE = {
    "rate_us":      ("rates", "policy_rate", "%", "US", "Fed Funds Rate"),
    "rate_ecb":     ("rates", "policy_rate", "%", "EU", "ECB Deposit Rate"),
    "rate_uk":      ("rates", "policy_rate", "%", "UK", "BoE Base Rate"),
    "rate_jp":      ("rates", "policy_rate", "%", "JP", "BoJ Rate"),
    "rate_ca":      ("rates", "policy_rate", "%", "CA", "BoC Rate"),
    "rate_br":      ("rates", "policy_rate", "%", "BR", "BCB Rate"),
    "rate_in":      ("rates", "policy_rate", "%", "IN", "RBI Rate"),
    "rate_za":      ("rates", "policy_rate", "%", "ZA", "SARB Rate"),
    "rate_cn":      ("rates", "policy_rate", "%", "CN", "PBoC Rate"),
    "unemp_us":     ("labour", "unemployment", "%", "US", "Unemployment US"),
    "unemp_uk":     ("labour", "unemployment", "%", "UK", "Unemployment UK"),
    "unemp_jp":     ("labour", "unemployment", "%", "JP", "Unemployment Japan"),
    "unemp_ca":     ("labour", "unemployment", "%", "CA", "Unemployment Canada"),
    "unemp_de":     ("labour", "unemployment", "%", "DE", "Unemployment Germany"),
    "unemp_fr":     ("labour", "unemployment", "%", "FR", "Unemployment France"),
    "unemp_it":     ("labour", "unemployment", "%", "IT", "Unemployment Italy"),
    "unemp_au":     ("labour", "unemployment", "%", "AU", "Unemployment Australia"),
    "unemp_se":     ("labour", "unemployment", "%", "SE", "Unemployment Sweden"),
    "unemp_kr":     ("labour", "unemployment", "%", "KR", "Unemployment South Korea"),
    "us_2y_yield":  ("rates", "bonds", "%", "US", "US 2Y Yield"),
    "us_10y_yield": ("rates", "bonds", "%", "US", "US 10Y Yield"),
    "us_30y_yield": ("rates", "bonds", "%", "US", "US 30Y Yield"),
    "fed_funds_rate":("rates","policy_rate", "%", "US", "Fed Funds Rate (daily)"),
    "bond10y_uk":   ("rates", "bonds", "%", "UK", "10Y VK"),
    "bond10y_de":   ("rates", "bonds", "%", "DE", "10Y Duitsland"),
    "bond10y_fr":   ("rates", "bonds", "%", "FR", "10Y Frankrijk"),
    "bond10y_it":   ("rates", "bonds", "%", "IT", "10Y Italië"),
    "bond10y_jp":   ("rates", "bonds", "%", "JP", "10Y Japan"),
    "bond10y_ca":   ("rates", "bonds", "%", "CA", "10Y Canada"),
    "bond10y_au":   ("rates", "bonds", "%", "AU", "10Y Australia"),
    "bond10y_se":   ("rates", "bonds", "%", "SE", "10Y Sweden"),
    "bond10y_no":   ("rates", "bonds", "%", "NO", "10Y Norway"),
    "bond10y_ch":   ("rates", "bonds", "%", "CH", "10Y Switzerland"),
    "bond10y_kr":   ("rates", "bonds", "%", "KR", "10Y South Korea"),
    "bond10y_mx":   ("rates", "bonds", "%", "MX", "10Y Mexico"),
    "bond10y_es":   ("rates", "bonds", "%", "ES", "10Y Spain"),
    "bond10y_be":   ("rates", "bonds", "%", "BE", "10Y Belgium"),
    "bond10y_pt":   ("rates", "bonds", "%", "PT", "10Y Portugal"),
    "bond10y_gr":   ("rates", "bonds", "%", "GR", "10Y Greece"),
    "bond10y_at":   ("rates", "bonds", "%", "AT", "10Y Austria"),
    "bond10y_fi":   ("rates", "bonds", "%", "FI", "10Y Finland"),
    "bond10y_nl":   ("rates", "bonds", "%", "NL", "10Y Netherlands"),
    "rate3m_uk":    ("rates", "money_market", "%", "UK", "3M Rate UK"),
    "rate3m_de":    ("rates", "money_market", "%", "DE", "3M Rate Germany"),
    "rate3m_jp":    ("rates", "money_market", "%", "JP", "3M Rate Japan"),
    "rate3m_ca":    ("rates", "money_market", "%", "CA", "3M Rate Canada"),
    "rate3m_au":    ("rates", "money_market", "%", "AU", "3M Rate Australia"),
    "rate3m_ch":    ("rates", "money_market", "%", "CH", "3M Rate Switzerland"),
    "rate3m_se":    ("rates", "money_market", "%", "SE", "3M Rate Sweden"),
    "rate3m_no":    ("rates", "money_market", "%", "NO", "3M Rate Norway"),
    "rate3m_kr":    ("rates", "money_market", "%", "KR", "3M Rate South Korea"),
    "rate3m_mx":    ("rates", "money_market", "%", "MX", "3M Rate Mexico"),
    "rate3m_za":    ("rates", "money_market", "%", "ZA", "3M Rate South Africa"),
    "ecb_ecb_deposit":  ("rates", "policy_rate", "%", "EU", "ECB Deposit Rate"),
    "ecb_ecb_refi":     ("rates", "policy_rate", "%", "EU", "ECB Refi Rate"),
    "ecb_ecb_lending":  ("rates", "policy_rate", "%", "EU", "ECB Lending Rate"),
    "ecb_euribor_1m":   ("rates", "money_market",    "%", "EU", "Euribor 1M"),
    "ecb_euribor_3m":   ("rates", "money_market",    "%", "EU", "Euribor 3M"),
    "ecb_euribor_6m":   ("rates", "money_market",    "%", "EU", "Euribor 6M"),
    "ecb_estr":         ("rates", "money_market",    "%", "EU", "€STR Overnight"),
    "ecb_bonds_ea_2y":  ("rates", "bonds", "%", "EU", "Eurozone 2Y Benchmark"),
    "ecb_bonds_ea_5y":  ("rates", "bonds", "%", "EU", "Eurozone 5Y Benchmark"),
    "ecb_bonds_ea_10y": ("rates", "bonds", "%", "EU", "Eurozone 10Y Benchmark"),
    "ecb_yc_2y":    ("rates", "yield_curve", "%", "EU", "ECB Yieldcurve 2Y"),
    "ecb_yc_5y":    ("rates", "yield_curve", "%", "EU", "ECB Yieldcurve 5Y"),
    "ecb_yc_10y":   ("rates", "yield_curve", "%", "EU", "ECB Yieldcurve 10Y"),
}

# Maandelijkse data — indexwaarden waaruit YoY% berekend moet worden
MONTHLY_INDEX = {
    "cpi_us":   ("inflation", "cpi", "index", "US", "CPI US"),
    "cpi_uk":   ("inflation", "cpi", "index", "UK", "CPI UK"),
    "cpi_jp":   ("inflation", "cpi", "index", "JP", "CPI Japan"),
    "cpi_ca":   ("inflation", "cpi", "index", "CA", "CPI Canada"),
    "cpi_de":   ("inflation", "cpi", "index", "DE", "CPI Germany"),
    "cpi_fr":   ("inflation", "cpi", "index", "FR", "CPI France"),
    "cpi_it":   ("inflation", "cpi", "index", "IT", "CPI Italy"),
    "cpi_au":   ("inflation", "cpi", "index", "AU", "CPI Australia"),
    "cpi_ch":   ("inflation", "cpi", "index", "CH", "CPI Switzerland"),
    "cpi_se":   ("inflation", "cpi", "index", "SE", "CPI Sweden"),
    "cpi_no":   ("inflation", "cpi", "index", "NO", "CPI Norway"),
    "cpi_kr":   ("inflation", "cpi", "index", "KR", "CPI South Korea"),
    "cpi_cn":   ("inflation", "cpi", "index", "CN", "CPI China"),
    "cpi_br":   ("inflation", "cpi", "index", "BR", "CPI Brazil"),
    "cpi_mx":   ("inflation", "cpi", "index", "MX", "CPI Mexico"),
    "cpi_in":   ("inflation", "cpi", "index", "IN", "CPI India"),
    "cpi_za":   ("inflation", "cpi", "index", "ZA", "CPI South Africa"),
    "m2_us":    ("money", "m2", "mrd", "US", "M2 US"),
    "m2_uk":    ("money", "m2", "mrd", "UK", "M2 UK"),
    "m2_jp":    ("money", "m2", "mrd", "JP", "M2 Japan"),
    "m2_cn":    ("money", "m2", "mrd", "CN", "M2 China"),
    "ecb_m1_ea":("money", "m1", "mrd", "EU", "M1 Eurozone"),
    "ecb_m3_ea":("money", "m3", "mrd", "EU", "M3 Eurozone"),
    "retail_us":("economy", "retail",                "index", "US", "Retail Sales US"),
    # Industriële productie (index 2015=100 — YoY% wordt berekend)
    "ip_us":    ("economy", "industrial_production", "index", "US", "Industrial Production US"),
    "ip_de":    ("economy", "industrial_production", "index", "DE", "Industrial Production Germany"),
    "ip_fr":    ("economy", "industrial_production", "index", "FR", "Industrial Production France"),
    "ip_jp":    ("economy", "industrial_production", "index", "JP", "Industrial Production Japan"),
    "ip_uk":    ("economy", "industrial_production", "index", "UK", "Industrial Production UK"),
    "ip_ca":    ("economy", "industrial_production", "index", "CA", "Industrial Production Canada"),
    "ip_kr":    ("economy", "industrial_production", "index", "KR", "Industrial Production South Korea"),
}

# ECB wisselkoersen (maandelijks, prijsniveau)
ECB_FX = {
    "ecb_eur_usd": ("currencies", "eur_pairs", "rate", "EU", "EUR/USD"),
    "ecb_eur_gbp": ("currencies", "eur_pairs", "rate", "EU", "EUR/GBP"),
    "ecb_eur_jpy": ("currencies", "eur_pairs", "rate", "EU", "EUR/JPY"),
    "ecb_eur_cny": ("currencies", "eur_pairs", "rate", "EU", "EUR/CNY"),
    "ecb_eur_chf": ("currencies", "eur_pairs", "rate", "EU", "EUR/CHF"),
    "ecb_eur_aud": ("currencies", "eur_pairs", "rate", "EU", "EUR/AUD"),
    "ecb_eur_cad": ("currencies", "eur_pairs", "rate", "EU", "EUR/CAD"),
    "ecb_eur_sek": ("currencies", "eur_pairs", "rate", "EU", "EUR/SEK"),
    "ecb_eur_nok": ("currencies", "eur_pairs", "rate", "EU", "EUR/NOK"),
    "ecb_eur_krw": ("currencies", "eur_pairs", "rate", "EU", "EUR/KRW"),
    "ecb_eur_brl": ("currencies", "eur_pairs", "rate", "EU", "EUR/BRL"),
    "ecb_eur_inr": ("currencies", "eur_pairs", "rate", "EU", "EUR/INR"),
    "ecb_eur_try": ("currencies", "eur_pairs", "rate", "EU", "EUR/TRY"),
    "ecb_eur_mxn": ("currencies", "eur_pairs", "rate", "EU", "EUR/MXN"),
    "ecb_eur_pln": ("currencies", "eur_pairs", "rate", "EU", "EUR/PLN"),
    "ecb_eur_czk": ("currencies", "eur_pairs", "rate", "EU", "EUR/CZK"),
    "ecb_eur_huf": ("currencies", "eur_pairs", "rate", "EU", "EUR/HUF"),
    "ecb_eur_zar": ("currencies", "eur_pairs", "rate", "EU", "EUR/ZAR"),
}
# Maandelijkse OECD Composite Leading Indicators (CLI)
# Waarden rond 100 = langetermijntrend; richting = het signaal
MONTHLY_CLI = {
    "oecd_cli_usa":   ("economy", "leading_indicator", "index", "US",   "CLI United States"),
    "oecd_cli_deu":   ("economy", "leading_indicator", "index", "DE",   "CLI Germany"),
    "oecd_cli_fra":   ("economy", "leading_indicator", "index", "FR",   "CLI France"),
    "oecd_cli_ita":   ("economy", "leading_indicator", "index", "IT",   "CLI Italy"),
    "oecd_cli_gbr":   ("economy", "leading_indicator", "index", "UK",   "CLI United Kingdom"),
    "oecd_cli_can":   ("economy", "leading_indicator", "index", "CA",   "CLI Canada"),
    "oecd_cli_jpn":   ("economy", "leading_indicator", "index", "JP",   "CLI Japan"),
    "oecd_cli_aus":   ("economy", "leading_indicator", "index", "AU",   "CLI Australia"),
    "oecd_cli_chn":   ("economy", "leading_indicator", "index", "CN",   "CLI China"),
    "oecd_cli_ind":   ("economy", "leading_indicator", "index", "IN",   "CLI India"),
    "oecd_cli_kor":   ("economy", "leading_indicator", "index", "KR",   "CLI South Korea"),
    "oecd_cli_bra":   ("economy", "leading_indicator", "index", "BR",   "CLI Brazil"),
    "oecd_cli_mex":   ("economy", "leading_indicator", "index", "MX",   "CLI Mexico"),
    "oecd_cli_esp":   ("economy", "leading_indicator", "index", "ES",   "CLI Spain"),
    "oecd_cli_idn":   ("economy", "leading_indicator", "index", "ID",   "CLI Indonesia"),
    "oecd_cli_tur":   ("economy", "leading_indicator", "index", "TR",   "CLI Turkey"),
    "oecd_cli_zaf":   ("economy", "leading_indicator", "index", "ZA",   "CLI South Africa"),
    "oecd_cli_g7":    ("economy", "leading_indicator", "index", "G7",   "CLI G7"),
    "oecd_cli_g20":   ("economy", "leading_indicator", "index", "G20",  "CLI G20"),
    "oecd_cli_nafta": ("economy", "leading_indicator", "index", "NAFTA","CLI NAFTA"),
    "oecd_cli_g4e":   ("economy", "leading_indicator", "index", "EU",   "CLI G4 Europe"),
    "oecd_cli_a5m":   ("economy", "leading_indicator", "index", "ASIA", "CLI Asia 5 Major"),
}

# ══════════════════════════════════════════════════════════════════
# HELPERFUNCTIES
# ══════════════════════════════════════════════════════════════════

def load(filename):
    """Laad een CSV uit de raw data-map."""
    path = RAW / f"{filename}.csv"
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.sort_values("date").dropna(subset=["value"])
        return df
    except Exception:
        return None

def save(df, filename):
    """Sla een verwerkt DataFrame op in data/processed/."""
    df.to_csv(PROC / f"{filename}.csv", index=False)

def pct_change_offset(series, periods):
    """% verandering t.o.v. N periodes geleden."""
    return ((series / series.shift(periods)) - 1) * 100

def abs_change_offset(series, periods):
    """Absolute verandering t.o.v. N periodes geleden."""
    return series - series.shift(periods)

def normalize(series):
    """Herbereken reeks zodat eerste waarde = 100."""
    return (series / series.iloc[0]) * 100

# ══════════════════════════════════════════════════════════════════
# VERWERKINGSFUNCTIES
# ══════════════════════════════════════════════════════════════════

def process_daily_price(name, meta):
    """
    Dagelijkse prijsdata (indices, grondstoffen, crypto):
    - % verandering dag/week/maand/jaar
    - Genormaliseerde waarde (start = 100)
    """
    df = load(name)
    if df is None:
        return None

    df["pct_1d"]  = pct_change_offset(df["value"], 1)
    df["pct_1w"]  = pct_change_offset(df["value"], 5)
    df["pct_1m"]  = pct_change_offset(df["value"], 21)
    df["pct_3m"]  = pct_change_offset(df["value"], 63)
    df["pct_6m"]  = pct_change_offset(df["value"], 126)
    df["pct_1y"]  = pct_change_offset(df["value"], 252)
    df["normalized"] = normalize(df["value"])

    # YTD % verandering
    current_year = df["date"].dt.year.max()
    ytd_start = df[df["date"].dt.year == current_year]["value"].iloc[0] \
        if len(df[df["date"].dt.year == current_year]) > 0 else np.nan
    df["pct_ytd"] = ((df["value"] / ytd_start) - 1) * 100

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df


def process_daily_pct(name, meta):
    """
    Dagelijkse data al in % of basispunten (credit spreads, rentes):
    - Absolute verandering dag/week/maand/jaar
    """
    df = load(name)
    if df is None:
        return None

    df["chg_1d"] = abs_change_offset(df["value"], 1)
    df["chg_1w"] = abs_change_offset(df["value"], 5)
    df["chg_1m"] = abs_change_offset(df["value"], 21)
    df["chg_1y"] = abs_change_offset(df["value"], 252)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df


def process_monthly_rate(name, meta):
    """
    Maandelijkse data al in % (rentes, werkloosheid, obligatierentes):
    - Absolute verandering maand/kwartaal/jaar
    """
    df = load(name)
    if df is None:
        return None

    df["chg_1m"] = abs_change_offset(df["value"], 1)
    df["chg_3m"] = abs_change_offset(df["value"], 3)
    df["chg_6m"] = abs_change_offset(df["value"], 6)
    df["chg_1y"] = abs_change_offset(df["value"], 12)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df


def process_monthly_index(name, meta):
    """
    Maandelijkse indexwaarden (CPI, M2, retailverkopen):
    - YoY% berekenen (= inflatie voor CPI)
    - MoM% verandering
    - 3-maands en 6-maands geannualiseerde groei
    """
    df = load(name)
    if df is None:
        return None

    df["yoy_pct"] = pct_change_offset(df["value"], 12)
    df["mom_pct"] = pct_change_offset(df["value"], 1)
    df["3m_ann"]  = ((df["value"] / df["value"].shift(3)) ** 4 - 1) * 100
    df["6m_ann"]  = ((df["value"] / df["value"].shift(6)) ** 2 - 1) * 100

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df

def process_monthly_cli(name, meta):
    """
    OECD Composite Leading Indicator (maandelijks):
    - Absolute verandering 1m/3m/6m/1y
    - 100 = langetermijntrend; stijgend boven 100 = expansie
    - Richting (stijgend/dalend) is het signaal, niet het absolute niveau
    """
    df = load(name)
    if df is None:
        return None

    df["chg_1m"] = abs_change_offset(df["value"], 1)
    df["chg_3m"] = abs_change_offset(df["value"], 3)
    df["chg_6m"] = abs_change_offset(df["value"], 6)
    df["chg_1y"] = abs_change_offset(df["value"], 12)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df

def process_ecb_fx(name, meta):
    """ECB wisselkoersen — zoekt flexibel naar bestandsnaam."""
    df = None

    # Probeer exacte naam
    exact = RAW / f"{name}.csv"
    if exact.exists():
        df = pd.read_csv(exact, parse_dates=["date"])
    else:
        # Scan naar bestanden die beginnen met de naam
        matches = sorted(RAW.glob(f"{name}*.csv"))
        if matches:
            df = pd.read_csv(matches[0], parse_dates=["date"])

    if df is None:
        return None

    df = df.sort_values("date").dropna(subset=["value"])
    df["pct_1m"] = pct_change_offset(df["value"], 1)
    df["pct_3m"] = pct_change_offset(df["value"], 3)
    df["pct_1y"] = pct_change_offset(df["value"], 12)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)
    return df


# ══════════════════════════════════════════════════════════════════
# AFGELEIDE BEREKENINGEN
# ══════════════════════════════════════════════════════════════════

def process_derived():
    """
    Bereken afgeleide reeksen die niet rechtstreeks beschikbaar zijn:
    - Reële rente per land
    - Europese obligatiespreads vs Duitsland
    - Yieldcurve spreads per land
    - Hypotheekspread
    """
    derived = {}

    # ── REËLE RENTE (nominale rente - CPI YoY) ────────────────────
    # Reële rente = wat je werkelijk verdient na inflatie
    real_rate_pairs = [
        ("real_rate_us", "us_10y_yield", "cpi_us"),
        ("real_rate_uk", "bond10y_uk",   "cpi_uk"),
        ("real_rate_de", "bond10y_de",   "cpi_de"),
        ("real_rate_fr", "bond10y_fr",   "cpi_fr"),
        ("real_rate_jp", "bond10y_jp",   "cpi_jp"),
        ("real_rate_ca", "bond10y_ca",   "cpi_ca"),
        ("real_rate_au", "bond10y_au",   "cpi_au"),
        ("real_rate_it", "bond10y_it",   "cpi_it"),
    ]

    for out_name, rate_file, cpi_file in real_rate_pairs:
        rate = load(rate_file)
        cpi  = load(cpi_file)
        if rate is None or cpi is None:
            continue

        cpi["yoy"] = pct_change_offset(cpi["value"], 12)
        merged = pd.merge_asof(
            rate.rename(columns={"value": "rate"}),
            cpi[["date", "yoy"]].dropna(),
            on="date", direction="backward"
        )
        merged["value"] = merged["rate"] - merged["yoy"]
        merged["chg_1m"] = abs_change_offset(merged["value"], 1)
        merged["chg_1y"] = abs_change_offset(merged["value"], 12)
        result = merged[["date", "value", "chg_1m", "chg_1y"]].dropna(subset=["value"])
        num = result.select_dtypes(include="number").columns
        result[num] = result[num].round(4)
        save(result, out_name)
        land_map = {
        "us_10y_yield": "US", "bond10y_uk": "UK", "bond10y_de": "DE",
        "bond10y_fr": "FR",   "bond10y_jp": "JP", "bond10y_ca": "CA",
        "bond10y_au": "AU",   "bond10y_it": "IT",
        }
        land = land_map.get(rate_file, "??")
        derived[out_name] = ("rates", "real", "%", land, f"Real Rate {land}")
        print(f"  ✓  {out_name}")

    # ── EUROPESE OBLIGATIESPREADS vs DUITSLAND ────────────────────
    spread_countries = [
        ("spread_it_de", "bond10y_it", "bond10y_de", "IT-DE spread"),
        ("spread_es_de", "bond10y_es", "bond10y_de", "ES-DE spread"),
        ("spread_fr_de", "bond10y_fr", "bond10y_de", "FR-DE spread"),
        ("spread_pt_de", "bond10y_pt", "bond10y_de", "PT-DE spread"),
        ("spread_gr_de", "bond10y_gr", "bond10y_de", "GR-DE spread"),
        ("spread_be_de", "bond10y_be", "bond10y_de", "BE-DE spread"),
    ]

    for out_name, c1, c2, desc in spread_countries:
        b1 = load(c1)
        b2 = load(c2)
        if b1 is None or b2 is None:
            continue
        merged = pd.merge_asof(
            b1.rename(columns={"value": "b1"}),
            b2.rename(columns={"value": "b2"}),
            on="date", direction="nearest"
        )
        merged["value"]  = (merged["b1"] - merged["b2"]) * 100  # in basispunten
        merged["chg_1m"] = abs_change_offset(merged["value"], 1)
        merged["chg_1y"] = abs_change_offset(merged["value"], 12)
        result = merged[["date", "value", "chg_1m", "chg_1y"]].dropna(subset=["value"])
        num = result.select_dtypes(include="number").columns
        result[num] = result[num].round(2)
        save(result, out_name)
        derived[out_name] = ("credit", "eu_spreads", "bps", "EU", desc)
        print(f"  ✓  {out_name}")

    # ── HYPOTHEEKSPREAD (hypotheekrente - 10j Treasury) ───────────
    mortgage = load("credit_mortgage_30y")
    us10y    = load("us_10y_yield")
    if mortgage is not None and us10y is not None:
        merged = pd.merge_asof(
            mortgage.rename(columns={"value": "mortgage"}),
            us10y.rename(columns={"value": "treasury"}),
            on="date", direction="nearest"
        )
        merged["value"]  = (merged["mortgage"] - merged["treasury"]) * 100
        merged["chg_1m"] = abs_change_offset(merged["value"], 1)
        result = merged[["date", "value", "chg_1m"]].dropna(subset=["value"])
        num = result.select_dtypes(include="number").columns
        result[num] = result[num].round(2)
        save(result, "mortgage_spread")
        derived["mortgage_spread"] = ("rates", "mortgage", "bps", "US", "Mortgage Spread")
        print(f"  ✓  mortgage_spread")

    return derived


# ══════════════════════════════════════════════════════════════════
# SUMMARY BUILDER
# ══════════════════════════════════════════════════════════════════

def get_latest(filename, col="value"):
    """Haal de laatste waarde op uit een processed bestand."""
    path = PROC / f"{filename}.csv"
    if not path.exists():
        return None, None
    try:
        df = pd.read_csv(path, parse_dates=["date"])
        df = df.dropna(subset=[col]).sort_values("date")
        if df.empty:
            return None, None
        last = df.iloc[-1]
        return last["date"], last[col]
    except Exception:
        return None, None


def build_summary(all_catalog):
    """
    Bouw een samenvattingstabel met voor elke reeks:
    - Laatste waarde en datum
    - % verandering week/maand/jaar (of absolute voor rentes)
    """
    rows = []

    for name, meta in all_catalog.items():
        cat, subcat, unit, country, desc = meta
        path = PROC / f"{name}.csv"
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path, parse_dates=["date"]).sort_values("date").dropna(subset=["value"])
            if df.empty:
                continue
            last = df.iloc[-1]
            row = {
                "name":     name,
                "description": desc,
                "category": cat,
                "subcategory": subcat,
                "unit":     unit,
                "country":  country,
                "last_date": last["date"].strftime("%Y-%m-%d"),
                "last_value": round(last["value"], 4),
            }
            # Voeg wijzigingen toe afhankelijk van beschikbare kolommen
            for col, label in [
                ("pct_1d", "chg_1d_pct"), ("chg_1d", "chg_1d_abs"),
                ("pct_1w", "chg_1w_pct"), ("chg_1w", "chg_1w_abs"),
                ("pct_1m", "chg_1m_pct"), ("chg_1m", "chg_1m_abs"),
                ("pct_1y", "chg_1y_pct"), ("chg_1y", "chg_1y_abs"),
                ("yoy_pct", "yoy_pct"),   ("pct_ytd", "ytd_pct"),
            ]:
                if col in df.columns:
                    row[label] = round(last[col], 4) if pd.notna(last[col]) else None
            rows.append(row)
        except Exception:
            continue

    summary = pd.DataFrame(rows)
    summary.to_csv(PROC / "summary.csv", index=False)
    print(f"\n  Samenvattingstabel: {len(summary)} reeksen → data/processed/summary.csv")
    return summary


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    start = datetime.now()
    processed_catalog = {}

    print(f"\n{'='*60}")
    print(f"  Processor — Global Macro Dashboard")
    print(f"{'='*60}\n")

    # ── Stap 1: Dagelijkse prijsdata ──────────────────────────────
    print("  [1/6] Dagelijkse prijsdata (indices, grondstoffen, crypto)...")
    ok = 0
    for name, meta in DAILY_PRICE.items():
        df = process_daily_price(name, meta)
        if df is not None:
            save(df, name)
            processed_catalog[name] = meta
            ok += 1
    print(f"        {ok}/{len(DAILY_PRICE)} verwerkt\n")

    # ── Stap 2: Dagelijkse % data (credit spreads) ────────────────
    print("  [2/6] Credit spreads en dagelijkse rentes...")
    ok = 0
    for name, meta in DAILY_PCT.items():
        df = process_daily_pct(name, meta)
        if df is not None:
            save(df, name)
            processed_catalog[name] = meta
            ok += 1
    print(f"        {ok}/{len(DAILY_PCT)} verwerkt\n")

    # ── Stap 3: Maandelijkse rentes en werkloosheid ───────────────
    print("  [3/6] Maandelijkse rentes, werkloosheid, obligaties...")
    ok = 0
    for name, meta in {**MONTHLY_RATE, **ECB_FX}.items():
        df = process_monthly_rate(name, meta) if name in MONTHLY_RATE \
             else process_ecb_fx(name, meta)
        if df is not None:
            save(df, name)
            processed_catalog[name] = meta
            ok += 1
    total = len(MONTHLY_RATE) + len(ECB_FX)
    print(f"        {ok}/{total} verwerkt\n")

    # ── Stap 4: CPI-indices, geldhoeveelheid en industriële productie ─
    print("  [4/6] CPI-indexreeksen, geldhoeveelheid en industriële productie (YoY% berekenen)...")
    ok = 0
    for name, meta in MONTHLY_INDEX.items():
        df = process_monthly_index(name, meta)
        if df is not None:
            save(df, name)
            processed_catalog[name] = meta
            ok += 1
    print(f"        {ok}/{len(MONTHLY_INDEX)} verwerkt\n")

    # ── Stap 5: OECD Composite Leading Indicators ─────────────────
    print("  [5/6] OECD Leading Indicators (CLI)...")
    ok = 0
    for name, meta in MONTHLY_CLI.items():
        df = process_monthly_cli(name, meta)
        if df is not None:
            save(df, name)
            processed_catalog[name] = meta
            ok += 1
    print(f"        {ok}/{len(MONTHLY_CLI)} verwerkt\n")

    # ── Stap 6: Afgeleide berekeningen ────────────────────────────
    print("  [6/6] Afgeleide berekeningen (reële rente, spreads)...")

    # ── Samenvattingstabel ────────────────────────────────────────
    print(f"\n  Samenvattingstabel bouwen...")
    build_summary(processed_catalog)

    duration = (datetime.now() - start).seconds
    print(f"\n{'='*60}")
    print(f"  Klaar in {duration}s — {len(processed_catalog)} reeksen verwerkt")
    print(f"  Output: data/processed/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
