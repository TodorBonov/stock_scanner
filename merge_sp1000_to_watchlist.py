"""
Merge S&P 1000 tickers into watchlist.txt, avoiding duplicates
"""
from pathlib import Path

def get_existing_tickers(watchlist_file):
    """Extract all tickers from watchlist.txt"""
    existing = set()
    with open(watchlist_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                existing.add(line.upper())
    return existing

def get_sp1000_tickers(sp1000_file):
    """Extract all tickers from sp1000_watchlist_section.txt"""
    tickers = []
    with open(sp1000_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                tickers.append(line)
    return tickers

def main():
    watchlist_file = Path("watchlist.txt")
    sp1000_file = Path("sp1000_watchlist_section.txt")
    
    if not sp1000_file.exists():
        print(f"[ERROR] {sp1000_file} not found. Run fetch_sp1000.py first.")
        return
    
    print("="*80)
    print("MERGING S&P 1000 INTO WATCHLIST")
    print("="*80)
    
    print("\n[1/3] Reading existing watchlist...")
    existing = get_existing_tickers(watchlist_file)
    print(f"   Found {len(existing)} existing tickers")
    
    print("\n[2/3] Reading S&P 1000 tickers...")
    sp1000_tickers = get_sp1000_tickers(sp1000_file)
    print(f"   Found {len(sp1000_tickers)} S&P 1000 tickers")
    
    print("\n[3/3] Filtering duplicates...")
    new_tickers = []
    duplicates = []
    for ticker in sp1000_tickers:
        if ticker.upper() not in existing:
            new_tickers.append(ticker)
        else:
            duplicates.append(ticker)
    
    print(f"   New tickers to add: {len(new_tickers)}")
    print(f"   Duplicates (skipped): {len(duplicates)}")
    
    if len(new_tickers) == 0:
        print("\n[INFO] All S&P 1000 tickers are already in watchlist!")
        return
    
    # Append to watchlist
    print(f"\n[4/4] Appending {len(new_tickers)} new tickers to watchlist...")
    with open(watchlist_file, 'a', encoding='utf-8') as f:
        f.write("\n# ============================================\n")
        f.write("# S&P 1000 COMPONENTS (S&P 500 + S&P 400 + S&P 600)\n")
        f.write("# ============================================\n")
        f.write(f"# Added: {len(new_tickers)} new tickers (skipped {len(duplicates)} duplicates)\n\n")
        for ticker in new_tickers:
            f.write(f"{ticker}\n")
    
    print(f"\n[SUCCESS] Added {len(new_tickers)} tickers to {watchlist_file}")
    print(f"   Total tickers in watchlist now: {len(existing) + len(new_tickers)}")
    if len(new_tickers) <= 20:
        print(f"   New tickers: {', '.join(new_tickers)}")
    else:
        print(f"   First 10 new tickers: {', '.join(new_tickers[:10])}")
        print(f"   Last 10 new tickers: {', '.join(new_tickers[-10:])}")

if __name__ == "__main__":
    main()
