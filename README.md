# Minervini SEPA Scanner

A professional-grade stock scanner that implements Mark Minervini's exact SEPA (Stock Exchange Price Action) methodology for European stocks. This scanner evaluates stocks against Minervini's complete checklist: Trend & Structure, Base Quality, Relative Strength, Volume Signature, and Breakout Rules.

## Features

1. **Complete Minervini SEPA Checklist**: Implements all 5 parts of Minervini's methodology
   - ✅ Trend & Structure (NON-NEGOTIABLE)
   - ✅ Base Quality (3-8 week bases, ≤25% depth)
   - ✅ Relative Strength (RS line, RSI > 60)
   - ✅ Volume Signature (dry volume in base, +40% on breakout)
   - ✅ Breakout Day Rules (pivot clearance, volume expansion)

2. **Automatic Grading**: Stocks receive A+, A, B, C, or F grades
   - **A+**: All criteria met → Full position
   - **A**: 1-2 minor flaws → Half position
   - **B/C/F**: More than 2 flaws → Walk away

3. **European Market Focus**: Optimized for SEPA stocks
   - Supports DAX (^GDAXI), CAC 40 (^FCHI), AEX (^AEX), Swiss (^SSMI), Nordics (^OMX)
   - Relative strength calculated vs European benchmarks

4. **Free Data Sources**: Uses Yahoo Finance (yfinance) as primary data source
   - No API key required for basic scanning
   - Alpha Vantage optional for additional data

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Optional: Get Alpha Vantage API Key (Optional)

For additional data coverage, get a free Alpha Vantage key:
1. Go to https://www.alphavantage.co/support/#api-key
2. Get your free API key
3. Add to `.env` file: `ALPHA_VANTAGE_API_KEY=your_key_here`

**Note**: The scanner works with just Yahoo Finance (yfinance) - no API key needed!

### 3. Configure (Optional)

Create a `.env` file in the project root (optional):
```
ALPHA_VANTAGE_API_KEY=your_key_here
```

## Usage

### Scan a Single Stock

```bash
python main.py scan AAPL
```

Output as JSON:
```bash
python main.py scan AAPL --json
```

### Scan Multiple Stocks

```bash
python main.py scan-multi AAPL MSFT GOOGL TSLA
```

### Search and Scan

If you have Trading 212 API credentials:
```bash
python main.py search "Apple Inc" --use-trading212
```

### Change Benchmark Index

For different European markets:
```bash
# DAX (Germany) - default
python main.py --benchmark ^GDAXI scan AAPL

# CAC 40 (France)
python main.py --benchmark ^FCHI scan AAPL

# AEX (Netherlands)
python main.py --benchmark ^AEX scan AAPL

# Swiss Market
python main.py --benchmark ^SSMI scan AAPL

# Nordics
python main.py --benchmark ^OMX scan AAPL
```

## Minervini SEPA Criteria Explained

### PART 1: Trend & Structure (NON-NEGOTIABLE)

**All of these must pass, or it's NOT SEPA:**
- ✅ Price above 50, 150, 200 SMA
- ✅ 50 SMA > 150 SMA > 200 SMA
- ✅ All three SMAs sloping UP
- ✅ Price ≥ 30% above 52-week low
- ✅ Price within 10–15% of 52-week high

### PART 2: Base Quality

**This is where amateurs fail:**
- ✅ Base length 3–8 weeks (daily chart)
- ✅ Depth ≤ 20–25% (≤15% is elite)
- ✅ No wide, sloppy candles
- ✅ Tight closes near highs
- ✅ Volume contracts inside base

### PART 3: Relative Strength (CRITICAL)

**Minervini buys strength, not value:**
- ✅ RS line near or at new highs
- ✅ Stock outperforms index (DAX / STOXX / FTSE)
- ✅ RSI(14) > 60 before breakout

### PART 4: Volume Signature

- ✅ Dry volume in base
- ✅ Breakout volume +40% or more
- ✅ No heavy sell volume before breakout

### PART 5: Breakout Day Rules

- ✅ Clears pivot decisively
- ✅ Closes in top 25% of range
- ✅ Volume expansion present

## Output Format

The scanner provides detailed results for each stock:

```
================================================================================
[STOCK] AAPL - Grade: A+ | Meets Criteria: True | Position Size: Full
================================================================================

[PRICE] Price Information:
   Current Price: $175.50
   52-Week High: $198.23
   52-Week Low: $124.17
   From 52W High: 11.5%
   From 52W Low: 41.3%

[PART 1] Trend & Structure (NON-NEGOTIABLE):
   Status: ✅ PASSED
   Price above 50 SMA: True
   Price above 150 SMA: True
   Price above 200 SMA: True
   SMA Order (50>150>200): True
   50 SMA: $165.20
   150 SMA: $155.80
   200 SMA: $150.30

[PART 2] Base Quality:
   Status: ✅ PASSED
   Base Length: 5.2 weeks (need 3-8)
   Base Depth: 12.3% (need ≤25%, ≤15% elite)
   Volume Contraction: 0.75x
   Avg Close Position: 68.5% of range

... (and so on for all 5 parts)
```

## Position Sizing Rules

Based on Minervini's methodology:

- **A+ Grade**: All boxes checked → **Full position**
- **A Grade**: 1–2 minor flaws → **Half position**
- **B/C/F Grade**: More than 2 flaws → **WALK AWAY**

## Project Structure

```
.
├── minervini_scanner.py  # Core Minervini SEPA scanner logic
├── bot.py                # Main bot interface
├── main.py               # CLI interface
├── data_provider.py      # Data fetching (yfinance, Alpha Vantage)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Data Sources

- **Yahoo Finance (yfinance)**: Primary data source (free, no API key needed)
  - Historical price/volume data
  - Moving averages
  - RSI calculations
  - 52-week highs/lows

- **Alpha Vantage** (optional): Additional data coverage
  - Free tier: 25 requests/day
  - Premium: Higher limits

- **Trading 212 API** (optional): For stock search functionality

## Important Notes

⚠️ **This scanner is for educational purposes. Always:**
- Test thoroughly before using with real money
- Start with small positions
- Never risk more than you can afford to lose
- Review all recommendations manually
- Understand that past performance doesn't guarantee future results
- This implements Minervini's methodology but is not financial advice

✅ **What This Scanner Does:**
- ✅ Real technical analysis (SMAs, RSI, volume patterns)
- ✅ Real base identification and quality assessment
- ✅ Real relative strength calculations vs benchmarks
- ✅ Real breakout pattern detection
- ✅ Complete Minervini checklist evaluation

## Example Workflow

1. **Screen stocks** using TradingView or your preferred screener with basic filters:
   - Close > SMA50
   - SMA50 > SMA150
   - SMA150 > SMA200
   - RSI(14) > 60
   - Close within 15% of 52W high
   - Average Volume > 300k

2. **Export ticker list** from your screener

3. **Scan with this tool**:
   ```bash
   python main.py scan-multi TICKER1 TICKER2 TICKER3
   ```

4. **Review A+ and A graded stocks** for potential entries

5. **Apply pyramiding rules** (not automated - manual execution):
   - First Entry: Buy pivot breakout (0.5-1% risk per trade)
   - First Add: Add if stock moves +2-3% from entry with volume confirmation
   - Second Add: Add if price respects 10 SMA, no wide red candles

## License

This project is provided as-is for educational purposes.

## Disclaimer

This software is for educational purposes only. Trading involves risk of loss. Always do your own research and consult with a financial advisor before making investment decisions. The authors are not responsible for any financial losses incurred from using this software.
