"""
Fetch and cache stock data from watchlist
Stores historical data for all stocks to avoid repeated API calls
"""
import json
import sys
import io
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from bot import TradingBot
from logger_config import setup_logging, get_logger

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
setup_logging(log_level="INFO", log_to_file=True)
logger = get_logger(__name__)

CACHE_FILE = Path("data/cached_stock_data.json")


def load_watchlist(file_path: str = "watchlist.txt") -> List[str]:
    """Load tickers from watchlist file"""
    tickers = []
    watchlist_path = Path(file_path)
    
    if not watchlist_path.exists():
        logger.error(f"Watchlist file not found: {file_path}")
        return []
    
    with open(watchlist_path, 'r', encoding='utf-8') as f:
        for line in f:
            ticker = line.strip()
            # Skip empty lines and comments
            if ticker and not ticker.startswith('#'):
                tickers.append(ticker)
    
    logger.info(f"Loaded {len(tickers)} tickers from {file_path}")
    return tickers


def load_cached_data() -> Dict:
    """Load cached stock data if it exists"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data.get('stocks', {}))} stocks from cache")
                return data
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            return {"stocks": {}, "metadata": {}}
    return {"stocks": {}, "metadata": {}}


def save_cached_data(data: Dict):
    """Save stock data to cache file"""
    # Ensure data directory exists
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved {len(data.get('stocks', {}))} stocks to cache: {CACHE_FILE}")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")
        raise


def fetch_stock_data(ticker: str, bot: TradingBot) -> Dict:
    """Fetch historical data for a single stock"""
    try:
        logger.info(f"Fetching data for {ticker}...")
        
        # Get historical data (need at least 1 year for 52-week calculations)
        hist = bot.data_provider.get_historical_data(ticker, period="1y", interval="1d")
        
        if hist.empty or len(hist) < 200:
            logger.warning(f"Insufficient data for {ticker}: {len(hist)} rows")
            return {
                "ticker": ticker,
                "error": "Insufficient historical data",
                "data_available": False
            }
        
        # Get stock info
        stock_info = bot.data_provider.get_stock_info(ticker)
        
        # Convert DataFrame to dict for JSON serialization
        hist_dict = {
            "index": [str(idx) for idx in hist.index],
            "data": hist.to_dict('records')
        }
        
        return {
            "ticker": ticker,
            "data_available": True,
            "historical_data": hist_dict,
            "stock_info": stock_info,
            "data_points": len(hist),
            "date_range": {
                "start": str(hist.index[0]),
                "end": str(hist.index[-1])
            },
            "fetched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "data_available": False
        }


def fetch_all_data(force_refresh: bool = False, benchmark: str = "^GDAXI"):
    """Fetch data for all stocks in watchlist"""
    # Load watchlist
    tickers = load_watchlist()
    if not tickers:
        print("No tickers found in watchlist.txt")
        return
    
    # Load existing cache
    cached_data = load_cached_data() if not force_refresh else {"stocks": {}, "metadata": {}}
    cached_stocks = cached_data.get("stocks", {})
    
    # Initialize bot
    bot = TradingBot(skip_trading212=True, benchmark=benchmark)
    
    # Track progress
    total = len(tickers)
    fetched = 0
    skipped = 0
    errors = 0
    
    print(f"\n{'='*80}")
    print(f"FETCHING STOCK DATA")
    print(f"{'='*80}")
    print(f"Total tickers: {total}")
    print(f"Force refresh: {force_refresh}")
    print(f"Cache file: {CACHE_FILE}")
    print(f"{'='*80}\n")
    
    # Fetch data for each ticker
    for i, ticker in enumerate(tickers, 1):
        # Check if already cached and not forcing refresh
        if not force_refresh and ticker in cached_stocks:
            cached_entry = cached_stocks[ticker]
            if cached_entry.get("data_available", False):
                print(f"[{i}/{total}] {ticker:12s} - Using cached data")
                skipped += 1
                continue
        
        # Fetch new data
        print(f"[{i}/{total}] {ticker:12s} - Fetching...", end=" ", flush=True)
        result = fetch_stock_data(ticker, bot)
        
        if result.get("data_available", False):
            cached_stocks[ticker] = result
            fetched += 1
            print(f"✓ ({result.get('data_points', 0)} data points)")
        else:
            cached_stocks[ticker] = result
            errors += 1
            error_msg = result.get("error", "Unknown error")
            print(f"✗ Error: {error_msg}")
    
    # Update metadata
    cached_data["metadata"] = {
        "last_updated": datetime.now().isoformat(),
        "total_stocks": len(cached_stocks),
        "stocks_with_data": sum(1 for s in cached_stocks.values() if s.get("data_available", False)),
        "stocks_with_errors": sum(1 for s in cached_stocks.values() if "error" in s),
        "benchmark": benchmark
    }
    cached_data["stocks"] = cached_stocks
    
    # Save cache
    save_cached_data(cached_data)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"FETCHING COMPLETE")
    print(f"{'='*80}")
    print(f"Total tickers: {total}")
    print(f"Fetched: {fetched}")
    print(f"Skipped (cached): {skipped}")
    print(f"Errors: {errors}")
    print(f"Cache saved to: {CACHE_FILE}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and cache stock data from watchlist"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh all data (ignore cache)"
    )
    parser.add_argument(
        "--benchmark",
        default="^GDAXI",
        choices=["^GDAXI", "^FCHI", "^AEX", "^SSMI", "^OMX"],
        help="Benchmark index for relative strength (default: ^GDAXI)"
    )
    parser.add_argument(
        "--watchlist",
        default="watchlist.txt",
        help="Path to watchlist file (default: watchlist.txt)"
    )
    
    args = parser.parse_args()
    
    fetch_all_data(force_refresh=args.refresh, benchmark=args.benchmark)


if __name__ == "__main__":
    main()

