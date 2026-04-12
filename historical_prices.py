import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Accept ticker as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python historical_prices.py <TICKER> [years]")
    sys.exit(1)

ticker = sys.argv[1]
years = int(sys.argv[2]) if len(sys.argv) > 2 else 11

# Define the date range
end_date = datetime.today()
start_date = end_date - timedelta(days=years*365)

# Download stock data
data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1mo", auto_adjust=False)

# Keep only Close price
close = data[["Close"]].droplevel(1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]

# Save the data to output/ folder (relative to this script)
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)
csv_filename = os.path.join(output_dir, f"{ticker}_stock_data.csv")
close.to_csv(csv_filename, float_format="%.2f")

currency = yf.Ticker(ticker).info.get("currency", "unknown")
print(f"Currency: {currency}")
print(f"Data saved to {csv_filename}")