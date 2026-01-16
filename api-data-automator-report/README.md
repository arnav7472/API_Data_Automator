# API Data Automator + Report (Crypto Tracker)

This project fetches live crypto market data from CoinGecko API,
cleans/transforms it using Pandas, and generates exportable reports.

## Features
- Fetches live API data (CoinGecko)
- Data cleaning + transformation with Pandas
- Generates CSV + JSON + HTML report
- Logs every run
- Can be scheduled with cron / Task Scheduler

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
