# Scripts Reference Guide

This document describes all scripts in the Trading212 Minervini Scanner project and their purposes.

---

## 🎯 **CORE SCRIPTS** (Main Functionality)

### `main.py`
**Purpose:** Main CLI interface for the Minervini SEPA Scanner  
**Usage:**
```bash
python main.py scan TICKER                    # Scan single stock
python main.py scan-multi TICKER1 TICKER2     # Scan multiple stocks
python main.py scan-file watchlist.txt        # Scan from file
python main.py scan-file watchlist.txt --json # Output as JSON
```
**What it does:**
- Entry point for all scanning operations
- Handles command-line arguments
- Formats and displays results
- Supports JSON output for programmatic use

---

### `bot.py`
**Purpose:** Main trading bot interface that orchestrates scanning  
**What it does:**
- Initializes Trading212Client, StockDataProvider, and MinerviniScanner
- Provides high-level methods: `scan_stock()`, `scan_stocks()`, `scan_from_file()`, `search_and_scan()`
- Handles validation and error management
- Used by `main.py` internally

---

### `minervini_scanner.py`
**Purpose:** Core Minervini SEPA methodology implementation  
**What it does:**
- Implements all 5 Minervini criteria checks:
  - Trend & Structure (NON-NEGOTIABLE)
  - Base Quality
  - Relative Strength
  - Volume Signature
  - Breakout Rules
- Calculates grades (A+, A, B, C, F)
- Identifies base patterns
- Calculates RSI, relative strength, volume patterns
- **This is the heart of the scanner**

---

### `data_provider.py`
**Purpose:** Fetches stock data from multiple sources  
**What it does:**
- Primary: Yahoo Finance (yfinance) - free, no API key
- Fallback: Alpha Vantage API (requires API key)
- Final fallback: Trading 212 API
- Provides historical data, stock info, relative strength calculations
- Handles data fetching errors and fallbacks

---

### `trading212_client.py`
**Purpose:** Trading 212 API client (optional)  
**What it does:**
- Connects to Trading 212 API for stock search
- Fetches instrument metadata
- Used for searching stocks by name
- **Optional** - scanner works without it (uses yfinance)

---

## 📊 **ANALYSIS & REPORTING SCRIPTS**

### `run_detailed_analysis.py` ⭐ **RECOMMENDED**
**Purpose:** Run scan with detailed criteria explanations and calculations  
**Usage:**
```bash
python run_detailed_analysis.py                    # All stocks
python run_detailed_analysis.py --filter IDR        # Filter by ticker
```
**What it does:**
- Runs full scan from watchlist
- Shows detailed breakdown for each criterion:
  - What each check means
  - How it's calculated
  - Formula used
  - Threshold required
  - Actual values
  - Why it passed/failed
- **Best for understanding WHY a stock passed/failed**

---

### `summary_report.py` ⭐ **RECOMMENDED**
**Purpose:** Generate comprehensive summary report with grade distribution  
**Usage:**
```bash
python summary_report.py
```
**What it does:**
- Runs full scan automatically
- Generates summary statistics:
  - Grade distribution (A+, A, B, C, F)
  - Position size recommendations
  - Criteria pass rates
  - Top stocks by grade
  - Stocks with errors
- **Best for getting overview of all stocks**

---

### `run_and_analyze.py`
**Purpose:** Run scan and show results ordered by grade  
**Usage:**
```bash
python run_and_analyze.py
```
**What it does:**
- Runs scan from watchlist
- Groups results by grade
- Shows summary for each stock
- **Simpler than detailed analysis, good for quick overview**

---

### `analyze_results.py`
**Purpose:** Analyze existing JSON scan results  
**Usage:**
```bash
python analyze_results.py < scan_results.json
# OR
python main.py scan-file watchlist.txt --json | python analyze_results.py
```
**What it does:**
- Reads JSON results from file or stdin
- Analyzes and sorts by grade
- Shows summary statistics
- **Useful for analyzing saved results**

---

### `run_and_analyze_detailed.py`
**Purpose:** Similar to `run_detailed_analysis.py` (alternative version)  
**Note:** Appears to be a duplicate/alternative implementation

---

## 🔧 **UTILITY SCRIPTS**

### `config.py`
**Purpose:** Configuration management  
**What it does:**
- Loads environment variables
- Provides default configuration paths
- Manages API keys and settings

---

### `validators.py`
**Purpose:** Input validation  
**What it does:**
- Validates ticker symbols
- Validates file paths
- Validates API keys
- Masks credentials in logs

---

### `logger_config.py`
**Purpose:** Logging configuration  
**What it does:**
- Sets up logging system
- Configures log levels
- Manages log files
- Used throughout the application

---

### `ticker_utils.py`
**Purpose:** Ticker symbol utilities  
**What it does:**
- Cleans ticker symbols
- Handles different exchange formats
- Converts between formats

---

## 📝 **WATCHLIST MANAGEMENT SCRIPTS**

### `add_wisdomtree_manual.py`
**Purpose:** Manually add WisdomTree ETF holdings to watchlist  
**Usage:**
```bash
python add_wisdomtree_manual.py
```
**What it does:**
- Adds curated list of major WisdomTree ETF holdings
- Appends to `watchlist.txt`
- **Already executed** - holdings are in watchlist

---

### `add_wisdomtree_holdings.py`
**Purpose:** Attempt to automatically fetch WisdomTree holdings  
**Status:** Experimental - may not work reliably  
**What it does:**
- Tries to fetch ETF holdings programmatically
- Uses web scraping or API calls
- **Less reliable than manual version**

---

### `get_wisdomtree_stocks.py`
**Purpose:** Alternative method to get WisdomTree ETF stocks  
**Status:** Experimental  
**What it does:**
- Tries multiple methods to get ETF holdings
- Web scraping from ETFDB, WisdomTree website
- Uses yfinance to get ETF info

---

### `fetch_wisdomtree_holdings.py`
**Purpose:** Another attempt at fetching WisdomTree holdings  
**Status:** Experimental  
**What it does:**
- Similar to other WisdomTree scripts
- Tries different data sources

---

## 📄 **DOCUMENTATION FILES**

### `README.md`
**Purpose:** Main project documentation  
**Contains:**
- Setup instructions
- Usage examples
- Minervini criteria explanations
- Configuration guide

---

### `CODE_REVIEW_AND_IMPROVEMENTS.md`
**Purpose:** Comprehensive code review with improvement suggestions  
**Contains:**
- 48+ improvement suggestions
- Priority rankings
- Implementation recommendations

---

### `BASE_IDENTIFICATION_ALTERNATIVES.md`
**Purpose:** Alternative approaches for base identification  
**Contains:**
- 7 different base identification methods
- Code examples
- Pros/cons analysis

---

### `WHAT_IS_MISSING_FOR_VOLUME_AND_BREAKOUT.md`
**Purpose:** Explains why Volume Signature and Breakout Rules can't be evaluated  
**Contains:**
- Explanation of base requirements
- Why stocks fail base identification
- What's needed for evaluation

---

## 🗂️ **DATA FILES**

### `watchlist.txt`
**Purpose:** List of stocks to scan  
**Format:** One ticker per line, `#` for comments  
**Contains:** 232+ stocks including:
- US Tech stocks
- Quantum computing stocks
- Pharma stocks (US & EU)
- European defense stocks
- WisdomTree ETF holdings

---

### `scan_results.json`
**Purpose:** Saved scan results (JSON format)  
**Contains:** Previous scan results for analysis

---

### `scan_results_latest.json`
**Purpose:** Latest scan results (may be incomplete due to encoding)

---

## 📋 **QUICK REFERENCE - Which Script to Use?**

| Task | Script | Command |
|------|--------|---------|
| **Scan single stock** | `main.py` | `python main.py scan TICKER` |
| **Scan all stocks** | `main.py` | `python main.py scan-file watchlist.txt` |
| **Get summary report** | `summary_report.py` | `python summary_report.py` |
| **Detailed analysis** | `run_detailed_analysis.py` | `python run_detailed_analysis.py --filter TICKER` |
| **Quick overview** | `run_and_analyze.py` | `python run_and_analyze.py` |
| **JSON output** | `main.py` | `python main.py scan-file watchlist.txt --json` |

---

## 🎯 **RECOMMENDED WORKFLOW**

1. **Daily/Weekly Scan:**
   ```bash
   python summary_report.py
   ```
   Get overview of all stocks

2. **Deep Dive on Specific Stock:**
   ```bash
   python run_detailed_analysis.py --filter TICKER
   ```
   Understand why stock passed/failed

3. **Quick Check:**
   ```bash
   python main.py scan TICKER
   ```
   Quick scan of single stock

4. **Programmatic Analysis:**
   ```bash
   python main.py scan-file watchlist.txt --json > results.json
   ```
   Save results for custom analysis

---

## 🔍 **Script Dependencies**

```
main.py
  └── bot.py
      ├── minervini_scanner.py
      │   └── data_provider.py
      │       ├── trading212_client.py (optional)
      │       └── ticker_utils.py
      ├── validators.py
      └── logger_config.py

run_detailed_analysis.py
  └── (calls main.py internally)

summary_report.py
  └── (calls main.py internally)
```

---

## 📝 **Notes**

- **Core scripts** (main.py, bot.py, minervini_scanner.py, data_provider.py) are essential
- **Analysis scripts** (run_detailed_analysis.py, summary_report.py) are convenience wrappers
- **WisdomTree scripts** are one-time utilities (already executed)
- **Experimental scripts** may not work reliably - use manual methods instead

---

**Last Updated:** 2024-01-05

