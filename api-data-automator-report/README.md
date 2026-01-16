# API Data Automator + Report (Crypto Tracker)

This project fetches live crypto market data from CoinGecko API,
cleans/transforms it using Pandas, and generates exportable reports.

## Features
- Fetches live API data (CoinGecko)
- Data cleaning + transformation with Pandas
- Generates CSV + JSON + HTML + PDF reports
- Creates data visualization charts
- Generates before/after data cleaning screenshots
- Generates CSV preview screenshots
- Logs every run
- Can be scheduled with cron / Task Scheduler

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

## Outputs
- `report_[timestamp].csv` - Cleaned CSV data
- `report_[timestamp].html` - HTML report with table
- `report_[timestamp].json` - JSON data export
- `report_[timestamp].pdf` - PDF report
- `chart_[timestamp].png` - Bar chart of current prices
- `before_data_[timestamp].png` - Screenshot of raw data before cleaning
- `after_data_[timestamp].png` - Screenshot of cleaned data after transformation
- `csv_preview_[timestamp].png` - Screenshot preview of the CSV data
