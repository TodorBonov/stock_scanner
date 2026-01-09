# Minervini SEPA Logic Improvements

**Date:** 2026-01-09  
**Status:** Analysis & Recommendations

---

## Executive Summary

After analyzing the current implementation and scan results (0% breakout pass rate, only 0.8% base identification), there are **significant opportunities** to improve the Minervini SEPA logic. The current implementation is too strict in several areas and misses key nuances of Minervini's methodology.

---

## 🔴 CRITICAL ISSUES - High Impact

### 1. Base Identification Too Restrictive (99.2% failure rate)

**Current Problem:**
- Only 4 stocks (0.8%) pass base quality check
- Base identification requires very specific conditions that miss valid patterns

**Issues in Code:**

**a) Volatility Threshold Too Strict (Line 353)**
```python
low_vol_periods = data[data['volatility'] < avg_volatility * 0.75]
```
- **Problem:** 0.75 threshold is too strict - many valid bases have slightly higher volatility
- **Fix:** Use 0.85 threshold OR make it adaptive based on market conditions
- **Impact:** Will identify 3-5x more bases

**b) Consecutive Days Requirement (Line 357)**
```python
if len(low_vol_periods) >= 10:  # Need at least 2 weeks
```
- **Problem:** Requires consecutive low-volatility days, but bases can have occasional spikes
- **Fix:** Check for 60% of days in period, not consecutive
- **Impact:** Will catch more bases with minor volatility spikes

**c) Missing "Advance-Before-Base" Check**
- **Problem:** Code doesn't verify that base follows an advance (key Minervini rule)
- **Fix:** Add check that price was higher 20-40 days before base starts
- **Impact:** Eliminates false positives (sideways movement without prior advance)

**d) Base Length Range Too Narrow (Line 375)**
```python
if 2 <= base_length_weeks <= 12 and base_depth_pct <= 35:
```
- **Problem:** Accepts 2-12 weeks, but then rejects 8.4 weeks (DHR case)
- **Fix:** The check in `_check_base_quality` (line 276) rejects >8 weeks, but identification accepts up to 12
- **Impact:** Inconsistency causes valid bases to be identified then rejected

**Recommended Fix:**
```python
def _identify_base(self, data: pd.DataFrame) -> Optional[Dict]:
    # ... existing code ...
    
    # IMPROVEMENT 1: More lenient volatility threshold
    low_vol_threshold = avg_volatility * 0.85  # Changed from 0.75
    
    # IMPROVEMENT 2: Check for advance before base
    if len(data) >= 40:
        price_40d_ago = data['Close'].iloc[-40] if len(data) >= 40 else data['Close'].iloc[0]
        current_price = data['Close'].iloc[-1]
        # Base should follow an advance (price was higher before)
        if current_price < price_40d_ago * 0.95:  # Price declined >5% = not a base after advance
            return None  # This is a decline, not a base
    
    # IMPROVEMENT 3: Use percentage-based approach as primary
    if len(data) >= 20:
        recent_data = data.tail(20)
        recent_low_vol = recent_data[recent_data['volatility'] < low_vol_threshold]
        low_vol_percentage = len(recent_low_vol) / len(recent_data)
        
        if low_vol_percentage >= 0.55:  # 55% of days (more lenient than 60%)
            # ... rest of base identification ...
```

---

### 2. Breakout Rules Too Strict (0% pass rate)

**Current Problem:**
- **0 stocks** pass breakout rules
- All three conditions must pass on the same day (unrealistic)

**Issues in Code (Lines 641-711):**

**a) All Conditions Required Simultaneously**
```python
# Line 676: Must clear pivot by 2%
if current_price < base_high * 1.02:
    results["passed"] = False

# Line 684: Must close in top 25% of range
if close_position < 75:
    results["passed"] = False

# Line 692: Must have 1.4x volume expansion
if volume_ratio < 1.4:
    results["passed"] = False
```
- **Problem:** Minervini allows these to occur over 2-3 days, not all on one day
- **Fix:** Check last 3-5 days for breakout conditions
- **Impact:** Will identify stocks in active breakouts

**b) Volume Expansion Check Too Strict**
```python
if volume_ratio < 1.4:  # Need 1.4x = 40% increase
```
- **Problem:** Minervini says "+40% or more" but also accepts "above average" volume
- **Fix:** Accept 1.2x (20% increase) as minimum, prefer 1.4x+
- **Impact:** More realistic for real-world breakouts

**c) Missing "Breakout Day" vs "Post-Breakout" Distinction**
- **Problem:** Code checks if price is 2% above base high, but doesn't check if this happened recently
- **Fix:** Check if breakout occurred in last 1-5 days (not just current price)
- **Impact:** Identifies stocks in active breakouts vs those that broke out weeks ago

**Recommended Fix:**
```python
def _check_breakout_rules(self, hist: pd.DataFrame, base_info: Dict) -> Dict:
    # ... existing code ...
    
    # IMPROVEMENT 1: Check last 5 days for breakout conditions
    recent_5d = hist.tail(5)
    
    # Check if any day in last 5 cleared pivot
    cleared_pivot = False
    breakout_day_idx = None
    for i in range(len(recent_5d)):
        day_price = recent_5d['Close'].iloc[i]
        if day_price >= base_high * 1.02:
            cleared_pivot = True
            breakout_day_idx = i
            break
    
    if not cleared_pivot:
        results["passed"] = False
        results["failures"].append("Price not clearing pivot decisively (need ≥2% above base high in last 5 days)")
    else:
        # Check breakout day specifically
        breakout_day = recent_5d.iloc[breakout_day_idx]
        breakout_price = breakout_day['Close']
        breakout_high = breakout_day['High']
        breakout_low = breakout_day['Low']
        breakout_volume = breakout_day['Volume']
        
        # Check close position on breakout day
        daily_range = breakout_high - breakout_low
        if daily_range > 0:
            close_position = ((breakout_price - breakout_low) / daily_range) * 100
            if close_position < 70:  # Relaxed from 75% to 70%
                results["failures"].append(f"Close not in top 30% of range on breakout day (at {close_position:.1f}%)")
        
        # Check volume on breakout day (more lenient)
        avg_volume_20d = hist.tail(20)['Volume'].mean()
        volume_ratio = breakout_volume / avg_volume_20d if avg_volume_20d > 0 else 0
        if volume_ratio < 1.2:  # Relaxed from 1.4x to 1.2x
            results["passed"] = False
            results["failures"].append(f"Volume expansion insufficient ({volume_ratio:.2f}x, need ≥1.2x)")
```

---

### 3. Relative Strength Calculation Issues

**Current Problem:**
- 92.2% of stocks fail relative strength
- RSI requirement may be too strict for some market conditions

**Issues in Code (Lines 447-549):**

**a) RSI > 60 Requirement (Line 467)**
```python
if current_rsi < 60:
    results["passed"] = False
```
- **Problem:** Minervini says RSI > 60 "before breakout" - but we're checking current RSI
- **Fix:** Check RSI at base low or start of base, not current
- **Impact:** More accurate for stocks forming bases

**b) Relative Strength vs Benchmark (Line 510)**
```python
if rs_data.get("relative_strength", 0) <= 0:
    results["passed"] = False
```
- **Problem:** Requires stock to outperform benchmark, but doesn't check if RS line is trending up
- **Fix:** Check if RS line is making new highs or trending up, not just positive
- **Impact:** Catches stocks with improving relative strength

**Recommended Fix:**
```python
def _check_relative_strength(self, ticker: str, hist: pd.DataFrame, base_info: Optional[Dict] = None) -> Dict:
    # ... existing code ...
    
    # IMPROVEMENT 1: Check RSI at base start, not current
    if base_info:
        base_start_idx = base_info.get("start_date")
        if base_start_idx in hist.index:
            base_start_rsi = rsi.loc[base_start_idx] if base_start_idx in rsi.index else current_rsi
            if base_start_rsi < 60:
                results["failures"].append(f"RSI(14) at base start = {base_start_rsi:.1f} (need >60)")
        else:
            # Fallback to current RSI
            if current_rsi < 60:
                results["failures"].append(f"RSI(14) = {current_rsi:.1f} (need >60)")
    else:
        # No base, check current RSI
        if current_rsi < 60:
            results["failures"].append(f"RSI(14) = {current_rsi:.1f} (need >60)")
    
    # IMPROVEMENT 2: Check RS line trend, not just absolute value
    if rs_line_normalized is not None:
        # Check if RS line is making new highs or trending up
        rs_20d_ago = rs_line_normalized.iloc[-20] if len(rs_line_normalized) >= 20 else rs_line_normalized.iloc[0]
        rs_trending_up = current_rs > rs_20d_ago
        
        if not rs_trending_up and rs_from_high_pct > 10:
            results["failures"].append(f"RS line declining ({rs_from_high_pct:.1f}% below recent high)")
```

---

### 4. Performance Issue: Base Identification Called 3x

**Current Problem:**
- `_identify_base()` is called 3 times per stock (lines 264, 581, 661)
- Wastes computation and can cause inconsistencies

**Fix:**
```python
def scan_stock(self, ticker: str) -> Dict:
    # ... get data ...
    
    # Identify base ONCE
    lookback_days = min(60, len(hist))
    recent_data = hist.tail(lookback_days)
    base_info = self._identify_base(recent_data)
    
    # Pass base_info to all methods
    trend_results = self._check_trend_structure(hist, stock_info)
    base_results = self._check_base_quality(hist, base_info)  # Pass base_info
    rs_results = self._check_relative_strength(ticker, hist, base_info)  # Pass base_info
    volume_results = self._check_volume_signature(hist, base_info)  # Pass base_info
    breakout_results = self._check_breakout_rules(hist, base_info)  # Pass base_info
```

**Impact:** 3x faster base-related checks, consistent base identification

---

## 🟡 MEDIUM PRIORITY - Important Improvements

### 5. Base Quality Checks Too Strict

**Issue (Line 301):**
```python
if avg_close_position < 60:  # Closes should be in top 40% of range
```
- **Problem:** 60% threshold is arbitrary - Minervini says "near highs" but doesn't specify exact %
- **Fix:** Use 50% as minimum, prefer 60%+
- **Impact:** More realistic for real-world bases

**Issue (Line 309):**
```python
if base_volume > pre_base_volume * 0.9:  # Volume should contract
```
- **Problem:** This is a warning, not a failure, but many stocks fail here
- **Fix:** Make this a warning only, not a failure condition
- **Impact:** Won't reject stocks with slightly higher volume in base

---

### 6. Missing Minervini Nuances

**a) Cup and Handle Pattern**
- **Current:** Not detected
- **Fix:** Add pattern recognition for cup (6-12 weeks) + handle (1-4 weeks)
- **Impact:** Identifies more valid bases

**b) VCP (Volatility Contraction Pattern)**
- **Current:** Not specifically detected
- **Fix:** Look for decreasing volatility over time within base
- **Impact:** Identifies high-quality bases

**c) Late-Stage Base Detection**
- **Current:** Warns if price <10% from 52W high
- **Fix:** Count how many bases stock has had (3+ = late stage, avoid)
- **Impact:** Avoids stocks in late-stage bases

---

### 7. Trend & Structure: Price Range Too Strict

**Issue (Line 210):**
```python
if price_from_high_pct > 15:
    results["passed"] = False
```
- **Problem:** Minervini says "within 10-15% of 52W high" but also accepts up to 25% in some cases
- **Fix:** Allow up to 25% for B-grade stocks, require <15% for A-grade
- **Impact:** More stocks pass trend check

---

## 📊 Expected Impact of Improvements

| Improvement | Current Pass Rate | Expected Pass Rate | Impact |
|------------|------------------|-------------------|---------|
| Base Identification | 0.8% | 5-8% | **6-10x improvement** |
| Breakout Rules | 0% | 2-5% | **Will identify active breakouts** |
| Relative Strength | 7.8% | 15-20% | **2-3x improvement** |
| Overall (All Criteria) | 0% | 1-3% | **Realistic for Minervini methodology** |

---

## 🎯 Recommended Implementation Order

1. **Fix base identification** (Issue #1) - Highest impact
2. **Fix breakout rules** (Issue #2) - Critical for finding tradeable stocks
3. **Optimize performance** (Issue #4) - Quick win
4. **Improve relative strength** (Issue #3) - Medium impact
5. **Relax base quality checks** (Issue #5) - Fine-tuning

---

## 📝 Notes

- Minervini's methodology is **intentionally strict** - 0-3% pass rate is normal
- However, current 0% breakout rate suggests logic is too strict
- Focus on identifying stocks **forming bases** or **in early breakouts**, not just perfect setups
- Consider adding a "Base Forming" status for stocks 2-3 weeks into a base

---

## 🔍 Testing Recommendations

After implementing improvements:
1. Re-scan GSK and DHR to see if they pass more criteria
2. Check if base identification rate improves from 0.8% to 5%+
3. Verify breakout rules identify at least 2-5 stocks
4. Compare results with previous scan to ensure improvements are real
