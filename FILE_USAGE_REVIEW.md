# File Usage Review

**Date:** 2026-01-09  
**Purpose:** Identify all unused files that can be removed

---

## ✅ **ACTIVE FILES** (Used in Main Workflow)

### Core Scripts
| File | Used By | Purpose |
|------|---------|---------|
| `01_fetch_stock_data.py` | Main workflow | Fetches and caches stock data |
| `02_generate_full_report.py` | Main workflow | Generates summary and detailed reports |
| `minervini_scanner.py` | `02_generate_full_report.py`, `bot.py` | Core Minervini SEPA logic |
| `bot.py` | `01_fetch_stock_data.py`, `02_generate_full_report.py` | Main bot interface |
| `data_provider.py` | `bot.py`, `minervini_scanner.py` | Data fetching (yfinance, Alpha Vantage) |
| `trading212_client.py` | `bot.py` | Trading212 API client (optional) |
| `logger_config.py` | All scripts | Logging configuration |
| `validators.py` | `bot.py` | Input validation |
| `config.py` | `bot.py`, `validators.py`, `trading212_client.py` | Configuration constants |
| `ticker_utils.py` | `data_provider.py`, `trading212_client.py` | Ticker cleaning utilities |

### Data & Config Files
| File | Used By | Purpose |
|------|---------|---------|
| `watchlist.txt` | `01_fetch_stock_data.py` | List of stocks to scan |
| `requirements.txt` | Setup | Python dependencies |
| `config.example.env` | Reference | Environment variable template |
| `data/cached_stock_data.json` | `01_fetch_stock_data.py`, `02_generate_full_report.py` | Cached stock data |

---

## ❌ **UNUSED FILES** (Removed)

### Temporary/Debug Scripts
| File | Status | Reason |
|------|--------|--------|
| ~~`fetch_single_ticker.py`~~ | **DELETED** | Temporary script for testing GS71 ticker |
| ~~`check_roche_base.py`~~ | **DELETED** | Temporary analysis script for Roche |
| ~~`compare_roche_final.py`~~ | **DELETED** | Temporary comparison script |

### Old Result Files
| File | Status | Reason |
|------|--------|--------|
| ~~`scan_results.json`~~ | **DELETED** | Old scan results format (replaced by cached data) |
| ~~`scan_results_latest.json`~~ | **DELETED** | Old scan results format (replaced by cached data) |

### Outdated Documentation
| File | Status | Reason |
|------|--------|--------|
| ~~`SCRIPTS_REFERENCE.md`~~ | **DELETED** | References old scripts (main.py, summary_report.py, etc.) that no longer exist |
| ~~`NEW_WORKFLOW.md`~~ | **DELETED** | References old script names (fetch_stock_data.py, generate_full_report.py) - scripts now have 01_/02_ prefixes |
| ~~`WHAT_IS_MISSING_FOR_VOLUME_AND_BREAKOUT.md`~~ | **DELETED** | Explains issues that have been fixed |

### Reference Documentation (Keep for Reference)
| File | Status | Recommendation |
|------|--------|----------------|
| `CODE_REVIEW_AND_IMPROVEMENTS.md` | Reference | Keep - useful for future improvements |
| `BASE_IDENTIFICATION_ALTERNATIVES.md` | Reference | Keep - useful for future improvements |
| `MINERVINI_LOGIC_IMPROVEMENTS.md` | Reference | Keep - documents recent improvements |
| `CONFIGURATION_VARIABLES.md` | Reference | Keep - useful reference for all variables |

---

## 📋 **SUMMARY**

### Files to DELETE (7 files):
1. `fetch_single_ticker.py` - Temporary debug script
2. `check_roche_base.py` - Temporary analysis script
3. `compare_roche_final.py` - Temporary comparison script
4. `scan_results.json` - Old results format
5. `scan_results_latest.json` - Old results format
6. `SCRIPTS_REFERENCE.md` - Outdated (references non-existent scripts)
7. `NEW_WORKFLOW.md` - Outdated (wrong script names)
8. `WHAT_IS_MISSING_FOR_VOLUME_AND_BREAKOUT.md` - Outdated (issues fixed)

### Files to KEEP (Reference Docs):
- `CODE_REVIEW_AND_IMPROVEMENTS.md` - Useful for future improvements
- `BASE_IDENTIFICATION_ALTERNATIVES.md` - Useful for future improvements
- `MINERVINI_LOGIC_IMPROVEMENTS.md` - Documents recent improvements
- `CONFIGURATION_VARIABLES.md` - Useful reference for all variables
- `README.md` - Main documentation

---

## 🔍 **VERIFICATION**

**Main Workflow:**
```
01_fetch_stock_data.py
  └── Uses: bot.py, logger_config.py
       └── bot.py uses: trading212_client.py, data_provider.py, minervini_scanner.py, validators.py, config.py
            └── data_provider.py uses: ticker_utils.py, logger_config.py
            └── trading212_client.py uses: ticker_utils.py, logger_config.py, config.py
            └── minervini_scanner.py uses: data_provider.py, logger_config.py

02_generate_full_report.py
  └── Uses: bot.py, minervini_scanner.py, data_provider.py, logger_config.py
       └── (same dependencies as above)
```

**All other files are NOT imported or used by the main workflow.**

---

## 🗑️ **RECOMMENDED ACTIONS**

1. **Delete temporary scripts:**
   - `fetch_single_ticker.py`
   - `check_roche_base.py`
   - `compare_roche_final.py`

2. **Delete old result files:**
   - `scan_results.json`
   - `scan_results_latest.json`

3. **Delete outdated documentation:**
   - `SCRIPTS_REFERENCE.md`
   - `NEW_WORKFLOW.md`
   - `WHAT_IS_MISSING_FOR_VOLUME_AND_BREAKOUT.md`

4. **Keep reference documentation:**
   - All `.md` files except the 3 outdated ones above

---

**Total files to delete: 8 files**
