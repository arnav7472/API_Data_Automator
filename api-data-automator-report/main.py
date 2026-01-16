import requests
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import dataframe_image as dfi

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
    df_raw = pd.DataFrame(raw)

    df = df_raw.copy()

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

    return df_raw, df

def generate_pdf(df: pd.DataFrame, pdf_path: str):
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("Crypto Market Report", styles['Title'])
    elements.append(title)

    # Timestamp
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = Paragraph(f"Generated: {ts}", styles['Normal'])
    elements.append(subtitle)

    # Table data
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)

def generate_chart(df: pd.DataFrame, chart_path: str):
    plt.figure(figsize=(10, 6))
    plt.bar(df['symbol'], df['current_price'], color='skyblue')
    plt.title('Current Prices of Cryptocurrencies')
    plt.xlabel('Symbol')
    plt.ylabel('Price (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

def export_reports(df_raw: pd.DataFrame, df_cleaned: pd.DataFrame):
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    csv_path = f"{OUTPUT_DIR}/report_{ts}.csv"
    html_path = f"{OUTPUT_DIR}/report_{ts}.html"
    json_path = f"{OUTPUT_DIR}/report_{ts}.json"
    pdf_path = f"{OUTPUT_DIR}/report_{ts}.pdf"
    chart_path = f"{OUTPUT_DIR}/chart_{ts}.png"
    before_img_path = f"{OUTPUT_DIR}/before_data_{ts}.png"
    after_img_path = f"{OUTPUT_DIR}/after_data_{ts}.png"
    csv_img_path = f"{OUTPUT_DIR}/csv_preview_{ts}.png"

    log(f"Saving CSV: {csv_path}")
    df_cleaned.to_csv(csv_path, index=False)

    log(f"Saving JSON: {json_path}")
    df_cleaned.to_json(json_path, orient="records", indent=2, date_format="iso")

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
        {df_cleaned.to_html(index=False)}
    </body>
    </html>
    """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Generate PDF
    log(f"Generating PDF: {pdf_path}")
    generate_pdf(df_cleaned, pdf_path)

    # Generate chart
    log(f"Generating chart: {chart_path}")
    generate_chart(df_cleaned, chart_path)

    # Generate data screenshots
    log(f"Generating before data screenshot: {before_img_path}")
    dfi.export(df_raw.head(10), before_img_path, table_conversion='matplotlib')

    log(f"Generating after data screenshot: {after_img_path}")
    dfi.export(df_cleaned.head(10), after_img_path, table_conversion='matplotlib')

    log(f"Generating CSV preview screenshot: {csv_img_path}")
    dfi.export(df_cleaned.head(10), csv_img_path, table_conversion='matplotlib')

    log("Export complete.")

def main():
    try:
        raw = fetch_data()
        df_raw, df_cleaned = transform_data(raw)
        export_reports(df_raw, df_cleaned)
        log("Run finished successfully.")
    except Exception as e:
        log(f"ERROR: {e}")

if __name__ == "__main__":
    main()
