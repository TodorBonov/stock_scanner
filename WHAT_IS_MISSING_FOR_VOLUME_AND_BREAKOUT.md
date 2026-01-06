# What's Missing to Evaluate Volume Signature & Breakout Rules

## The Problem

For **IDR.MC**, both **Volume Signature** and **Breakout Rules** cannot be evaluated because the scanner cannot identify a **base pattern** in the stock's price action.

## Why a Base is Required

Both criteria depend on having a **base** (consolidation pattern) identified first:

1. **Volume Signature** needs:
   - Base average volume (to compare against pre-base volume)
   - Base high price (to determine if stock is breaking out)
   - Base period data (to check for dry volume)

2. **Breakout Rules** needs:
   - Base high price (the "pivot point" to break above)
   - Base period data (to understand the consolidation context)

## What Makes a Valid Base Pattern?

The scanner uses **two methods** to identify a base:

### Method 1: Low Volatility Period
A base is identified if:
- **Volatility** < 70% of average volatility (over 10-day rolling window)
- **Duration**: At least **15 trading days** (3 weeks) of low volatility
- **Length**: Between **2-12 weeks** (10-60 trading days)
- **Depth**: ≤ **35%** (price range from base high to base low)

### Method 2: Price Range Consolidation
A base is identified if:
- **30-day price range** ≤ **15%** of average price, OR
- **60-day price range** ≤ **25%** of average price
- **Length**: Between **2-12 weeks**
- **Depth**: ≤ **35%**

## Why IDR.MC Doesn't Have a Base

Based on the scan results, IDR.MC likely fails base identification because:

1. **Still in strong uptrend** - The stock is only 3.2% from its 52-week high, suggesting it's still advancing rather than consolidating
2. **Price range too wide** - The recent price action may have a range >15% (30 days) or >25% (60 days)
3. **Volatility too high** - The stock's volatility may be >70% of average, indicating choppy/trending action rather than consolidation
4. **No clear sideways movement** - The price may still be trending up without a clear pause/consolidation period

## What This Means

**IDR.MC is in a strong uptrend but hasn't formed a proper consolidation base yet.**

This is actually a **good problem** - it means the stock is still advancing. However, according to Minervini's methodology:

- You need a **base** (3-8 weeks of consolidation) before a proper breakout
- Without a base, you can't evaluate:
  - Whether volume is contracting (dry volume)
  - Whether there's a proper breakout with volume expansion
  - Whether the breakout clears the pivot decisively

## What to Watch For

For IDR.MC to become fully evaluable, you need to wait for:

1. **Price consolidation** - Stock needs to move sideways for 3-8 weeks
2. **Tight price range** - The consolidation should be ≤25% deep (ideally ≤15%)
3. **Lower volatility** - Volatility should drop below 70% of average during consolidation
4. **Volume contraction** - Volume should dry up during the base (fall below 90% of pre-base volume)

Once these conditions are met, the scanner will be able to:
- Evaluate Volume Signature (dry volume in base, breakout volume)
- Evaluate Breakout Rules (pivot clearance, close position, volume expansion)

## Current Status Summary

✅ **Trend & Structure**: PASS - Stock is in strong uptrend  
❌ **Base Quality**: FAIL - No base pattern identified  
❌ **Relative Strength**: FAIL - RSI too low (50.9, needs >60)  
❌ **Volume Signature**: CANNOT EVALUATE - Requires base  
❌ **Breakout Rules**: CANNOT EVALUATE - Requires base  

**Grade: B** (partial pass on critical trend criteria, but missing base formation)

