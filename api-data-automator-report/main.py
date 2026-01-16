import requests
import pandas as pd
from datetime import datetime
import os

API_URL = "https://api.coingecko.com/api/v3/coins/markets"

COINS = ["bitcoin", "ethereum", "solana", "dogecoin"]
VS_CURRENCY = "usd"

OUTPUT_DIR = "outputs"
LOG_DIR = "logs"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(f"{LOG_DIR}/run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch_data():
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": ",".join(COINS),
        "order": "market_cap_desc",
        "per_page": len(COINS),
        "page": 1,
        "sparkline": False
    }

    log("Fetching API data...")
    r = requests.get(API_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def transform_data(raw):
    log("Transforming data...")
    df = pd.DataFrame(raw)

    # Keep only useful columns
    df = df[[
        "id", "symbol", "name",
        "current_price", "market_cap",
        "price_change_percentage_24h",
        "high_24h", "low_24h",
        "last_updated"
    ]]

    # Clean types
    df["symbol"] = df["symbol"].str.upper()
    df["last_updated"] = pd.to_datetime(df["last_updated"])

    # Add a run timestamp
    df["report_generated_at"] = datetime.now()

    # Sort by market cap
    df = df.sort_values(by="market_cap", ascending=False).reset_index(drop=True)

    return df

def export_reports(df: pd.DataFrame):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    csv_path = f"{OUTPUT_DIR}/report_{ts}.csv"
    html_path = f"{OUTPUT_DIR}/report_{ts}.html"
    json_path = f"{OUTPUT_DIR}/report_{ts}.json"

    log(f"Saving CSV: {csv_path}")
    df.to_csv(csv_path, index=False)

    log(f"Saving JSON: {json_path}")
    df.to_json(json_path, orient="records", indent=2, date_format="iso")

    log(f"Saving HTML: {html_path}")
    html = f"""
    <html>
    <head>
        <title>Crypto Market Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #222; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>Crypto Market Report</h1>
        <p><b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        {df.to_html(index=False)}
    </body>
    </html>
    """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    log("Export complete.")

def main():
    try:
        raw = fetch_data()
        df = transform_data(raw)
        export_reports(df)
        log("Run finished successfully.")
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
