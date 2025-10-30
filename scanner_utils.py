#!/usr/bin/env python3
"""
Scanner Utilities - Helper functions for the EOD Scanner
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# Optional imports for plotting
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

def analyze_historical_performance(output_dir="eod_scanner_output", days_back=30):
    """Analyze historical performance of scanner recommendations."""
    output_path = Path(output_dir)
    files = list(output_path.glob("long_candidates_*.csv"))
    
    if not files:
        print("No historical files found")
        return
    
    performance_data = []
    
    for file in sorted(files)[-days_back:]:
        try:
            df = pd.read_csv(file)
            date_str = file.stem.split('_')[-1]
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Add to performance tracking
            for _, row in df.head(10).iterrows():  # Top 10 recommendations
                performance_data.append({
                    'date': date,
                    'symbol': row['symbol'],
                    'score': row['score_long'],
                    'rsi': row['rsi14'],
                    'risk_level': row.get('risk_level', 'Unknown')
                })
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        print(f"\nHistorical Analysis Summary ({len(files)} files analyzed):")
        print(f"Total recommendations: {len(perf_df)}")
        print(f"Average score: {perf_df['score'].mean():.1f}")
        print(f"Risk distribution:")
        print(perf_df['risk_level'].value_counts())
        
        return perf_df
    
def update_watchlist(symbols, config_file="scanner_config.json"):
    """Update custom watchlist in configuration."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config['universe'] = 'CUSTOM'
        config['custom_symbols'] = symbols
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Updated watchlist with {len(symbols)} symbols")
        print("Set universe to 'CUSTOM'")
        
    except Exception as e:
        print(f"Error updating watchlist: {e}")

def quick_scan_summary(csv_file):
    """Quick summary of a scan result file."""
    try:
        df = pd.read_csv(csv_file)
        print(f"\nQuick Summary of {csv_file}:")
        print(f"Total symbols: {len(df)}")
        print(f"High scorers (score >= 5): {len(df[df['score_long'] >= 5])}")
        print(f"Low risk opportunities: {len(df[df.get('risk_level', '') == 'Low'])}")
        
        # Top 5 recommendations
        print(f"\nTop 5 Long Candidates:")
        top5 = df.nlargest(5, 'score_long')[['symbol', 'score_long', 'rsi14', 'risk_level']]
        print(top5.to_string(index=False))
        
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "analyze":
            analyze_historical_performance()
        elif command == "summary" and len(sys.argv) > 2:
            quick_scan_summary(sys.argv[2])
        elif command == "watchlist" and len(sys.argv) > 2:
            symbols = sys.argv[2].split(',')
            update_watchlist([s.strip() for s in symbols])
        else:
            print("Usage:")
            print("  python scanner_utils.py analyze")
            print("  python scanner_utils.py summary <csv_file>")
            print("  python scanner_utils.py watchlist SYMBOL1,SYMBOL2,...")
    else:
        print("Available utilities:")
        print("- analyze: Historical performance analysis")
        print("- summary: Quick summary of scan results")
        print("- watchlist: Update custom watchlist")