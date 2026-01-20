"""
ChatGPT Validation Script
Sends A and B grade stocks to ChatGPT for Minervini SEPA analysis validation
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from logger_config import get_logger
from config import DEFAULT_ENV_PATH, OPENAI_API_TIMEOUT

logger = get_logger(__name__)

# Load environment variables
env_file = Path(DEFAULT_ENV_PATH)
if env_file.exists():
    load_dotenv(env_file)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def load_cached_data() -> Dict:
    """Load cached stock data"""
    cache_file = Path("data/cached_stock_data.json")
    if not cache_file.exists():
        logger.error(f"Cache file not found: {cache_file}")
        return None
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
        return None


def format_stock_data_for_chatgpt(stock_result: Dict) -> str:
    """
    Format stock analysis data for ChatGPT prompt
    """
    ticker = stock_result.get("ticker", "UNKNOWN")
    company_name = stock_result.get("stock_info", {}).get("company_name", "N/A")
    grade = stock_result.get("overall_grade", "F")
    meets_criteria = stock_result.get("meets_criteria", False)
    position_size = stock_result.get("position_size", "None")
    
    detailed = stock_result.get("detailed_analysis", {})
    checklist = stock_result.get("checklist", {})
    buy_sell = stock_result.get("buy_sell_prices", {})
    
    # Build formatted text
    lines = []
    lines.append(f"STOCK: {ticker} ({company_name})")
    lines.append(f"Grade: {grade} | Meets Criteria: {meets_criteria} | Position Size: {position_size}")
    
    # For A stocks (not A+), highlight that we need to know why it's not A+
    if grade == "A":
        lines.append("*** NOTE: This stock is A grade (not A+). Please explain what criteria failures prevent it from being A+. ***")
    elif grade == "A+":
        lines.append("*** NOTE: This stock is A+ grade. Please confirm all criteria are met. ***")
    
    lines.append("")
    
    # Price Information
    lines.append("PRICE INFORMATION:")
    lines.append(f"  Current Price: ${detailed.get('current_price', 0):.2f}")
    lines.append(f"  52-Week High: ${detailed.get('52_week_high', 0):.2f}")
    lines.append(f"  52-Week Low: ${detailed.get('52_week_low', 0):.2f}")
    lines.append(f"  From 52W High: {detailed.get('price_from_52w_high_pct', 0):.1f}%")
    lines.append(f"  From 52W Low: {detailed.get('price_from_52w_low_pct', 0):.1f}%")
    lines.append("")
    
    # Buy/Sell Prices
    if buy_sell:
        lines.append("ENTRY/EXIT PRICES:")
        if buy_sell.get("pivot_price"):
            lines.append(f"  Pivot Price (Base High): ${buy_sell.get('pivot_price', 0):.2f}")
        lines.append(f"  Buy Price: ${buy_sell.get('buy_price', 0):.2f}")
        lines.append(f"  Stop Loss: ${buy_sell.get('stop_loss', 0):.2f} ({buy_sell.get('stop_loss_pct', 0):.1f}%)")
        lines.append(f"  Profit Target 1: ${buy_sell.get('profit_target_1', 0):.2f} ({buy_sell.get('profit_target_1_pct', 0):.1f}%)")
        lines.append(f"  Profit Target 2: ${buy_sell.get('profit_target_2', 0):.2f} ({buy_sell.get('profit_target_2_pct', 0):.1f}%)")
        if buy_sell.get("risk_reward_ratio"):
            lines.append(f"  Risk/Reward Ratio: {buy_sell.get('risk_reward_ratio', 0):.2f}")
        lines.append("")
    
    # PART 1: Trend & Structure
    trend = checklist.get("trend_structure", {})
    lines.append("PART 1: TREND & STRUCTURE")
    lines.append(f"  Passed: {trend.get('passed', False)}")
    if trend.get("details"):
        d = trend["details"]
        lines.append(f"  Current Price: ${d.get('current_price', 0):.2f}")
        lines.append(f"  SMA 50: ${d.get('sma_50', 0):.2f} | Above: {'✓' if d.get('above_50') else '✗'}")
        lines.append(f"  SMA 150: ${d.get('sma_150', 0):.2f} | Above: {'✓' if d.get('above_150') else '✗'}")
        lines.append(f"  SMA 200: ${d.get('sma_200', 0):.2f} | Above: {'✓' if d.get('above_200') else '✗'}")
        lines.append(f"  SMA Order (50>150>200): {'✓' if d.get('sma_order_correct') else '✗'}")
        lines.append(f"  Price from 52W Low: {d.get('price_from_52w_low_pct', 0):.1f}% (need ≥30%)")
        lines.append(f"  Price from 52W High: {d.get('price_from_52w_high_pct', 0):.1f}% (need ≤15%)")
    if trend.get("failures"):
        lines.append(f"  Failures: {', '.join(trend['failures'])}")
    lines.append("")
    
    # PART 2: Base Quality
    base = checklist.get("base_quality", {})
    lines.append("PART 2: BASE QUALITY")
    lines.append(f"  Passed: {base.get('passed', False)}")
    if base.get("details"):
        d = base["details"]
        lines.append(f"  Base Length: {d.get('base_length_weeks', 0):.1f} weeks (need 3-8 weeks)")
        lines.append(f"  Base Depth: {d.get('base_depth_pct', 0):.1f}% (need ≤25%, ≤15% is elite)")
        lines.append(f"  Base High: ${d.get('base_high', 0):.2f}")
        lines.append(f"  Base Low: ${d.get('base_low', 0):.2f}")
        lines.append(f"  Avg Close Position: {d.get('avg_close_position_pct', 0):.1f}% (need ≥50%)")
        lines.append(f"  Volume Contraction: {d.get('volume_contraction', 0):.2f}x (need <0.95x)")
    if base.get("failures"):
        lines.append(f"  Failures: {', '.join(base['failures'])}")
    lines.append("")
    
    # PART 3: Relative Strength
    rs = checklist.get("relative_strength", {})
    lines.append("PART 3: RELATIVE STRENGTH")
    lines.append(f"  Passed: {rs.get('passed', False)}")
    if rs.get("details"):
        d = rs["details"]
        lines.append(f"  RSI(14): {d.get('rsi_14', 0):.1f} (need >60)")
        lines.append(f"  Relative Strength: {d.get('relative_strength', 0):.4f} (need >0)")
        lines.append(f"  RS Rating: {d.get('rs_rating', 0):.1f}")
        lines.append(f"  Stock Return: {d.get('stock_return', 0):.2%}")
        lines.append(f"  Benchmark Return: {d.get('benchmark_return', 0):.2%}")
        lines.append(f"  Outperforming: {'✓' if d.get('outperforming') else '✗'}")
    if rs.get("failures"):
        lines.append(f"  Failures: {', '.join(rs['failures'])}")
    lines.append("")
    
    # PART 4: Volume Signature
    volume = checklist.get("volume_signature", {})
    lines.append("PART 4: VOLUME SIGNATURE")
    lines.append(f"  Passed: {volume.get('passed', False)}")
    if volume.get("details"):
        d = volume["details"]
        lines.append(f"  Base Avg Volume: {d.get('base_avg_volume', 0):,.0f}")
        lines.append(f"  Pre-Base Volume: {d.get('pre_base_volume', 0):,.0f}")
        lines.append(f"  Volume Contraction: {d.get('volume_contraction', 0):.2f}x (need <0.9x)")
        lines.append(f"  Recent Volume: {d.get('recent_volume', 0):,.0f}")
        lines.append(f"  Avg Volume (20d): {d.get('avg_volume_20d', 0):,.0f}")
        lines.append(f"  Volume Increase: {d.get('volume_increase', 0):.2f}x (need ≥1.4x for breakout)")
        lines.append(f"  In Breakout: {'✓' if d.get('in_breakout') else '✗'}")
    if volume.get("failures"):
        lines.append(f"  Failures: {', '.join(volume['failures'])}")
    lines.append("")
    
    # PART 5: Breakout Rules
    breakout = checklist.get("breakout_rules", {})
    lines.append("PART 5: BREAKOUT RULES")
    lines.append(f"  Passed: {breakout.get('passed', False)}")
    if breakout.get("details"):
        d = breakout["details"]
        lines.append(f"  Pivot Price (Base High): ${d.get('pivot_price', 0):.2f}")
        lines.append(f"  Current Price: ${d.get('current_price', 0):.2f}")
        lines.append(f"  Clears Pivot (≥2% above): {'✓' if d.get('clears_pivot') else '✗'}")
        lines.append(f"  Close Position on Breakout: {d.get('close_position_pct', 0):.1f}% (need ≥70%)")
        lines.append(f"  Volume Ratio: {d.get('volume_ratio', 0):.2f}x (need ≥1.2x)")
        lines.append(f"  In Breakout: {'✓' if d.get('in_breakout') else '✗'}")
    if breakout.get("failures"):
        lines.append(f"  Failures: {', '.join(breakout['failures'])}")
    lines.append("")
    
    return "\n".join(lines)


def create_chatgpt_prompt(stocks_data: List[str]) -> str:
    """
    Create the prompt for ChatGPT analysis
    """
    prompt = """You are an expert stock analyst specializing in Mark Minervini's SEPA (Stock Exchange Price Action) methodology.

Analyze the following stocks that have been graded A+ or A by an automated Minervini scanner.

## FIRST: TOP 3 PICKS SUMMARY
Before the detailed analysis, start with a brief "TOP 3 PICKS" section that highlights your top 3 stock recommendations from the list. For each pick, provide:
- Ticker and company name
- Why it's your top pick (1-2 sentences)
- Suggested entry price and stop loss

## THEN: For each stock, provide detailed analysis:

1. **Overall Assessment**: Do you agree with the grade? Why or why not?
2. **A+ vs A Analysis**: 
   - If the stock is graded A (not A+), explain SPECIFICALLY why it is not A+. What criteria are missing or what failures prevent it from being A+?
   - If the stock is graded A+, confirm that all criteria are met and explain why it deserves the A+ grade.
3. **Trend & Structure Analysis**: Is the stock in a proper Stage 2 uptrend?
4. **Base Quality Assessment**: Is the base pattern valid (3-8 weeks, ≤25% depth)?
5. **Relative Strength Evaluation**: Is the stock showing strong relative strength?
6. **Volume Analysis**: Is volume contracting in base and expanding on breakout?
7. **Breakout Validation**: Is the stock breaking out properly?
8. **Risk Assessment**: What are the key risks for this stock?
9. **Recommendation**: Would you take a position? If yes, what size (Full/Half/None)?
10. What is the pivot price?
11. What is the buy price?
12. What is the stop loss?

IMPORTANT: For stocks graded A (not A+), you MUST clearly explain what specific criteria failures or issues prevent them from being A+ grade. Reference the detailed checklist data provided for each stock.

Provide your analysis in a clear, structured format for each stock.

STOCKS TO ANALYZE:
"""
    prompt += "\n" + "="*80 + "\n"
    prompt += "\n".join(stocks_data)
    prompt += "\n" + "="*80 + "\n"
    prompt += "\nPlease provide your detailed analysis for each stock above.\n"
    
    return prompt


def send_to_chatgpt(prompt: str, api_key: str, model: str = "gpt-5.2", timeout: int = None) -> Optional[str]:
    """
    Send prompt to ChatGPT and get response
    """
    try:
        # Use longer timeout for large requests (default 60s, but allow override)
        request_timeout = timeout or OPENAI_API_TIMEOUT
        # For large prompts, increase timeout significantly
        if len(prompt) > 50000:
            request_timeout = max(request_timeout, 300)  # At least 5 minutes for large prompts
        
        client = OpenAI(api_key=api_key, timeout=request_timeout)
        
        logger.info(f"Sending request to ChatGPT (model: {model})...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert stock analyst specializing in Mark Minervini's SEPA methodology. Provide detailed, accurate analysis of stocks based on technical analysis principles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=16000  # Allow for detailed analysis (GPT-4o supports up to 16k tokens)
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling ChatGPT API: {e}")
        if "rate_limit" in str(e).lower():
            logger.error("Rate limit exceeded. Please wait and try again later.")
        elif "insufficient_quota" in str(e).lower():
            logger.error("Insufficient API quota. Please check your OpenAI account.")
        return None


def get_scan_results() -> List[Dict]:
    """
    Get scan results - either from existing scan or run new scan
    """
    # Try to load from most recent detailed report's scan
    # For now, we'll run a fresh scan on A and B stocks
    # In production, you might want to load from a saved scan results file
    
    cached_data = load_cached_data()
    if not cached_data:
        logger.error("No cached data available. Please run 01_fetch_stock_data.py first.")
        return []
    
    # Import scan function using importlib (can't use regular import for files starting with numbers)
    import importlib.util
    report_module_path = Path("02_generate_full_report.py")
    spec = importlib.util.spec_from_file_location("generate_full_report", report_module_path)
    report_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report_module)
    
    logger.info("Running Minervini scan on all stocks...")
    results = report_module.scan_all_stocks_from_cache(cached_data, benchmark="^GDAXI")
    
    return results


def main():
    """Main function"""
    print("="*80)
    print("CHATGPT VALIDATION - MINERVINI SEPA ANALYSIS")
    print("="*80)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY not found in environment variables")
        print("   Please add it to your .env file:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("\n   Get your API key from: https://platform.openai.com/api-keys")
        return
    
    # Get scan results
    print("\n[INFO] Loading scan results...")
    all_results = get_scan_results()
    
    if not all_results:
        print("[ERROR] No scan results available")
        return
    
    # Filter for A+ and A grade stocks
    a_plus_stocks = [
        r for r in all_results 
        if r.get("overall_grade") == "A+" and "error" not in r
    ]
    a_stocks = [
        r for r in all_results 
        if r.get("overall_grade") == "A" and "error" not in r
    ]
    
    # Combine A+ and A stocks
    all_a_stocks = a_plus_stocks + a_stocks
    
    if not all_a_stocks:
        print("[ERROR] No A+ or A grade stocks found")
        return
    
    print(f"[OK] Found {len(all_a_stocks)} stocks to analyze:")
    print(f"   A+ grade: {len(a_plus_stocks)}")
    print(f"   A grade: {len(a_stocks)}")
    
    # Format stock data for ChatGPT
    print("\n[INFO] Formatting stock data...")
    formatted_stocks = []
    for stock in all_a_stocks:
        formatted = format_stock_data_for_chatgpt(stock)
        formatted_stocks.append(formatted)
    
    # Create prompt
    print("[INFO] Creating ChatGPT prompt...")
    prompt = create_chatgpt_prompt(formatted_stocks)
    
    # Check prompt length (rough estimate - ~4 chars per token)
    prompt_length = len(prompt)
    estimated_tokens = prompt_length / 4
    
    print(f"\n[STATS] Prompt Statistics:")
    print(f"   Prompt length: {prompt_length:,} characters")
    print(f"   Estimated tokens: ~{estimated_tokens:,.0f}")
    print(f"   Stocks to analyze: {len(all_a_stocks)}")
    
    # Warn if prompt is very long
    if estimated_tokens > 100000:  # GPT-4o context limit is 128k, but we want margin
        print(f"\n[WARNING] Prompt is very long ({estimated_tokens:,.0f} tokens)")
        print("   Consider analyzing fewer stocks at once")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled")
            return
    
    # Send to ChatGPT
    print("\n[INFO] Sending to ChatGPT for analysis...")
    if estimated_tokens > 10000:
        print(f"   (Large request: ~{estimated_tokens:,.0f} tokens - this may take 5-10 minutes...)")
    else:
        print("   (This may take a few minutes...)")
    analysis = send_to_chatgpt(prompt, api_key)
    
    if not analysis:
        print("[ERROR] Failed to get analysis from ChatGPT")
        print("   Check your API key and quota, then try again")
        return
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Primary filename as requested
    output_file = REPORTS_DIR / "summary_Chat_GPT.txt"
    # Also save timestamped version for history
    timestamped_file = REPORTS_DIR / f"summary_Chat_GPT_{timestamp}.txt"
    
    # Create summary report
    report_lines = []
    report_lines.append("="*100)
    report_lines.append("CHATGPT VALIDATION - MINERVINI SEPA ANALYSIS")
    report_lines.append("="*100)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Stocks Analyzed: {len(all_a_stocks)}")
    report_lines.append(f"  A+ Grade: {len(a_plus_stocks)}")
    report_lines.append(f"  A Grade: {len(a_stocks)}")
    report_lines.append("")
    report_lines.append("="*100)
    report_lines.append("CHATGPT ANALYSIS")
    report_lines.append("="*100)
    report_lines.append("")
    report_lines.append(analysis)
    report_lines.append("")
    report_lines.append("="*100)
    report_lines.append("ORIGINAL SCAN DATA (for reference)")
    report_lines.append("="*100)
    report_lines.append("")
    
    # Add original data for reference
    for stock in all_a_stocks:
        report_lines.append(format_stock_data_for_chatgpt(stock))
        report_lines.append("")
        report_lines.append("-"*100)
        report_lines.append("")
    
    # Write to both files
    report_content = "\n".join(report_lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    with open(timestamped_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n[SUCCESS] Analysis complete!")
    print(f"   Report saved to: {output_file}")
    print(f"   Backup saved to: {timestamped_file}")
    print(f"   File size: {output_file.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()
