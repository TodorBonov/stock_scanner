"""Quick script to fetch and cache a single ticker"""
import json
import sys
import io
from pathlib import Path
from bot import TradingBot

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try different ticker formats
base_ticker = "GS71"
tickers_to_try = [base_ticker, f"{base_ticker}.L", f"{base_ticker}-GB", f"{base_ticker}.LON"]
cache_file = Path("data/cached_stock_data.json")

# Load existing cache
if cache_file.exists():
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"stocks": {}, "metadata": {}}

# Fetch data - try different formats
bot = TradingBot()
ticker = None
hist = None

for t in tickers_to_try:
    print(f"Trying {t}...")
    try:
        hist = bot.data_provider.get_historical_data(t, period="1y", interval="1d")
        if not hist.empty and len(hist) >= 200:
            ticker = t
            print(f"✓ Found data for {t} ({len(hist)} rows)")
            break
    except Exception as e:
        continue

if ticker is None or hist is None or hist.empty or len(hist) < 200:
    print(f"✗ Error: Could not find data for {base_ticker} in any format")
    print(f"   Tried: {', '.join(tickers_to_try)}")
    print(f"   Please verify the ticker symbol is correct")
    exit(1)

info = bot.data_provider.get_stock_info(ticker)

# Add to cache
data["stocks"][ticker] = {
    "ticker": ticker,
    "company_name": info.get("longName", "N/A"),
    "historical": {
        "index": [str(idx) for idx in hist.index],
        "data": hist.to_dict('records')
    },
    "info": info,
    "data_available": True
}

# Save cache
cache_file.parent.mkdir(parents=True, exist_ok=True)
with open(cache_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, default=str)

print(f"✓ Fetched and cached {ticker} ({len(hist)} data points)")
