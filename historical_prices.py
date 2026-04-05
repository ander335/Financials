import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys

# Accept ticker as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <TICKER> <years optional>")
    sys.exit(1)

ticker = sys.argv[1]
years = int(sys.argv[2]) if len(sys.argv) > 2 else 11

# Define the date range: 11 years from today
end_date = datetime.today()
start_date = end_date - timedelta(days=years*365)

# Download stock data
data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1mo", auto_adjust=False)

# Save the data to a CSV file
csv_filename = f"{ticker}_stock_data.csv"
data.to_csv(csv_filename)

print(f"Data saved to {csv_filename}")