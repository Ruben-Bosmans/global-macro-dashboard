import subprocess
import sys
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# GLOBAL MACRO DASHBOARD — Master Collector
# Voer dit script dagelijks uit via Windows Task Scheduler
# ══════════════════════════════════════════════════════════════════

LOG_FILE = "logs/run_log.txt"

COLLECTORS = [
    ("FRED",               "collectors/fred_collector.py"),
    ("FRED International", "collectors/fred_international.py"),
    ("BIS",                "collectors/bis_collector.py"),
    ("Stocks & Indices",   "collectors/yfinance_collector.py"),
    ("Crypto",             "collectors/crypto_collector.py"),
    ("Credit Spreads",     "collectors/credit_collector.py"),
    ("ECB",                "collectors/ecb_collector.py"),
    ("ECB Fixes",          "collectors/ecb_fixes.py"),
    ("World Bank",         "collectors/worldbank_collector.py"),
    ("OECD",               "collectors/oecd_collector.py"),
    ("IMF",                "collectors/imf_collector.py"),
    ("Processor",          "process.py"),
    ("Compass",            "compass.py"),
    ("Push to GitHub",     "push_data.py"),
]

def log(message):
    """Schrijf naar terminal én logbestand."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_collector(name, script_path):
    """Voer één collector uit en geef succes/fout terug."""
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"  # Forceer UTF-8 output

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding="utf-8",              # Lees output als UTF-8
            timeout=300,
            env=env
        )
        if result.returncode == 0:
            log(f"  ✓ {name}")
            return True
        else:
            log(f"  ✗ {name} — fout:")
            for line in result.stderr.splitlines()[-5:]:
                log(f"    {line}")
            return False
    except subprocess.TimeoutExpired:
        log(f"  ✗ {name} — timeout (>5 min)")
        return False
    except Exception as e:
        log(f"  ✗ {name} — {e}")
        return False

def main():
    start = datetime.now()
    log("=" * 50)
    log("Global Macro Dashboard — Dagelijkse update")
    log("=" * 50)

    succeeded = []
    failed    = []

    for name, path in COLLECTORS:
        if run_collector(name, path):
            succeeded.append(name)
        else:
            failed.append(name)

    duration = (datetime.now() - start).seconds
    log("-" * 50)
    log(f"Klaar in {duration}s — "
        f"{len(succeeded)} gelukt, {len(failed)} mislukt")
    if failed:
        log(f"Mislukt: {', '.join(failed)}")
    log("=" * 50)

if __name__ == "__main__":
    main()
