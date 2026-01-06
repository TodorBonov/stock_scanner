# Base Identification - Alternative Approaches & Options

## Current Implementation Issues

**Current Method 1 Requirements:**
- Volatility < **70%** of average volatility
- At least **15 consecutive days** of low volatility
- Base length: 2-12 weeks
- Base depth: ≤ 35%

**Problems:**
- Too strict - misses many valid bases
- Requires consecutive days (not allowing for minor volatility spikes)
- Single threshold (70%) may not work for all market conditions

---

## Alternative Approaches

### Option 1: Relaxed Volatility Thresholds (Easiest)

**Change the 70% threshold to be more flexible:**

```python
# Current (too strict):
low_vol_periods = data[data['volatility'] < avg_volatility * 0.7]

# Option 1A: More lenient (80%)
low_vol_periods = data[data['volatility'] < avg_volatility * 0.8]

# Option 1B: Adaptive threshold (based on market conditions)
# Use 75% in normal markets, 85% in volatile markets
market_volatility = data['volatility'].tail(60).mean()
if market_volatility > data['volatility'].mean() * 1.2:
    threshold = 0.85  # More lenient in volatile markets
else:
    threshold = 0.75  # Normal threshold
low_vol_periods = data[data['volatility'] < avg_volatility * threshold]

# Option 1C: Multiple thresholds (tiered approach)
# Try 70% first, if no base found, try 80%, then 90%
for threshold in [0.7, 0.8, 0.9]:
    low_vol_periods = data[data['volatility'] < avg_volatility * threshold]
    if len(low_vol_periods) >= 10:  # Reduced from 15
        break
```

**Pros:**
- Easy to implement
- Maintains same logic structure
- Can be made configurable

**Cons:**
- Still requires consecutive days
- May catch false positives

---

### Option 2: Non-Consecutive Days (More Flexible)

**Allow gaps in low volatility periods:**

```python
# Current (requires 15 consecutive days):
if len(low_vol_periods) >= 15:
    # Only works if all 15 days are consecutive

# Option 2A: Allow gaps (80% of days must be low vol)
window_days = 20  # Check last 20 days
low_vol_count = len(low_vol_periods.tail(window_days))
if low_vol_count >= window_days * 0.75:  # 75% of days must be low vol
    # Valid base even if not consecutive

# Option 2B: Sliding window approach
# Check multiple windows, not just most recent
for window_start in range(len(data) - 20, len(data) - 10):
    window_data = data.iloc[window_start:window_start + 20]
    low_vol_count = len(window_data[window_data['volatility'] < avg_volatility * 0.75])
    if low_vol_count >= 12:  # 12 out of 20 days
        # Found potential base
        break
```

**Pros:**
- More realistic (allows for minor volatility spikes)
- Catches bases that current method misses
- Better reflects real market behavior

**Cons:**
- More complex logic
- Need to handle edge cases

---

### Option 3: Percentage-Based Approach (Most Flexible)

**Use percentage of low-volatility days instead of consecutive requirement:**

```python
# Option 3A: Simple percentage
lookback_days = 30
recent_data = data.tail(lookback_days)
low_vol_days = recent_data[recent_data['volatility'] < avg_volatility * 0.75]
low_vol_percentage = len(low_vol_days) / len(recent_data)

if low_vol_percentage >= 0.60:  # 60% of days must be low volatility
    # Valid base pattern
    base_data = recent_data
    # Calculate base metrics...

# Option 3B: Weighted percentage (recent days count more)
lookback_days = 30
recent_data = data.tail(lookback_days)
weights = np.linspace(0.5, 1.0, len(recent_data))  # Recent days weighted more
low_vol_mask = recent_data['volatility'] < avg_volatility * 0.75
weighted_score = (low_vol_mask * weights).sum() / weights.sum()

if weighted_score >= 0.65:  # 65% weighted score
    # Valid base
```

**Pros:**
- Most flexible
- Easy to tune (just change percentage threshold)
- Works well for various market conditions

**Cons:**
- May be too lenient if threshold too low
- Need to validate against known good bases

---

### Option 4: Trend-Following-Base Detection (New Method)

**Look for bases that follow an advance (more aligned with Minervini):**

```python
def identify_trend_following_base(data: pd.DataFrame) -> Optional[Dict]:
    """
    Identify base that follows an advance (Minervini pattern)
    """
    # Step 1: Find recent high (20-40 days ago)
    lookback = min(60, len(data))
    recent_data = data.tail(lookback)
    
    # Find highest point in first half of lookback period
    first_half = recent_data.iloc[:lookback//2]
    if len(first_half) < 10:
        return None
    
    recent_high_idx = first_half['High'].idxmax()
    recent_high = first_half['High'].max()
    
    # Step 2: Check if price has consolidated after the high
    second_half = recent_data.loc[recent_high_idx:]
    if len(second_half) < 15:  # Need at least 3 weeks of consolidation
        return None
    
    # Step 3: Check consolidation characteristics
    consolidation_high = second_half['High'].max()
    consolidation_low = second_half['Low'].min()
    consolidation_depth = ((consolidation_high - consolidation_low) / consolidation_high) * 100
    
    # Check if price is consolidating (not trending up)
    price_change = (second_half['Close'].iloc[-1] - second_half['Close'].iloc[0]) / second_half['Close'].iloc[0]
    
    # Valid base if:
    # - Depth ≤ 25%
    # - Price hasn't moved much (consolidation, not trend)
    # - At least 15 days of consolidation
    if (consolidation_depth <= 25 and 
        abs(price_change) < 0.10 and  # Less than 10% net movement
        len(second_half) >= 15):
        
        return {
            "data": second_half,
            "length_weeks": len(second_half) / 5.0,
            "depth_pct": consolidation_depth,
            "start_date": second_half.index[0],
            "end_date": second_half.index[-1],
            "method": "trend_following"
        }
    
    return None
```

**Pros:**
- More aligned with Minervini's methodology
- Catches bases that follow advances
- More realistic pattern recognition

**Cons:**
- More complex
- Requires validation

---

### Option 5: Support/Resistance Based (Technical Analysis)

**Identify bases using support and resistance levels:**

```python
def identify_support_resistance_base(data: pd.DataFrame) -> Optional[Dict]:
    """
    Identify base using support/resistance levels
    """
    lookback = min(60, len(data))
    recent_data = data.tail(lookback)
    
    # Find support and resistance levels
    highs = recent_data['High'].rolling(window=5).max()
    lows = recent_data['Low'].rolling(window=5).min()
    
    # Identify consolidation zone (price bouncing between levels)
    price_range = recent_data['High'].max() - recent_data['Low'].min()
    avg_price = recent_data['Close'].mean()
    range_pct = (price_range / avg_price) * 100
    
    # Check if price is consolidating (multiple touches of support/resistance)
    # Count how many times price touched within 2% of high/low
    high_touches = 0
    low_touches = 0
    high_level = recent_data['High'].max()
    low_level = recent_data['Low'].min()
    
    for idx, row in recent_data.iterrows():
        if abs(row['High'] - high_level) / high_level < 0.02:
            high_touches += 1
        if abs(row['Low'] - low_level) / low_level < 0.02:
            low_touches += 1
    
    # Valid base if:
    # - Range is tight (≤ 25%)
    # - Multiple touches of support/resistance (shows consolidation)
    # - At least 15 days
    if (range_pct <= 25 and 
        (high_touches >= 2 or low_touches >= 2) and
        len(recent_data) >= 15):
        
        return {
            "data": recent_data,
            "length_weeks": len(recent_data) / 5.0,
            "depth_pct": range_pct,
            "start_date": recent_data.index[0],
            "end_date": recent_data.index[-1],
            "method": "support_resistance"
        }
    
    return None
```

**Pros:**
- Uses technical analysis principles
- Catches consolidation patterns
- More intuitive

**Cons:**
- More complex calculations
- May need tuning

---

### Option 6: Volume-Weighted Approach

**Use volume patterns to identify bases (low volume = consolidation):**

```python
def identify_volume_based_base(data: pd.DataFrame) -> Optional[Dict]:
    """
    Identify base using volume patterns (dry volume = consolidation)
    """
    lookback = min(60, len(data))
    recent_data = data.tail(lookback)
    
    # Calculate volume metrics
    avg_volume = recent_data['Volume'].mean()
    pre_base_volume = data.iloc[-(lookback + 20):-lookback]['Volume'].mean()
    
    # Check for volume contraction
    volume_contraction = avg_volume / pre_base_volume if pre_base_volume > 0 else 1.0
    
    # Check price range
    price_range = ((recent_data['High'].max() - recent_data['Low'].min()) / 
                   recent_data['Close'].mean()) * 100
    
    # Valid base if:
    # - Volume contracts (dry volume)
    # - Price range is tight
    # - At least 15 days
    if (volume_contraction < 0.9 and  # Volume contracts
        price_range <= 25 and  # Tight range
        len(recent_data) >= 15):
        
        return {
            "data": recent_data,
            "length_weeks": len(recent_data) / 5.0,
            "depth_pct": price_range,
            "start_date": recent_data.index[0],
            "end_date": recent_data.index[-1],
            "method": "volume_based"
        }
    
    return None
```

**Pros:**
- Uses Minervini's volume principles
- Volume contraction is a key indicator
- Simple to implement

**Cons:**
- May miss bases with normal volume
- Requires good volume data

---

### Option 7: Hybrid Multi-Method Approach (Recommended)

**Combine multiple methods with scoring:**

```python
def identify_base_hybrid(data: pd.DataFrame) -> Optional[Dict]:
    """
    Use multiple methods and score them
    """
    methods = []
    scores = []
    
    # Method 1: Volatility-based (relaxed)
    vol_base = identify_base_volatility(data, threshold=0.75, min_days=10)
    if vol_base:
        methods.append(vol_base)
        scores.append(0.8)  # Weight: 0.8
    
    # Method 2: Range-based (current Method 2)
    range_base = identify_base_range(data)
    if range_base:
        methods.append(range_base)
        scores.append(0.7)  # Weight: 0.7
    
    # Method 3: Trend-following
    trend_base = identify_trend_following_base(data)
    if trend_base:
        methods.append(trend_base)
        scores.append(0.9)  # Weight: 0.9 (most aligned with Minervini)
    
    # Method 4: Volume-based
    volume_base = identify_volume_based_base(data)
    if volume_base:
        methods.append(volume_base)
        scores.append(0.85)  # Weight: 0.85
    
    # If multiple methods agree, use the one with highest score
    if methods:
        best_idx = scores.index(max(scores))
        return methods[best_idx]
    
    return None
```

**Pros:**
- Most robust approach
- Catches bases that single method might miss
- Can weight methods by reliability

**Cons:**
- Most complex
- Requires tuning weights
- Slower (but can be optimized)

---

## Recommended Implementation Strategy

### Phase 1: Quick Wins (Immediate)
1. **Relax volatility threshold** from 70% to 75-80%
2. **Reduce consecutive days** from 15 to 10-12
3. **Add percentage-based check** as fallback

### Phase 2: Enhanced Detection (Short-term)
4. **Add trend-following-base detection** (Option 4)
5. **Add volume-based detection** (Option 6)
6. **Combine methods** with scoring (Option 7)

### Phase 3: Advanced Features (Long-term)
7. **Add support/resistance detection** (Option 5)
8. **Add adaptive thresholds** based on market conditions
9. **Add diagnostic output** showing which method found the base

---

## Configuration Options

Create a configurable system:

```python
# config.py or minervini_config.py
BASE_IDENTIFICATION = {
    # Volatility method
    "volatility_threshold": 0.75,  # Changed from 0.7
    "min_consecutive_days": 10,   # Changed from 15
    "min_percentage_days": 0.60,  # 60% of days must be low vol
    
    # Range method
    "range_30d_threshold": 15,    # 30-day range ≤ 15%
    "range_60d_threshold": 25,     # 60-day range ≤ 25%
    
    # Hybrid approach
    "use_hybrid": True,
    "method_weights": {
        "volatility": 0.8,
        "range": 0.7,
        "trend_following": 0.9,
        "volume": 0.85
    },
    
    # Base validation
    "min_length_weeks": 2,
    "max_length_weeks": 12,
    "max_depth_pct": 35
}
```

---

## Testing Recommendations

Before implementing, test each option:

1. **Test on known good bases** - Stocks that clearly have bases
2. **Test on known bad cases** - Stocks that shouldn't have bases
3. **Compare results** - How many more bases are detected?
4. **Check false positives** - Are we catching invalid patterns?
5. **Validate against Minervini's examples** - Use stocks from his books/courses

---

## Quick Implementation Example

Here's a quick implementation of Option 1C (tiered thresholds) + Option 3 (percentage-based):

```python
def _identify_base_improved(self, data: pd.DataFrame) -> Optional[Dict]:
    """
    Improved base identification with multiple thresholds
    """
    try:
        window = 10
        data = data.copy()
        data['volatility'] = data['Close'].pct_change().rolling(window=window).std()
        avg_volatility = data['volatility'].mean()
        
        # Try multiple thresholds (tiered approach)
        for threshold in [0.7, 0.75, 0.8, 0.85]:
            low_vol_periods = data[data['volatility'] < avg_volatility * threshold]
            
            # Option 1: Check consecutive days (original)
            if len(low_vol_periods) >= 15:
                # Found base with consecutive days
                return self._extract_base_data(data, low_vol_periods, threshold)
            
            # Option 2: Check percentage of days (new)
            lookback_days = 30
            recent_data = data.tail(lookback_days)
            recent_low_vol = recent_data[recent_data['volatility'] < avg_volatility * threshold]
            low_vol_percentage = len(recent_low_vol) / len(recent_data)
            
            if low_vol_percentage >= 0.60 and len(recent_data) >= 15:
                # Found base with percentage approach
                return self._extract_base_data(data, recent_data, threshold)
        
        # If no base found, try range-based method (current Method 2)
        return self._identify_base_range(data)
        
    except Exception as e:
        logger.debug(f"Error identifying base: {e}")
        return None
```

---

## Summary

**Best Options for Your Use Case:**

1. **Quick Fix:** Relax threshold to 75-80%, reduce days to 10-12
2. **Better Fix:** Add percentage-based approach (60% of days)
3. **Best Fix:** Implement hybrid approach with multiple methods

**Recommended Starting Point:**
- Change threshold: 0.7 → 0.75
- Change min days: 15 → 10 (consecutive) OR 60% of 20 days
- Add trend-following-base detection
- Add diagnostic output to see which method found the base

This will significantly increase base detection rate while maintaining quality.

