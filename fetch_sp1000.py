"""
Fetch S&P 1000 components (S&P 500 + S&P 400 Mid-Cap + S&P 600 Small-Cap)
Uses multiple methods to ensure we get the data
"""
import requests
from pathlib import Path
import time
import pandas as pd
from io import StringIO

def fetch_sp500_tickers():
    """Fetch S&P 500 tickers from Wikipedia"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        print(f"   Fetching from: {url}")
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            tables = pd.read_html(StringIO(response.text))
            if len(tables) > 0:
                sp500_table = tables[0]
                if 'Symbol' in sp500_table.columns:
                    tickers = sp500_table['Symbol'].tolist()
                    # Clean tickers (convert BRK.B to BRK-B for Yahoo Finance)
                    cleaned = []
                    for t in tickers:
                        t = str(t).replace('.', '-').strip()
                        if t and t != 'nan':
                            cleaned.append(t)
                    return cleaned
    except Exception as e:
        print(f"   Error: {e}")
    return []

def fetch_sp400_tickers():
    """Fetch S&P 400 Mid-Cap tickers"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
        print(f"   Fetching from: {url}")
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            tables = pd.read_html(StringIO(response.text))
            if len(tables) > 0:
                sp400_table = tables[0]
                if 'Symbol' in sp400_table.columns:
                    tickers = sp400_table['Symbol'].tolist()
                    cleaned = []
                    for t in tickers:
                        t = str(t).replace('.', '-').strip()
                        if t and t != 'nan':
                            cleaned.append(t)
                    return cleaned
    except Exception as e:
        print(f"   Error: {e}")
    return []

def fetch_sp600_tickers():
    """Fetch S&P 600 Small-Cap tickers"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"
        print(f"   Fetching from: {url}")
        response = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            tables = pd.read_html(StringIO(response.text))
            if len(tables) > 0:
                sp600_table = tables[0]
                if 'Symbol' in sp600_table.columns:
                    tickers = sp600_table['Symbol'].tolist()
                    cleaned = []
                    for t in tickers:
                        t = str(t).replace('.', '-').strip()
                        if t and t != 'nan':
                            cleaned.append(t)
                    return cleaned
    except Exception as e:
        print(f"   Error: {e}")
    return []

def main():
    print("="*80)
    print("FETCHING S&P 1000 COMPONENTS")
    print("="*80)
    
    print("\n[1/3] Fetching S&P 500...")
    sp500 = fetch_sp500_tickers()
    if sp500:
        print(f"   [OK] Found {len(sp500)} tickers")
    else:
        print(f"   [FAIL] Failed to fetch S&P 500")
        sp500 = []
    
    print("\n[2/3] Fetching S&P 400 Mid-Cap...")
    sp400 = fetch_sp400_tickers()
    if sp400:
        print(f"   [OK] Found {len(sp400)} tickers")
    else:
        print(f"   [FAIL] Failed to fetch S&P 400 (may not be available on Wikipedia)")
        sp400 = []
    
    print("\n[3/3] Fetching S&P 600 Small-Cap...")
    sp600 = fetch_sp600_tickers()
    if sp600:
        print(f"   [OK] Found {len(sp600)} tickers")
    else:
        print(f"   [FAIL] Failed to fetch S&P 600 (may not be available on Wikipedia)")
        sp600 = []
    
    # Combine and deduplicate
    all_tickers = list(set(sp500 + sp400 + sp600))
    all_tickers.sort()
    
    print(f"\n[OK] Total unique tickers: {len(all_tickers)}")
    print(f"   S&P 500: {len(sp500)}")
    print(f"   S&P 400: {len(sp400)}")
    print(f"   S&P 600: {len(sp600)}")
    
    if len(all_tickers) == 0:
        print("\n[WARNING] No tickers fetched. Wikipedia may be blocking requests.")
        print("   Alternative: Manually add S&P components or use a different source.")
        return
    
    # Save to file
    output_file = Path("sp1000_tickers.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# S&P 1000 Components (S&P 500 + S&P 400 + S&P 600)\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total: {len(all_tickers)} tickers\n")
        f.write(f"# S&P 500: {len(sp500)} | S&P 400: {len(sp400)} | S&P 600: {len(sp600)}\n\n")
        for ticker in all_tickers:
            f.write(f"{ticker}\n")
    
    print(f"\n[SUCCESS] Saved to: {output_file}")
    if len(all_tickers) > 0:
        print(f"   First 10: {', '.join(all_tickers[:10])}")
        if len(all_tickers) > 10:
            print(f"   Last 10: {', '.join(all_tickers[-10:])}")
    
    # Also create a section to append to watchlist
    watchlist_section = Path("sp1000_watchlist_section.txt")
    with open(watchlist_section, 'w', encoding='utf-8') as f:
        f.write("\n# ============================================\n")
        f.write("# S&P 1000 COMPONENTS\n")
        f.write("# ============================================\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total: {len(all_tickers)} tickers\n\n")
        for ticker in all_tickers:
            f.write(f"{ticker}\n")
    
    print(f"   Watchlist section saved to: {watchlist_section}")
    print(f"\n   To add to watchlist.txt, append the contents of {watchlist_section}")

if __name__ == "__main__":
    main()
