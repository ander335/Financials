import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="Download monthly historical close prices.")
parser.add_argument("ticker", help="Ticker symbol to download.")
parser.add_argument("years", nargs="?", type=int, default=11, help="Number of years to download.")
parser.add_argument("--output", default=str(REPO_ROOT / "output"), help="Folder where the CSV should be saved.")
args = parser.parse_args()

ticker = args.ticker
years = args.years

# Define the date range
end_date = datetime.today()
start_date = end_date - timedelta(days=years*365)

# Download stock data
data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1mo", auto_adjust=False)

# Keep only Close price
close = data[["Close"]].droplevel(1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]

# Save the data to the requested output folder.
output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)
csv_filename = output_dir / f"{ticker}_stock_data.csv"
close.to_csv(csv_filename, float_format="%.2f")

currency = yf.Ticker(ticker).info.get("currency", "unknown")
print(f"Currency: {currency}")
print(f"Data saved to {csv_filename}")
