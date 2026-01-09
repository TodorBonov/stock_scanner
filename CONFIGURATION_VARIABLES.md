# Configuration Variables Reference

This document lists all configuration variables, thresholds, and constants used in the Minervini SEPA scanner and where they are located.

---

## 📍 Primary Location: `minervini_scanner.py`

**All Minervini-specific variables are currently hardcoded in this file.** They are not in a separate config file yet.

---

## 📊 TREND & STRUCTURE Variables

**Location:** `minervini_scanner.py` - `_check_trend_structure()` method (lines ~116-238)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `SMA_50_PERIOD` | `50` | 147 | 50-day Simple Moving Average |
| `SMA_150_PERIOD` | `150` | 148 | 150-day Simple Moving Average |
| `SMA_200_PERIOD` | `200` | 149 | 200-day Simple Moving Average |
| `SMA_SLOPE_LOOKBACK_DAYS` | `20` | 182 | Days to compare for SMA slope check |
| `SMA_SLOPE_LOOKBACK_SHORT` | `10` | 197 | Shorter lookback if insufficient data |
| `PRICE_FROM_52W_LOW_MIN_PCT` | `30` | 204 | Minimum % above 52-week low |
| `PRICE_FROM_52W_HIGH_MAX_PCT` | `15` | 210 | Maximum % below 52-week high |
| `PRICE_TOO_CLOSE_TO_HIGH_PCT` | `10` | 213 | Warning if within 10% of 52W high (late stage) |
| `MIN_DATA_DAYS` | `200` | 142 | Minimum days of data required |

---

## 📈 BASE QUALITY Variables

**Location:** `minervini_scanner.py` - `_check_base_quality()` method (lines ~240-329)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `BASE_LENGTH_MIN_WEEKS` | `3` | 276 | Minimum base length in weeks |
| `BASE_LENGTH_MAX_WEEKS` | `8` | 276 | Maximum base length in weeks |
| `BASE_DEPTH_MAX_PCT` | `25` | 281 | Maximum base depth % (acceptable) |
| `BASE_DEPTH_ELITE_PCT` | `15` | 283 | Elite base depth % (preferred) |
| `BASE_DEPTH_WARNING_PCT` | `20` | 284 | Warning threshold for base depth |
| `BASE_VOLATILITY_MULTIPLIER` | `1.5` | 298 | Base volatility vs avg volatility (reject if >1.5x) |
| `CLOSE_POSITION_MIN_PCT` | `50` | 301 | Minimum close position in daily range (was 60) |
| `VOLUME_CONTRACTION_WARNING` | `0.95` | 319 | Volume contraction warning threshold (was 0.90) |
| `LOOKBACK_DAYS` | `60` | 259 | Days to look back for base identification |

---

## 🔍 BASE IDENTIFICATION Variables

**Location:** `minervini_scanner.py` - `_identify_base()` method (lines ~331-445)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `VOLATILITY_WINDOW` | `10` | 346 | Rolling window for volatility calculation (~2 weeks) |
| `LOW_VOL_THRESHOLD_MULTIPLIER` | `0.85` | 363 | Volatility threshold multiplier (was 0.75) |
| `LOW_VOL_MIN_DAYS` | `10` | 357 | Minimum consecutive low volatility days |
| `LOW_VOL_PERCENTAGE_THRESHOLD` | `0.55` | 384 | Percentage of days that must be low vol (was 0.60) |
| `LOW_VOL_MIN_DAYS_FOR_PCT` | `15` | 384 | Minimum days required for percentage check |
| `BASE_LENGTH_MIN_WEEKS_IDENTIFY` | `2` | 375 | Minimum weeks for base identification |
| `BASE_LENGTH_MAX_WEEKS_IDENTIFY` | `12` | 375 | Maximum weeks for base identification |
| `BASE_DEPTH_MAX_PCT_IDENTIFY` | `35` | 375 | Maximum depth % for base identification |
| `RANGE_30D_THRESHOLD_PCT` | `15` | 423 | 30-day price range threshold |
| `RANGE_60D_THRESHOLD_PCT` | `25` | 423 | 60-day price range threshold |
| `ADVANCE_DECLINE_THRESHOLD_PCT` | `10` | 370 | Reject if price declined >10% (not a base) |

---

## 💪 RELATIVE STRENGTH Variables

**Location:** `minervini_scanner.py` - `_check_relative_strength()` method (lines ~447-549)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `RSI_PERIOD` | `14` | 464 | RSI calculation period |
| `RSI_MIN_THRESHOLD` | `60` | 467 | Minimum RSI value required |
| `RS_LINE_DECLINE_WARNING_PCT` | `5` | 531 | Warning if RS line >5% below recent high |
| `RS_LINE_DECLINE_FAIL_PCT` | `10` | 533 | Fail if RS line >10% below recent high |
| `RS_LOOKBACK_DAYS` | `60` | 520 | Days to look back for RS line calculation |
| `RS_TREND_LOOKBACK_DAYS` | `20` | 528 | Days to check RS line trend |

---

## 📊 VOLUME SIGNATURE Variables

**Location:** `minervini_scanner.py` - `_check_volume_signature()` method (lines ~562-666)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `VOLUME_CONTRACTION_WARNING` | `0.9` | 627 | Volume contraction warning (base volume vs pre-base) |
| `BREAKOUT_VOLUME_MULTIPLIER` | `1.4` | 643 | Minimum volume increase for breakout (1.4x = 40%) |
| `HEAVY_SELL_VOLUME_MULTIPLIER` | `1.5` | 651 | Heavy sell volume threshold (1.5x base volume) |
| `RECENT_DAYS_FOR_VOLUME` | `5` | 630 | Days to check for recent volume |
| `AVG_VOLUME_LOOKBACK_DAYS` | `20` | 640 | Days for average volume calculation |

---

## 🚀 BREAKOUT RULES Variables

**Location:** `minervini_scanner.py` - `_check_breakout_rules()` method (lines ~668-771)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `PIVOT_CLEARANCE_PCT` | `2` | 708 | Minimum % above base high to clear pivot |
| `BREAKOUT_LOOKBACK_DAYS` | `5` | 700 | Days to check for breakout |
| `CLOSE_POSITION_MIN_PCT` | `70` | 738 | Minimum close position in range (was 75%, top 30% vs 25%) |
| `VOLUME_EXPANSION_MIN` | `1.2` | 751 | Minimum volume expansion (was 1.4x, now 1.2x = 20%) |
| `AVG_VOLUME_LOOKBACK_DAYS` | `20` | 749 | Days for average volume calculation |

---

## 💰 BUY/SELL PRICE Variables

**Location:** `minervini_scanner.py` - `_calculate_buy_sell_prices()` method (lines ~837-920)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `STOP_LOSS_PCT` | `7.5` | 872 | Stop loss % below buy price (Minervini's 7-8% rule) |
| `PROFIT_TARGET_1_PCT` | `22.5` | 876 | First profit target % above entry (20-25% range) |
| `PROFIT_TARGET_2_PCT` | `45.0` | 880 | Second profit target % above entry (40-50% range) |
| `BUY_PRICE_BUFFER_PCT` | `2` | 708 | Buy when price is 2% above pivot (breakout confirmation) |
| `BUY_PRICE_ADJUSTMENT_PCT` | `0.995` | 866 | Slight adjustment if already above pivot (99.5% of current) |

---

## 🎯 GRADING Variables

**Location:** `minervini_scanner.py` - `_calculate_grade()` method (lines ~773-835)

| Variable | Value | Line | Description |
|----------|-------|------|-------------|
| `MAX_FAILURES_FOR_A` | `2` | 745 | Maximum failures for A grade |
| `MAX_FAILURES_FOR_B` | `4` | 749 | Maximum failures for B grade |
| `CRITICAL_FAILURE_GRADE` | `"F"` | 738 | Grade if trend & structure fails |

---

## 📁 Other Configuration Files

### `config.py`
**Location:** Root directory  
**Contains:** API rate limits, timeouts, logging config (NOT Minervini-specific)

### `config.example.env`
**Location:** Root directory  
**Contains:** Environment variable template for API keys

---

## 🔧 How to Change Variables

Currently, you need to edit `minervini_scanner.py` directly. For example:

**To change stop loss from 7.5% to 8%:**
- Edit line 872 in `minervini_scanner.py`:
  ```python
  stop_loss_pct = 8.0  # Changed from 7.5
  ```

**To change SMA periods:**
- Edit lines 147-149 in `minervini_scanner.py`:
  ```python
  sma_50 = hist['Close'].rolling(window=50).mean()  # Change 50
  sma_150 = hist['Close'].rolling(window=150).mean()  # Change 150
  sma_200 = hist['Close'].rolling(window=200).mean()  # Change 200
  ```

**To change volume expansion threshold:**
- Edit line 751 in `minervini_scanner.py`:
  ```python
  if volume_ratio < 1.2:  # Change 1.2 to desired value
  ```

---

## 💡 Future Improvement: Configuration File

**Recommended:** Create a `minervini_config.py` file to centralize all these values:

```python
# minervini_config.py
TREND_STRUCTURE = {
    "SMA_PERIODS": [50, 150, 200],
    "PRICE_FROM_52W_LOW_MIN_PCT": 30,
    "PRICE_FROM_52W_HIGH_MAX_PCT": 15,
    "PRICE_TOO_CLOSE_TO_HIGH_PCT": 10,
}

BASE_QUALITY = {
    "LENGTH_MIN_WEEKS": 3,
    "LENGTH_MAX_WEEKS": 8,
    "DEPTH_MAX_PCT": 25,
    "CLOSE_POSITION_MIN_PCT": 50,
    "VOLUME_CONTRACTION_WARNING": 0.95,
}

BUY_SELL = {
    "STOP_LOSS_PCT": 7.5,
    "PROFIT_TARGET_1_PCT": 22.5,
    "PROFIT_TARGET_2_PCT": 45.0,
}
```

This would make it easier to adjust parameters without editing the main scanner code.

---

## 📝 Quick Reference by Category

### Moving Averages
- **File:** `minervini_scanner.py`
- **Lines:** 147-149, 182-193
- **Values:** 50, 150, 200 days

### Base Identification
- **File:** `minervini_scanner.py`
- **Lines:** 331-445
- **Key Values:** 0.85 volatility threshold, 55% low-vol days, 3-8 weeks length

### Volume Criteria
- **File:** `minervini_scanner.py`
- **Lines:** 562-666, 668-771
- **Key Values:** 1.2x expansion (breakout), 0.9x contraction (base), 1.5x heavy sell

### Entry/Exit Prices
- **File:** `minervini_scanner.py`
- **Lines:** 837-920
- **Key Values:** 7.5% stop loss, 22.5% target 1, 45% target 2

### RSI & Relative Strength
- **File:** `minervini_scanner.py`
- **Lines:** 447-549, 551-560
- **Key Values:** RSI period 14, RSI min 60

---

**Last Updated:** 2026-01-09  
**All variables are in:** `minervini_scanner.py`
