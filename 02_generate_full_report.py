"""
Generate full Minervini SEPA analysis report from cached data
Produces: Summary report + Detailed list of all stocks
"""
import json
import sys
import io
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional
from bot import TradingBot
from minervini_scanner import MinerviniScanner
from data_provider import StockDataProvider
from logger_config import setup_logging, get_logger
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
setup_logging(log_level="INFO", log_to_file=True)
logger = get_logger(__name__)

CACHE_FILE = Path("data/cached_stock_data.json")
REPORTS_DIR = Path("reports")


def load_cached_data() -> Dict:
    """Load cached stock data"""
    if not CACHE_FILE.exists():
        logger.error(f"Cache file not found: {CACHE_FILE}")
        logger.error("Please run fetch_stock_data.py first to fetch and cache data")
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data.get('stocks', {}))} stocks from cache")
        return data
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return None


def convert_cached_data_to_dataframe(cached_stock: Dict) -> Optional[pd.DataFrame]:
    """Convert cached historical data back to DataFrame"""
    try:
        hist_dict = cached_stock.get("historical_data", {})
        if not hist_dict or "data" not in hist_dict:
            return None
        
        # Reconstruct DataFrame
        data = hist_dict["data"]
        df = pd.DataFrame(data)
        
        # Convert index back to datetime
        if "index" in hist_dict and hist_dict["index"]:
            df.index = pd.to_datetime(hist_dict["index"])
        elif "Date" in df.columns:
            df.index = pd.to_datetime(df["Date"])
            df = df.drop("Date", axis=1)
        else:
            # Try to find date column
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    df.index = pd.to_datetime(df[col])
                    df = df.drop(col, axis=1)
                    break
        
        # Ensure proper column names (case-insensitive)
        df.columns = [col.capitalize() if col.lower() in ['open', 'high', 'low', 'close', 'volume'] else col 
                     for col in df.columns]
        
        # Map common column name variations
        col_mapping = {
            'Open': ['Open', 'open', 'OPEN'],
            'High': ['High', 'high', 'HIGH'],
            'Low': ['Low', 'low', 'LOW'],
            'Close': ['Close', 'close', 'CLOSE', 'Adj Close', 'adj close'],
            'Volume': ['Volume', 'volume', 'VOLUME', 'Vol', 'vol']
        }
        
        # Find and rename columns
        for target_col, variations in col_mapping.items():
            for var in variations:
                if var in df.columns and target_col not in df.columns:
                    df = df.rename(columns={var: target_col})
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}. Available: {list(df.columns)}")
            return None
        
        # Return only required columns in correct order
        return df[required_cols]
    except Exception as e:
        logger.error(f"Error converting cached data to DataFrame: {e}", exc_info=True)
        return None


class CachedDataProvider:
    """Data provider that uses cached data"""
    def __init__(self, cached_stocks: Dict, original_provider):
        self.cached_stocks = cached_stocks
        self.original_provider = original_provider
    
    def get_historical_data(self, ticker: str, period: str = "1y", interval: str = "1d"):
        """Get historical data from cache or fallback to original"""
        if ticker in self.cached_stocks:
            cached = self.cached_stocks[ticker]
            if cached.get("data_available", False):
                hist = convert_cached_data_to_dataframe(cached)
                if hist is not None and not hist.empty:
                    return hist
        # Fallback to original provider if not in cache
        return self.original_provider.get_historical_data(ticker, period, interval)
    
    def get_stock_info(self, ticker: str):
        """Get stock info from cache or fallback to original"""
        if ticker in self.cached_stocks:
            cached = self.cached_stocks[ticker]
            stock_info = cached.get("stock_info", {})
            if stock_info:
                return stock_info
        return self.original_provider.get_stock_info(ticker)
    
    def calculate_relative_strength(self, ticker: str, benchmark: str, period: int = 252):
        """Use original provider for relative strength (needs benchmark data)"""
        return self.original_provider.calculate_relative_strength(ticker, benchmark, period)


def scan_all_stocks_from_cache(cached_data: Dict, benchmark: str = "^GDAXI", single_ticker: Optional[str] = None) -> List[Dict]:
    """Scan all stocks using cached data"""
    stocks = cached_data.get("stocks", {})
    
    # Initialize bot
    bot = TradingBot(skip_trading212=True, benchmark=benchmark)
    
    # Create cached data provider
    cached_provider = CachedDataProvider(stocks, bot.data_provider)
    
    # Create scanner with cached provider
    scanner = MinerviniScanner(cached_provider, benchmark=benchmark)
    
    results = []
    
    # Filter to single ticker if specified
    if single_ticker:
        if single_ticker in stocks:
            stocks = {single_ticker: stocks[single_ticker]}
        else:
            logger.error(f"Ticker {single_ticker} not found in cache")
            return []
    
    total = len(stocks)
    print(f"\n{'='*80}")
    print(f"RUNNING MINERVINI SEPA ANALYSIS")
    print(f"{'='*80}")
    print(f"Total stocks: {total}")
    if single_ticker:
        print(f"Single stock mode: {single_ticker}")
    print(f"{'='*80}\n")
    
    # Scan each stock
    for i, (ticker, cached_stock) in enumerate(stocks.items(), 1):
        if not cached_stock.get("data_available", False):
            # Skip stocks without data
            error_msg = cached_stock.get("error", "No data available")
            print(f"[{i}/{total}] {ticker:12s} - ✗ {error_msg}")
            results.append({
                "ticker": ticker,
                "error": error_msg,
                "meets_criteria": False,
                "overall_grade": "F"
            })
            continue
        
        print(f"[{i}/{total}] Scanning {ticker:12s}...", end=" ", flush=True)
        
        # Scan using cached data
        try:
            result = scanner.scan_stock(ticker)
            # Add company name from cached stock_info if available
            cached_stock_info = cached_stock.get("stock_info", {})
            company_name = cached_stock_info.get("company_name", "")
            if company_name and "stock_info" in result:
                result["stock_info"]["company_name"] = company_name
            elif company_name:
                if "stock_info" not in result:
                    result["stock_info"] = {}
                result["stock_info"]["company_name"] = company_name
            grade = result.get("overall_grade", "F")
            meets = "✓" if result.get("meets_criteria", False) else "✗"
            print(f"{meets} Grade: {grade}")
            results.append(result)
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error scanning {ticker}: {e}", exc_info=True)
            results.append({
                "ticker": ticker,
                "error": str(e),
                "meets_criteria": False,
                "overall_grade": "F"
            })
    
    return results


def get_company_name(result: Dict) -> str:
    """Extract company name from result"""
    stock_info = result.get("stock_info", {})
    company_name = stock_info.get("company_name", "")
    return company_name if company_name else "N/A"


def generate_summary_report(results: List[Dict], output_file: Optional[Path] = None):
    """Generate summary report with grade distribution"""
    total = len(results)
    grade_counts = defaultdict(int)
    meets_criteria = sum(1 for r in results if r.get('meets_criteria', False))
    position_sizes = defaultdict(int)
    criteria_pass = defaultdict(int)
    
    for result in results:
        if "error" not in result:
            grade = result.get("overall_grade", "F")
            grade_counts[grade] += 1
            position = result.get("position_size", "None")
            position_sizes[position] += 1
            
            checklist = result.get("checklist", {})
            if checklist.get("trend_structure", {}).get("passed", False):
                criteria_pass["Trend & Structure"] += 1
            if checklist.get("base_quality", {}).get("passed", False):
                criteria_pass["Base Quality"] += 1
            if checklist.get("relative_strength", {}).get("passed", False):
                criteria_pass["Relative Strength"] += 1
            if checklist.get("volume_signature", {}).get("passed", False):
                criteria_pass["Volume Signature"] += 1
            if checklist.get("breakout_rules", {}).get("passed", False):
                criteria_pass["Breakout Rules"] += 1
    
    # Generate report
    lines = []
    lines.append("=" * 100)
    lines.append("MINERVINI SEPA SCAN - SUMMARY REPORT")
    lines.append("=" * 100)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Overall Statistics
    lines.append("📊 OVERALL STATISTICS")
    lines.append("-" * 100)
    lines.append(f"Total Stocks Scanned: {total}")
    lines.append(f"Stocks Meeting Criteria: {meets_criteria} ({meets_criteria/total*100:.1f}%)")
    lines.append(f"Stocks NOT Meeting Criteria: {total - meets_criteria} ({(total-meets_criteria)/total*100:.1f}%)")
    lines.append("")
    
    # Grade Distribution
    lines.append("🎯 GRADE DISTRIBUTION")
    lines.append("-" * 100)
    grade_order = ["A+", "A", "B", "C", "F"]
    
    for grade in grade_order:
        count = grade_counts.get(grade, 0)
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        
        if grade == "A+":
            position = "Full Position"
        elif grade == "A":
            position = "Half Position"
        elif grade == "B":
            position = "Half Position (Watch)"
        elif grade == "C":
            position = "Avoid"
        else:
            position = "Avoid"
        
        lines.append(f"{grade:3s}: {count:4d} stocks ({percentage:5.1f}%) {bar} {position}")
    
    lines.append("")
    
    # Position Size Distribution
    lines.append("💰 POSITION SIZE RECOMMENDATIONS")
    lines.append("-" * 100)
    for position in ["Full", "Half", "None"]:
        count = position_sizes.get(position, 0)
        percentage = (count / total * 100) if total > 0 else 0
        lines.append(f"{position:6s}: {count:4d} stocks ({percentage:5.1f}%)")
    lines.append("")
    
    # Criteria Pass Rates
    lines.append("✅ CRITERIA PASS RATES")
    lines.append("-" * 100)
    criteria_names = [
        "Trend & Structure",
        "Base Quality",
        "Relative Strength",
        "Volume Signature",
        "Breakout Rules"
    ]
    
    for criterion in criteria_names:
        count = criteria_pass.get(criterion, 0)
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        lines.append(f"{criterion:25s}: {count:4d} stocks ({percentage:5.1f}%) {bar}")
    
    lines.append("")
    
    # Top Stocks by Grade
    lines.append("📈 TOP STOCKS BY GRADE")
    lines.append("-" * 100)
    grade_order_list = ["A+", "A", "B", "C"]
    for grade in grade_order_list:
        stocks = [r for r in results if "error" not in r and r.get("overall_grade") == grade]
        if not stocks:
            continue
        
        # Sort by price from 52W high (closest to high is better)
        stocks_sorted = sorted(
            stocks,
            key=lambda x: x.get("detailed_analysis", {}).get("price_from_52w_high_pct", 100)
        )
        
        lines.append(f"\n{grade} Grade ({len(stocks_sorted)} stocks):")
        for i, stock in enumerate(stocks_sorted[:10], 1):  # Top 10 per grade
            ticker = stock.get("ticker", "UNKNOWN")
            company_name = get_company_name(stock)
            price_pct = stock.get("detailed_analysis", {}).get("price_from_52w_high_pct", 0)
            if company_name and company_name != "N/A":
                lines.append(f"  {i:2d}. {ticker:12s} ({company_name[:50]}) - {price_pct:.1f}% from 52W high")
            else:
                lines.append(f"  {i:2d}. {ticker:12s} - {price_pct:.1f}% from 52W high")
    
    lines.append("")
    lines.append("=" * 100)
    
    # Print to console
    report_text = "\n".join(lines)
    print(report_text)
    
    # Save to file
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\nSummary report saved to: {output_file}")
    
    return report_text


def format_stock_header(result: Dict) -> str:
    """Format stock header with ticker and company name"""
    ticker = result.get("ticker", "UNKNOWN")
    company_name = get_company_name(result)
    grade = result.get("overall_grade", "F")
    meets = result.get("meets_criteria", False)
    position = result.get("position_size", "None")
    
    if company_name and company_name != "N/A":
        return f"STOCK: {ticker} ({company_name}) | Grade: {grade} | Meets Criteria: {meets} | Position Size: {position}"
    else:
        return f"STOCK: {ticker} | Grade: {grade} | Meets Criteria: {meets} | Position Size: {position}"


def generate_detailed_report(results: List[Dict], output_file: Optional[Path] = None):
    """Generate detailed report with complete explanations for each stock"""
    # Sort by grade (A+ first, F last)
    grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3, "F": 4}
    results_sorted = sorted(
        [r for r in results if "error" not in r],
        key=lambda x: (grade_order.get(x.get("overall_grade", "F"), 4), 
                       -x.get("detailed_analysis", {}).get("price_from_52w_high_pct", 100))
    )
    
    # Group by grade
    by_grade = defaultdict(list)
    for result in results_sorted:
        grade = result.get("overall_grade", "F")
        by_grade[grade].append(result)
    
    # Generate report
    lines = []
    lines.append("=" * 100)
    lines.append("MINERVINI SEPA SCAN - DETAILED ANALYSIS")
    lines.append("=" * 100)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Stocks: {len(results_sorted)}")
    lines.append("")
    
    # Print by grade
    grade_order_list = ["A+", "A", "B", "C", "F"]
    for grade in grade_order_list:
        stocks = by_grade.get(grade, [])
        if not stocks:
            continue
        
        lines.append("#" * 100)
        lines.append(f"# GRADE {grade} ({len(stocks)} stocks)")
        lines.append("#" * 100)
        lines.append("")
        
        for stock in stocks:
            # Stock header with company name
            lines.append("=" * 100)
            lines.append(format_stock_header(stock))
            lines.append("=" * 100)
            lines.append("")
            
            # Price info
            detailed = stock.get("detailed_analysis", {})
            if detailed:
                lines.append("[PRICE INFO]")
                lines.append(f"  Current Price: ${detailed.get('current_price', 0):.2f}")
                lines.append(f"  52-Week High: ${detailed.get('52_week_high', 0):.2f}")
                lines.append(f"  52-Week Low: ${detailed.get('52_week_low', 0):.2f}")
                lines.append(f"  From 52W High: {detailed.get('price_from_52w_high_pct', 0):.1f}%")
                lines.append(f"  From 52W Low: {detailed.get('price_from_52w_low_pct', 0):.1f}%")
                lines.append("")
            
            # Checklist summary
            checklist = stock.get("checklist", {})
            criteria_names = [
                ("trend_structure", "Trend & Structure"),
                ("base_quality", "Base Quality"),
                ("relative_strength", "Relative Strength"),
                ("volume_signature", "Volume Signature"),
                ("breakout_rules", "Breakout Rules")
            ]
            
            for key, name in criteria_names:
                if key in checklist:
                    criterion = checklist[key]
                    passed = criterion.get("passed", False)
                    status = "[PASS]" if passed else "[FAIL]"
                    lines.append("=" * 100)
                    lines.append(f"{status} PART {criteria_names.index((key, name)) + 1}: {name}")
                    lines.append("=" * 100)
                    
                    description = criterion.get("description", "")
                    if description:
                        lines.append(f"Description: {description}")
                        lines.append("")
                    
                    # Show key checks
                    checks = criterion.get("checks", [])
                    if checks:
                        for check in checks[:5]:  # Limit to first 5 checks
                            check_name = check.get("name", "")
                            check_passed = check.get("passed", False)
                            check_mark = "✓" if check_passed else "✗"
                            lines.append(f"  {check_mark} {check_name}")
                    else:
                        # Show summary
                        failures = criterion.get("failures", [])
                        if failures:
                            lines.append("  Failures:")
                            for failure in failures[:3]:  # Limit to first 3 failures
                                lines.append(f"    - {failure}")
                    
                    lines.append("")
            
            lines.append("")
    
    # Print to console (truncated for very long reports)
    report_text = "\n".join(lines)
    if len(report_text) > 50000:  # If very long, only show first part
        print(report_text[:50000])
        print("\n... (report truncated in console, full version saved to file)")
    else:
        print(report_text)
    
    # Save to file
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\nDetailed report saved to: {output_file}")
    
    return report_text


def main():
    parser = argparse.ArgumentParser(
        description="Generate full Minervini SEPA analysis report from cached data"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        help="Analyze single stock only (optional)"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh data before analysis (runs fetch_stock_data.py)"
    )
    parser.add_argument(
        "--benchmark",
        default="^GDAXI",
        choices=["^GDAXI", "^FCHI", "^AEX", "^SSMI", "^OMX"],
        help="Benchmark index (default: ^GDAXI)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Generate only summary report (skip detailed)"
    )
    parser.add_argument(
        "--detailed-only",
        action="store_true",
        help="Generate only detailed report (skip summary)"
    )
    
    args = parser.parse_args()
    
    # Refresh data if requested
    if args.refresh:
        print("Refreshing stock data...")
        from fetch_stock_data import fetch_all_data
        fetch_all_data(force_refresh=True, benchmark=args.benchmark)
        print()
    
    # Load cached data
    cached_data = load_cached_data()
    if cached_data is None:
        print("Error: Could not load cached data")
        print("Please run: python fetch_stock_data.py")
        sys.exit(1)
    
    # Scan all stocks
    results = scan_all_stocks_from_cache(
        cached_data, 
        benchmark=args.benchmark,
        single_ticker=args.ticker
    )
    
    if not results:
        print("No results to report")
        return
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate reports
    if not args.detailed_only:
        summary_file = REPORTS_DIR / f"summary_report_{timestamp}.txt"
        generate_summary_report(results, summary_file)
        print()
    
    if not args.summary_only:
        detailed_file = REPORTS_DIR / f"detailed_report_{timestamp}.txt"
        generate_detailed_report(results, detailed_file)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"Reports saved to: {REPORTS_DIR}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

