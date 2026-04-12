# Download annual FX exchange rates for a currency pair.

# Steps

## Parse arguments
- The command is invoked as `/fx-rates FROM TO [--year-end MONTH]`
  - Examples: `/fx-rates JPY USD`, `/fx-rates JPY USD --year-end 3`
- FROM = base currency, TO = quote currency (ISO 4217 codes)
- --year-end MONTH = fiscal year-end month 1-12 (default 12 = December)
  - Use 3 for March (Japanese companies: Toyota, Sony, Honda…)
  - Use 6 for June, 9 for September, etc.
- If FROM or TO are missing, ask the user for the two currency codes before proceeding.

## Run the script
```
python fx_rates.py FROM TO [--year-end MONTH]
```
- Wait for the script to complete.
- If the script exits with an error (e.g. unsupported currency code), show the error and stop.

## Show the result
- Display the output table printed by the script.
- Note the output file path.
- Data source: Frankfurter API (backed by ECB and major central banks), free, no API key.
