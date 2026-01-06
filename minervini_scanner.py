"""
Minervini SEPA (Stock Exchange Price Action) Scanner
Implements Mark Minervini's exact screening criteria for European stocks
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from data_provider import StockDataProvider
from logger_config import get_logger

logger = get_logger(__name__)


class MinerviniScanner:
    """
    Scans stocks according to Mark Minervini's SEPA methodology
    Implements the complete checklist: Trend, Base Quality, Relative Strength, Volume, Breakout
    """
    
    def __init__(self, data_provider: StockDataProvider, benchmark: str = "^GDAXI"):
        """
        Initialize Minervini scanner
        
        Args:
            data_provider: StockDataProvider instance for fetching data
            benchmark: Benchmark index for relative strength (default: DAX for European stocks)
                       Options: ^GDAXI (DAX), ^FCHI (CAC 40), ^AEX (AEX), ^SSMI (Swiss), ^OMX (Nordics)
        """
        self.data_provider = data_provider
        self.benchmark = benchmark
        
    def scan_stock(self, ticker: str) -> Dict:
        """
        Scan a single stock against all Minervini SEPA criteria
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with complete scan results including:
            - overall_grade: "A+", "A", "B", "C", or "F"
            - meets_criteria: Boolean
            - checklist: Detailed pass/fail for each criterion
            - position_size: "Full", "Half", or "None"
            - detailed_analysis: All calculated metrics
        """
        try:
            logger.info(f"Scanning {ticker} for Minervini SEPA criteria...")
            
            # Get historical data (need at least 1 year for 52-week calculations)
            hist = self.data_provider.get_historical_data(ticker, period="1y", interval="1d")
            if hist.empty or len(hist) < 200:
                return {
                    "ticker": ticker,
                    "error": "Insufficient historical data",
                    "meets_criteria": False,
                    "overall_grade": "F"
                }
            
            # Get stock info for fundamentals
            stock_info = self.data_provider.get_stock_info(ticker)
            
            # PART 1: Trend & Structure (NON-NEGOTIABLE)
            trend_results = self._check_trend_structure(hist, stock_info)
            
            # PART 2: Base Quality
            base_results = self._check_base_quality(hist)
            
            # PART 3: Relative Strength
            rs_results = self._check_relative_strength(ticker, hist)
            
            # PART 4: Volume Signature
            volume_results = self._check_volume_signature(hist)
            
            # PART 5: Breakout Day Rules
            breakout_results = self._check_breakout_rules(hist)
            
            # Combine all results
            checklist = {
                "trend_structure": trend_results,
                "base_quality": base_results,
                "relative_strength": rs_results,
                "volume_signature": volume_results,
                "breakout_rules": breakout_results
            }
            
            # Calculate overall grade
            grade_result = self._calculate_grade(checklist)
            
            return {
                "ticker": ticker,
                "overall_grade": grade_result["grade"],
                "meets_criteria": grade_result["meets_criteria"],
                "position_size": grade_result["position_size"],
                "checklist": checklist,
                "detailed_analysis": {
                    "current_price": float(hist['Close'].iloc[-1]),
                    "52_week_high": float(hist['High'].tail(252).max()) if len(hist) >= 252 else float(hist['High'].max()),
                    "52_week_low": float(hist['Low'].tail(252).min()) if len(hist) >= 252 else float(hist['Low'].min()),
                    "price_from_52w_high_pct": grade_result.get("price_from_52w_high_pct", 0),
                    "price_from_52w_low_pct": grade_result.get("price_from_52w_low_pct", 0),
                },
                "stock_info": stock_info
            }
            
        except Exception as e:
            logger.error(f"Error scanning {ticker}: {e}", exc_info=True)
            return {
                "ticker": ticker,
                "error": str(e),
                "meets_criteria": False,
                "overall_grade": "F"
            }
    
    def _check_trend_structure(self, hist: pd.DataFrame, stock_info: Dict) -> Dict:
        """
        PART 1: Trend & Structure (NON-NEGOTIABLE)
        
        Checks:
        - Price above 50, 150, 200 SMA
        - 50 SMA > 150 SMA > 200 SMA
        - All three SMAs sloping UP
        - Price ≥ 30% above 52-week low
        - Price within 10–15% of 52-week high
        """
        results = {
            "passed": True,
            "failures": [],
            "details": {}
        }
        
        try:
            current_price = hist['Close'].iloc[-1]
            
            # Calculate SMAs
            sma_50 = hist['Close'].rolling(window=50).mean()
            sma_150 = hist['Close'].rolling(window=150).mean()
            sma_200 = hist['Close'].rolling(window=200).mean()
            
            # Check if we have enough data
            if len(hist) < 200:
                results["passed"] = False
                results["failures"].append("Insufficient data for 200 SMA")
                return results
            
            current_sma_50 = sma_50.iloc[-1]
            current_sma_150 = sma_150.iloc[-1]
            current_sma_200 = sma_200.iloc[-1]
            
            # Check price above SMAs
            above_50 = current_price > current_sma_50
            above_150 = current_price > current_sma_150
            above_200 = current_price > current_sma_200
            
            if not (above_50 and above_150 and above_200):
                results["passed"] = False
                if not above_50:
                    results["failures"].append("Price below 50 SMA")
                if not above_150:
                    results["failures"].append("Price below 150 SMA")
                if not above_200:
                    results["failures"].append("Price below 200 SMA")
            
            # Check SMA order: 50 > 150 > 200
            sma_order_correct = (current_sma_50 > current_sma_150 > current_sma_200)
            if not sma_order_correct:
                results["passed"] = False
                results["failures"].append("SMA order incorrect (50 SMA must be > 150 SMA > 200 SMA)")
            
            # Check SMAs sloping UP (compare current to 20 days ago)
            if len(hist) >= 220:
                sma_50_slope = current_sma_50 > sma_50.iloc[-20]
                sma_150_slope = current_sma_150 > sma_150.iloc[-20]
                sma_200_slope = current_sma_200 > sma_200.iloc[-20]
                
                if not (sma_50_slope and sma_150_slope and sma_200_slope):
                    results["passed"] = False
                    if not sma_50_slope:
                        results["failures"].append("50 SMA not sloping up")
                    if not sma_150_slope:
                        results["failures"].append("150 SMA not sloping up")
                    if not sma_200_slope:
                        results["failures"].append("200 SMA not sloping up")
            else:
                # Use shorter period if needed
                if len(hist) >= 70:
                    sma_50_slope = current_sma_50 > sma_50.iloc[-10]
                    if not sma_50_slope:
                        results["passed"] = False
                        results["failures"].append("50 SMA not sloping up")
            
            # Calculate 52-week high/low
            if len(hist) >= 252:
                year_data = hist.tail(252)
            else:
                year_data = hist
            
            week_52_high = year_data['High'].max()
            week_52_low = year_data['Low'].min()
            
            # Check price ≥ 30% above 52-week low
            price_from_low_pct = ((current_price - week_52_low) / week_52_low) * 100
            if price_from_low_pct < 30:
                results["passed"] = False
                results["failures"].append(f"Price only {price_from_low_pct:.1f}% above 52W low (need ≥30%)")
            
            # Check price within 10–15% of 52-week high
            price_from_high_pct = ((week_52_high - current_price) / week_52_high) * 100
            if price_from_high_pct > 15:
                results["passed"] = False
                results["failures"].append(f"Price {price_from_high_pct:.1f}% below 52W high (need within 15%)")
            elif price_from_high_pct < 10:
                # Too close to high might indicate late stage
                results["failures"].append(f"Price very close to 52W high ({price_from_high_pct:.1f}%) - may be late stage")
            
            # Store details
            results["details"] = {
                "current_price": float(current_price),
                "sma_50": float(current_sma_50),
                "sma_150": float(current_sma_150),
                "sma_200": float(current_sma_200),
                "above_50": above_50,
                "above_150": above_150,
                "above_200": above_200,
                "sma_order_correct": sma_order_correct,
                "52_week_high": float(week_52_high),
                "52_week_low": float(week_52_low),
                "price_from_52w_low_pct": float(price_from_low_pct),
                "price_from_52w_high_pct": float(price_from_high_pct)
            }
            
        except Exception as e:
            logger.error(f"Error checking trend structure: {e}", exc_info=True)
            results["passed"] = False
            results["failures"].append(f"Error: {str(e)}")
        
        return results
    
    def _check_base_quality(self, hist: pd.DataFrame) -> Dict:
        """
        PART 2: Base Quality
        
        Checks:
        - Base length 3–8 weeks (daily chart)
        - Depth ≤ 20–25% (≤15% is elite)
        - No wide, sloppy candles
        - Tight closes near highs
        - Volume contracts inside base
        """
        results = {
            "passed": True,
            "failures": [],
            "details": {}
        }
        
        try:
            # Look for base in last 60 days (about 12 weeks)
            lookback_days = min(60, len(hist))
            recent_data = hist.tail(lookback_days)
            
            # Find the most recent base (consolidation period)
            # A base is characterized by sideways movement after an advance
            base_info = self._identify_base(recent_data)
            
            if not base_info:
                results["passed"] = False
                results["failures"].append("No clear base pattern identified")
                return results
            
            base_length_weeks = base_info["length_weeks"]
            base_depth_pct = base_info["depth_pct"]
            base_data = base_info["data"]
            
            # Check base length: 3-8 weeks
            if base_length_weeks < 3 or base_length_weeks > 8:
                results["passed"] = False
                results["failures"].append(f"Base length {base_length_weeks:.1f} weeks (need 3-8 weeks)")
            
            # Check base depth: ≤ 20-25% (≤15% is elite)
            if base_depth_pct > 25:
                results["passed"] = False
                results["failures"].append(f"Base depth {base_depth_pct:.1f}% (need ≤25%, ≤15% is elite)")
            elif base_depth_pct > 20:
                results["failures"].append(f"Base depth {base_depth_pct:.1f}% (acceptable but >20%)")
            
            # Check for wide, sloppy candles (high volatility)
            base_volatility = base_data['Close'].pct_change().std()
            avg_volatility = hist['Close'].pct_change().tail(252).std()
            
            if base_volatility > avg_volatility * 1.5:
                results["passed"] = False
                results["failures"].append("Base shows high volatility (wide, sloppy candles)")
            
            # Check for tight closes near highs
            # Calculate average close position in daily range
            base_data['range_pct'] = ((base_data['Close'] - base_data['Low']) / 
                                      (base_data['High'] - base_data['Low'])) * 100
            avg_close_position = base_data['range_pct'].mean()
            
            if avg_close_position < 60:  # Closes should be in top 40% of range
                results["passed"] = False
                results["failures"].append(f"Closes not near highs (avg {avg_close_position:.1f}% of range)")
            
            # Check volume contracts inside base
            base_volume = base_data['Volume'].mean()
            pre_base_volume = hist.iloc[-(lookback_days + 20):-lookback_days]['Volume'].mean()
            
            if base_volume > pre_base_volume * 0.9:  # Volume should contract
                results["failures"].append("Volume not contracting in base (should be <90% of pre-base)")
            
            # Store details
            results["details"] = {
                "base_length_weeks": float(base_length_weeks),
                "base_depth_pct": float(base_depth_pct),
                "base_volatility": float(base_volatility),
                "avg_volatility": float(avg_volatility),
                "avg_close_position_pct": float(avg_close_position),
                "volume_contraction": float(base_volume / pre_base_volume) if pre_base_volume > 0 else 1.0,
                "base_high": float(base_data['High'].max()),
                "base_low": float(base_data['Low'].min())
            }
            
        except Exception as e:
            logger.error(f"Error checking base quality: {e}", exc_info=True)
            results["passed"] = False
            results["failures"].append(f"Error: {str(e)}")
        
        return results
    
    def _identify_base(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Identify the most recent base pattern in the data
        
        A base is a consolidation period (3-8 weeks) where price moves sideways
        after an advance. This is a natural price pattern - you cannot "add" it.
        
        Returns:
            Dictionary with base information or None
        """
        try:
            # Look for consolidation periods (sideways movement)
            # A base typically follows an advance and shows 3-8 weeks of consolidation
            
            # Method 1: Look for low volatility periods (improved method)
            window = 10  # ~2 weeks
            data = data.copy()  # Avoid SettingWithCopyWarning
            data['volatility'] = data['Close'].pct_change().rolling(window=window).std()
            
            # Find periods with low volatility (potential bases)
            # Improved: Use 0.75 threshold instead of 0.7 (more lenient)
            avg_volatility = data['volatility'].mean()
            low_vol_periods = data[data['volatility'] < avg_volatility * 0.75]
            
            # Improved: Check for 10 consecutive days OR 60% of recent days
            # Option 1: Consecutive days (reduced from 15 to 10)
            if len(low_vol_periods) >= 10:  # Need at least 2 weeks of data
                # Get the most recent low volatility period
                base_start_idx = low_vol_periods.index[0]
                base_end_idx = data.index[-1]
                
                # Extend base backwards to find the start of consolidation
                base_data = data.loc[base_start_idx:base_end_idx]
                
                # Calculate base metrics
                base_high = base_data['High'].max()
                base_low = base_data['Low'].min()
                base_depth_pct = ((base_high - base_low) / base_high) * 100
                
                # Calculate length in weeks (assuming ~5 trading days per week)
                base_length_days = len(base_data)
                base_length_weeks = base_length_days / 5.0
                
                # Only return if it looks like a valid base (2-12 weeks, reasonable depth)
                if 2 <= base_length_weeks <= 12 and base_depth_pct <= 35:
                    return {
                        "data": base_data,
                        "length_weeks": base_length_weeks,
                        "depth_pct": base_depth_pct,
                        "start_date": base_start_idx,
                        "end_date": base_end_idx
                    }
            
            # Option 2: Percentage-based approach (fallback if consecutive fails)
            # Check if 60% of recent days are low volatility
            if len(data) >= 20:
                recent_data = data.tail(20)
                recent_low_vol = recent_data[recent_data['volatility'] < avg_volatility * 0.75]
                low_vol_percentage = len(recent_low_vol) / len(recent_data) if len(recent_data) > 0 else 0
                
                if low_vol_percentage >= 0.60 and len(recent_data) >= 15:  # 60% of days, at least 15 days
                    # Use recent data as base
                    base_data = recent_data
                    base_high = base_data['High'].max()
                    base_low = base_data['Low'].min()
                    base_depth_pct = ((base_high - base_low) / base_high) * 100
                    base_length_weeks = len(base_data) / 5.0
                    
                    # Only return if it looks like a valid base
                    if 2 <= base_length_weeks <= 12 and base_depth_pct <= 35:
                        return {
                            "data": base_data,
                            "length_weeks": base_length_weeks,
                            "depth_pct": base_depth_pct,
                            "start_date": base_data.index[0],
                            "end_date": base_data.index[-1]
                        }
            
            # Method 2: Look for recent consolidation using price range
            # Check last 30-60 days for sideways movement
            if len(data) >= 30:
                # Look at last 30-60 days
                recent_30d = data.tail(30)
                recent_60d = data.tail(min(60, len(data)))
                
                # Calculate price range
                range_30d = ((recent_30d['High'].max() - recent_30d['Low'].min()) / 
                            recent_30d['Close'].mean()) * 100
                range_60d = ((recent_60d['High'].max() - recent_60d['Low'].min()) / 
                            recent_60d['Close'].mean()) * 100
                
                # If recent range is relatively small (consolidation), use it as base
                if range_30d <= 15 or (range_60d <= 25 and len(data) >= 40):
                    base_data = recent_30d if range_30d <= 15 else recent_60d
                    base_high = base_data['High'].max()
                    base_low = base_data['Low'].min()
                    base_depth_pct = ((base_high - base_low) / base_high) * 100
                    base_length_weeks = len(base_data) / 5.0
                    
                    # Only return if reasonable
                    if 2 <= base_length_weeks <= 12 and base_depth_pct <= 35:
                        return {
                            "data": base_data,
                            "length_weeks": base_length_weeks,
                            "depth_pct": base_depth_pct,
                            "start_date": base_data.index[0],
                            "end_date": base_data.index[-1]
                        }
            
            # No clear base pattern found
            return None
            
        except Exception as e:
            logger.debug(f"Error identifying base: {e}")
            return None
    
    def _check_relative_strength(self, ticker: str, hist: pd.DataFrame) -> Dict:
        """
        PART 3: Relative Strength (CRITICAL)
        
        Checks:
        - RS line near or at new highs
        - Stock outperforms index (DAX / STOXX / FTSE)
        - RSI(14) > 60 before breakout
        """
        results = {
            "passed": True,
            "failures": [],
            "details": {}
        }
        
        try:
            # Calculate RSI(14)
            rsi = self._calculate_rsi(hist['Close'], period=14)
            current_rsi = rsi.iloc[-1] if not rsi.empty else 0
            
            if current_rsi < 60:
                results["passed"] = False
                results["failures"].append(f"RSI(14) = {current_rsi:.1f} (need >60)")
            
            # Calculate relative strength vs benchmark
            rs_data = self.data_provider.calculate_relative_strength(ticker, self.benchmark, period=252)
            
            if not rs_data or "error" in rs_data:
                # Try to calculate manually
                benchmark_hist = self.data_provider.get_historical_data(self.benchmark, period="1y", interval="1d")
                if not benchmark_hist.empty:
                    # Calculate RS manually
                    stock_returns = hist['Close'].pct_change().dropna()
                    bench_returns = benchmark_hist['Close'].pct_change().dropna()
                    
                    # Align dates
                    common_dates = stock_returns.index.intersection(bench_returns.index)
                    if len(common_dates) >= 60:
                        stock_period = stock_returns.loc[common_dates[-60:]]
                        bench_period = bench_returns.loc[common_dates[-60:]]
                        
                        stock_cumulative = (1 + stock_period).prod() - 1
                        bench_cumulative = (1 + bench_period).prod() - 1
                        
                        relative_strength = stock_cumulative - bench_cumulative
                        rs_rating = min(100, max(0, 50 + (relative_strength * 100)))
                        
                        rs_data = {
                            "relative_strength": float(relative_strength),
                            "rs_rating": float(rs_rating),
                            "stock_return": float(stock_cumulative),
                            "benchmark_return": float(bench_cumulative)
                        }
                    else:
                        results["passed"] = False
                        results["failures"].append("Insufficient data for relative strength calculation")
                        return results
                else:
                    results["passed"] = False
                    results["failures"].append("Cannot fetch benchmark data for relative strength")
                    return results
            
            # Check if stock outperforms benchmark
            if rs_data.get("relative_strength", 0) <= 0:
                results["passed"] = False
                results["failures"].append("Stock not outperforming benchmark")
            
            # Check if RS line is near new highs
            # Calculate RS line (price / benchmark price)
            benchmark_hist = self.data_provider.get_historical_data(self.benchmark, period="1y", interval="1d")
            if not benchmark_hist.empty:
                # Align dates
                common_dates = hist.index.intersection(benchmark_hist.index)
                if len(common_dates) >= 60:
                    aligned_stock = hist.loc[common_dates]['Close']
                    aligned_bench = benchmark_hist.loc[common_dates]['Close']
                    
                    rs_line = aligned_stock / aligned_bench
                    rs_line_normalized = (rs_line / rs_line.iloc[0]) * 100  # Normalize to start at 100
                    
                    current_rs = rs_line_normalized.iloc[-1]
                    rs_high = rs_line_normalized.tail(60).max()
                    rs_from_high_pct = ((rs_high - current_rs) / rs_high) * 100
                    
                    if rs_from_high_pct > 5:  # More than 5% below RS high
                        results["failures"].append(f"RS line {rs_from_high_pct:.1f}% below recent high")
            
            # Store details
            results["details"] = {
                "rsi_14": float(current_rsi),
                "relative_strength": rs_data.get("relative_strength", 0),
                "rs_rating": rs_data.get("rs_rating", 0),
                "stock_return": rs_data.get("stock_return", 0),
                "benchmark_return": rs_data.get("benchmark_return", 0),
                "outperforming": rs_data.get("relative_strength", 0) > 0
            }
            
        except Exception as e:
            logger.error(f"Error checking relative strength: {e}", exc_info=True)
            results["passed"] = False
            results["failures"].append(f"Error: {str(e)}")
        
        return results
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _check_volume_signature(self, hist: pd.DataFrame) -> Dict:
        """
        PART 4: Volume Signature
        
        Checks:
        - Dry volume in base
        - Breakout volume +40% or more
        - No heavy sell volume before breakout
        """
        results = {
            "passed": True,
            "failures": [],
            "details": {}
        }
        
        try:
            # Get base data (reuse from base quality check)
            lookback_days = min(60, len(hist))
            recent_data = hist.tail(lookback_days)
            base_info = self._identify_base(recent_data)
            
            if not base_info:
                results["passed"] = False
                results["failures"].append("Cannot check volume signature without base")
                return results
            
            base_data = base_info["data"]
            
            # Check for dry volume in base
            base_avg_volume = base_data['Volume'].mean()
            pre_base_volume = hist.iloc[-(lookback_days + 20):-lookback_days]['Volume'].mean()
            
            volume_contraction = base_avg_volume / pre_base_volume if pre_base_volume > 0 else 1.0
            
            if volume_contraction > 0.9:
                results["failures"].append(f"Volume not dry in base (contraction: {volume_contraction:.2f}x)")
            
            # Check for breakout volume (last 5 days)
            recent_5_days = hist.tail(5)
            recent_volume = recent_5_days['Volume'].mean()
            
            # Check if we're in a breakout (price breaking above base high)
            base_high = base_data['High'].max()
            current_price = hist['Close'].iloc[-1]
            
            if current_price > base_high * 1.02:  # 2% above base high = breakout
                # Check if volume is +40% above average
                avg_volume_20d = hist.tail(20)['Volume'].mean()
                volume_increase = recent_volume / avg_volume_20d if avg_volume_20d > 0 else 0
                
                if volume_increase < 1.4:
                    results["passed"] = False
                    results["failures"].append(f"Breakout volume only {volume_increase:.2f}x (need ≥1.4x)")
            else:
                # Not in breakout yet, just check for heavy sell volume
                down_days = recent_5_days[recent_5_days['Close'] < recent_5_days['Open']]
                if len(down_days) > 0:
                    down_volume = down_days['Volume'].mean()
                    if down_volume > base_avg_volume * 1.5:
                        results["failures"].append("Heavy sell volume detected before breakout")
            
            # Store details
            results["details"] = {
                "base_avg_volume": float(base_avg_volume),
                "pre_base_volume": float(pre_base_volume),
                "volume_contraction": float(volume_contraction),
                "recent_volume": float(recent_volume),
                "avg_volume_20d": float(hist.tail(20)['Volume'].mean()),
                "volume_increase": float(recent_volume / hist.tail(20)['Volume'].mean()) if hist.tail(20)['Volume'].mean() > 0 else 0,
                "in_breakout": current_price > base_high * 1.02
            }
            
        except Exception as e:
            logger.error(f"Error checking volume signature: {e}", exc_info=True)
            results["passed"] = False
            results["failures"].append(f"Error: {str(e)}")
        
        return results
    
    def _check_breakout_rules(self, hist: pd.DataFrame) -> Dict:
        """
        PART 5: Breakout Day Rules
        
        Checks:
        - Clears pivot decisively
        - Closes in top 25% of range
        - Volume expansion present
        - Market NOT in correction (we'll skip this as it requires market data)
        """
        results = {
            "passed": True,
            "failures": [],
            "details": {}
        }
        
        try:
            # Find pivot point (base high)
            lookback_days = min(60, len(hist))
            recent_data = hist.tail(lookback_days)
            base_info = self._identify_base(recent_data)
            
            if not base_info:
                results["passed"] = False
                results["failures"].append("Cannot check breakout rules without base")
                return results
            
            base_high = base_info["data"]['High'].max()
            current_price = hist['Close'].iloc[-1]
            current_high = hist['High'].iloc[-1]
            current_low = hist['Low'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist.tail(20)['Volume'].mean()
            
            # Check if clearing pivot decisively (at least 2% above base high)
            if current_price < base_high * 1.02:
                results["passed"] = False
                results["failures"].append(f"Price not clearing pivot decisively (need ≥2% above base high)")
            
            # Check if closes in top 25% of range
            daily_range = current_high - current_low
            if daily_range > 0:
                close_position = ((current_price - current_low) / daily_range) * 100
                if close_position < 75:  # Not in top 25%
                    results["passed"] = False
                    results["failures"].append(f"Close not in top 25% of range (at {close_position:.1f}%)")
            else:
                results["failures"].append("Zero daily range (no price movement)")
            
            # Check volume expansion
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            if volume_ratio < 1.4:
                results["passed"] = False
                results["failures"].append(f"Volume expansion insufficient ({volume_ratio:.2f}x, need ≥1.4x)")
            
            # Store details
            results["details"] = {
                "pivot_price": float(base_high),
                "current_price": float(current_price),
                "clears_pivot": current_price >= base_high * 1.02,
                "close_position_pct": float(close_position) if daily_range > 0 else 0,
                "volume_ratio": float(volume_ratio),
                "in_breakout": current_price >= base_high * 1.02
            }
            
        except Exception as e:
            logger.error(f"Error checking breakout rules: {e}", exc_info=True)
            results["passed"] = False
            results["failures"].append(f"Error: {str(e)}")
        
        return results
    
    def _calculate_grade(self, checklist: Dict) -> Dict:
        """
        Calculate overall grade based on checklist
        
        A+ Verdict Rule:
        - All boxes checked → Full position
        - 1–2 minor flaws → Half position
        - More than 2 → WALK AWAY
        """
        # Count failures
        total_failures = 0
        critical_failures = 0
        
        # Trend & Structure is NON-NEGOTIABLE
        if not checklist["trend_structure"]["passed"]:
            critical_failures += len(checklist["trend_structure"]["failures"])
        
        # Count other failures
        for category, result in checklist.items():
            if category != "trend_structure":
                if not result["passed"]:
                    total_failures += len(result["failures"])
        
        # Calculate grade
        if critical_failures > 0:
            grade = "F"
            meets_criteria = False
            position_size = "None"
        elif total_failures == 0:
            grade = "A+"
            meets_criteria = True
            position_size = "Full"
        elif total_failures <= 2:
            grade = "A"
            meets_criteria = True
            position_size = "Half"
        elif total_failures <= 4:
            grade = "B"
            meets_criteria = False
            position_size = "Half"
        else:
            grade = "C"
            meets_criteria = False
            position_size = "None"
        
        # Calculate price metrics for detailed analysis
        price_from_52w_high_pct = 0
        price_from_52w_low_pct = 0
        
        if "trend_structure" in checklist and "details" in checklist["trend_structure"]:
            details = checklist["trend_structure"]["details"]
            price_from_52w_high_pct = details.get("price_from_52w_high_pct", 0)
            price_from_52w_low_pct = details.get("price_from_52w_low_pct", 0)
        
        return {
            "grade": grade,
            "meets_criteria": meets_criteria,
            "position_size": position_size,
            "total_failures": total_failures + critical_failures,
            "critical_failures": critical_failures,
            "price_from_52w_high_pct": price_from_52w_high_pct,
            "price_from_52w_low_pct": price_from_52w_low_pct
        }
    
    def scan_multiple(self, tickers: List[str]) -> List[Dict]:
        """
        Scan multiple stocks
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            List of scan results, sorted by grade (A+ first)
        """
        results = []
        for ticker in tickers:
            result = self.scan_stock(ticker)
            results.append(result)
        
        # Sort by grade (A+ > A > B > C > F)
        grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3, "F": 4}
        results.sort(key=lambda x: (grade_order.get(x.get("overall_grade", "F"), 4), 
                                    -x.get("detailed_analysis", {}).get("price_from_52w_high_pct", 100)))
        
        return results

