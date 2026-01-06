# New Workflow - Reorganized Scripts

## Overview

The project has been reorganized into two main scripts that separate data fetching from analysis:

1. **`fetch_stock_data.py`** - Fetches and caches all stock data
2. **`generate_full_report.py`** - Analyzes cached data and generates reports

---

## 📥 **Step 1: Fetch Stock Data**

### Purpose
Fetches historical data for all stocks in `watchlist.txt` and caches it to avoid repeated API calls.

### Usage

**Basic (uses cache if available):**
```bash
python fetch_stock_data.py
```

**Force refresh all data:**
```bash
python fetch_stock_data.py --refresh
```

**Change benchmark:**
```bash
python fetch_stock_data.py --benchmark ^FCHI
```

**Custom watchlist:**
```bash
python fetch_stock_data.py --watchlist my_watchlist.txt
```

### What it does:
- Reads all tickers from `watchlist.txt`
- Fetches 1 year of historical data for each stock
- Caches data to `data/cached_stock_data.json`
- Skips already-cached stocks (unless `--refresh` is used)
- Shows progress for each stock
- Handles errors gracefully

### Output:
- Cache file: `data/cached_stock_data.json`
- Console: Progress and summary statistics

---

## 📊 **Step 2: Generate Full Report**

### Purpose
Analyzes all cached stock data using Minervini SEPA methodology and generates comprehensive reports.

### Usage

**Generate both reports (default):**
```bash
python generate_full_report.py
```

**Single stock analysis:**
```bash
python generate_full_report.py --ticker IDR.MC
```

**Refresh data first, then analyze:**
```bash
python generate_full_report.py --refresh
```

**Summary only:**
```bash
python generate_full_report.py --summary-only
```

**Detailed only:**
```bash
python generate_full_report.py --detailed-only
```

**Change benchmark:**
```bash
python generate_full_report.py --benchmark ^FCHI
```

### What it does:
- Loads cached data from `data/cached_stock_data.json`
- Runs Minervini SEPA analysis on all stocks
- Generates two reports:
  1. **Summary Report** - Grade distribution, statistics, top stocks
  2. **Detailed Report** - Complete analysis for each stock (highest to lowest grade)

### Output:
- Console: Both reports printed
- Files (with timestamp):
  - `reports/summary_report_YYYYMMDD_HHMMSS.txt`
  - `reports/detailed_report_YYYYMMDD_HHMMSS.txt`

---

## 🔄 **Typical Workflow**

### Daily/Weekly Analysis:
```bash
# Step 1: Fetch fresh data (optional - only if you want to refresh)
python fetch_stock_data.py --refresh

# Step 2: Generate reports
python generate_full_report.py
```

### Quick Analysis (using cached data):
```bash
# Just generate reports (uses existing cache)
python generate_full_report.py
```

### Single Stock Deep Dive:
```bash
# Analyze one stock in detail
python generate_full_report.py --ticker IDR.MC
```

---

## 📁 **File Structure**

```
Trading212/
├── data/
│   └── cached_stock_data.json    # Cached stock data
├── reports/
│   ├── summary_report_20240105_163000.txt
│   └── detailed_report_20240105_163000.txt
├── fetch_stock_data.py           # Step 1: Fetch & cache data
├── generate_full_report.py       # Step 2: Analyze & report
└── watchlist.txt                 # List of stocks to scan
```

---

## ⚙️ **Parameters Reference**

### `fetch_stock_data.py`
- `--refresh` - Force refresh all data (ignore cache)
- `--benchmark` - Benchmark index (^GDAXI, ^FCHI, ^AEX, ^SSMI, ^OMX)
- `--watchlist` - Path to watchlist file (default: watchlist.txt)

### `generate_full_report.py`
- `--ticker TICKER` - Analyze single stock only
- `--refresh` - Refresh data before analysis
- `--benchmark` - Benchmark index
- `--summary-only` - Generate only summary report
- `--detailed-only` - Generate only detailed report

---

## 💡 **Benefits of New Structure**

1. **Faster Analysis** - No repeated API calls, uses cached data
2. **Separation of Concerns** - Data fetching separate from analysis
3. **Flexible** - Can refresh data independently, run analysis multiple times
4. **Timestamped Reports** - All reports saved with timestamps for comparison
5. **Single Stock Support** - Can analyze individual stocks via parameter

---

## 🔧 **Migration from Old Scripts**

The old scripts still work, but the new workflow is recommended:

| Old Script | New Equivalent |
|------------|----------------|
| `main.py scan-file watchlist.txt` | `fetch_stock_data.py` then `generate_full_report.py` |
| `summary_report.py` | `generate_full_report.py` (summary part) |
| `run_detailed_analysis.py` | `generate_full_report.py` (detailed part) |
| `main.py scan TICKER` | `generate_full_report.py --ticker TICKER` |

---

## 📝 **Notes**

- Cache file is in JSON format (human-readable)
- Cache persists between runs (use `--refresh` to update)
- Reports are saved with timestamps for historical comparison
- Both console and file outputs provided
- Single stock analysis uses same cached data (fast)

---

**Ready to use!** Start with `python fetch_stock_data.py` to cache your data, then run `python generate_full_report.py` for analysis.

