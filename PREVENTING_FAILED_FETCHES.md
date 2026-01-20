# Preventing Failed Stock Data Fetches

## Problem
Stocks like DHR can fail to fetch initially due to:
- Temporary API issues (Yahoo Finance rate limiting, network problems)
- Transient errors that resolve on retry
- Cached error states that persist even when data becomes available

## Solutions Implemented

### 1. Automatic Retry Logic
**File:** `01_fetch_stock_data.py`

**What it does:**
- Automatically retries failed fetches up to 2 times
- Uses exponential backoff (2s, 4s delays) between retries
- Retries stocks that previously failed when running without `--refresh`

**How it works:**
- When a stock has a cached error entry, it will be retried automatically
- Each fetch attempt has built-in retry logic (up to 3 total attempts)
- Errors are timestamped so you know when they occurred

### 2. Retry Failed Stocks Script
**File:** `04_retry_failed_stocks.py`

**What it does:**
- Identifies all stocks with failed fetches
- Optionally retries only old errors (older than 7 days)
- Allows you to manually retry failed stocks without re-fetching everything

**Usage:**
```bash
python 04_retry_failed_stocks.py
```

**Features:**
- Shows list of failed stocks before retrying
- Asks for confirmation before retrying
- Reports success/failure statistics
- Updates cache with fresh data

### 3. Better Error Tracking
**Improvements:**
- All errors now include timestamps (`fetched_at`)
- Error messages include more detail (e.g., "Insufficient historical data (73 rows, need ≥200)")
- Failed fetches are tracked with when they occurred

## Best Practices

### 1. Regular Retry of Failed Stocks
Run the retry script periodically:
```bash
python 04_retry_failed_stocks.py
```

This will catch stocks that:
- Had temporary API issues
- Were fetched during market closures
- Had network problems

### 2. Use Force Refresh When Needed
If you suspect data is stale:
```bash
python 01_fetch_stock_data.py --refresh
```

This will:
- Re-fetch ALL stocks (including ones with errors)
- Update all timestamps
- Catch stocks that now have data available

### 3. Check Failed Stocks Before Reports
Before generating reports, check for failed stocks:
```bash
python -c "import json; data = json.load(open('data/cached_stock_data.json')); failed = [t for t, s in data['stocks'].items() if not s.get('data_available')]; print(f'Failed stocks: {len(failed)}'); [print(f'  {t}: {s.get(\"error\", \"Unknown\")}') for t, s in [(t, data['stocks'][t]) for t in failed[:10]]]"
```

### 4. Monitor Data Freshness
The summary report shows data freshness. If you see:
- "Data is X day(s) old - consider refreshing"
- Many stocks with old timestamps

Run a refresh or retry failed stocks.

## Automatic Improvements

The system now:
1. **Retries failed stocks automatically** when running normal fetch (without --refresh)
2. **Tracks error timestamps** so you know when failures occurred
3. **Provides better error messages** with specific details
4. **Has built-in retry logic** for transient failures

## Manual Recovery

If a specific stock is missing:
1. Run the retry script: `python 04_retry_failed_stocks.py`
2. Or manually fetch: Create a small script to fetch that specific ticker
3. Or force refresh: `python 01_fetch_stock_data.py --refresh` (takes longer)

## Example: What Happened with DHR

**Before:**
- DHR failed during initial fetch (temporary API issue)
- Error was cached: `{"error": "Insufficient historical data", "data_available": false}`
- DHR was skipped in subsequent runs (cache had error entry)
- DHR didn't appear in reports

**After (with improvements):**
- DHR would be automatically retried on next fetch
- Or you can run `04_retry_failed_stocks.py` to retry all failed stocks
- DHR now appears in reports with fresh data

## Future Enhancements

Consider adding:
- Automatic daily/weekly retry of failed stocks
- Email/notification when stocks fail
- Validation script that checks all stocks in watchlist are in cache
- Automatic retry of stocks older than X days
