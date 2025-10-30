#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE End-of-Day Scanner (Next-Day Intraday Candidates)
-----------------------------------------------------
What it does (after 3:30 PM IST):
- Downloads daily OHLCV for a universe (default: NIFTY 50) using yfinance
- Computes common setups: NR7, Inside Day, Breakout/Breadcrumb, Volume Surge, Trend Alignment, CPR width
- Scores long/short candidates and exports CSV + a human-readable summary

Requirements:
    pip install pandas numpy yfinance pytz

Usage:
    python eod_scanner_nse.py
"""

import os
import math
import datetime as dt
from dataclasses import dataclass
from typing import List, Dict

import numpy as np
import pandas as pd
import pytz

try:
    import yfinance as yf
except Exception as e:
    raise SystemExit("Please install yfinance first: pip install yfinance")


# ---------------------
# Universe (NIFTY 50) - update if needed
# ---------------------
NIFTY50 = [
    # As of 2024-2025 period. Feel free to tweak.
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "LT", "SBIN", "BHARTIARTL", "HINDUNILVR",
    "HCLTECH", "AXISBANK", "BAJFINANCE", "KOTAKBANK", "MARUTI", "ASIANPAINT", "SUNPHARMA", "LUPIN", "ONGC",
    "POWERGRID", "TITAN", "WIPRO", "ULTRACEMCO", "NTPC", "M&M", "NESTLEIND", "BAJAJFINSV", "ADANIENT",
    "ADANIPORTS", "HINDALCO", "JSWSTEEL", "TATASTEEL", "TATAMOTORS", "TATACONSUM", "COALINDIA", "GRASIM",
    "BPCL", "HEROMOTOCO", "BRITANNIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "HDFCLIFE", "BAJAJ-AUTO",
    "CIPLA", "SHRIRAMFIN", "TECHM", "UPL", "LTIM", "LTTS"
]

# Map to yfinance (NSE tickers usually end with '.NS')
def yf_symbol(nse_code: str) -> str:
    return f"{nse_code}.NS"


# ---------------------
# Indicators
# ---------------------
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(gain, index=series.index).rolling(length).mean()
    roll_down = pd.Series(loss, index=series.index).rolling(length).mean()
    rs = roll_up / (roll_down + 1e-9)
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    high = df['High']; low = df['Low']; close = df['Close']
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(length).mean()

def pivots_cpr(row):
    """Return Pivot, BC, TC, and width% for one row with High/Low/Close."""
    h, l, c = row['High'], row['Low'], row['Close']
    pivot = (h + l + c) / 3.0
    bc = (h + l) / 2.0
    tc = 2 * pivot - bc
    width = abs(tc - bc) / (pivot + 1e-9) * 100  # percent
    return pd.Series({'Pivot': pivot, 'BC': bc, 'TC': tc, 'CPR_WidthPct': width})


# ---------------------
# Setup rules
# ---------------------
@dataclass
class SetupFlags:
    nr7: bool
    inside_day: bool
    vol_surge: bool
    trend_long: bool
    trend_short: bool
    twenty_high_break: bool
    twenty_low_break: bool
    narrow_cpr: bool


def compute_setups(df: pd.DataFrame) -> pd.DataFrame:
    """
    df: MultiIndex columns if many tickers; else single ticker DataFrame.
    We'll handle both cases by iterating over tickers.
    """
    if isinstance(df.columns, pd.MultiIndex):
        tickers = sorted(set([c[1] for c in df.columns if c[0] == 'Close']))
    else:
        # This path is not expected since we request multiple tickers.
        tickers = ['SINGLE']

    rows = []
    for t in tickers:
        if t == 'SINGLE':
            sub = df.copy()
        else:
            sub = pd.DataFrame({
                'Open': df[('Open', t)],
                'High': df[('High', t)],
                'Low': df[('Low', t)],
                'Close': df[('Close', t)],
                'Volume': df[('Volume', t)],
            }).dropna()

        if sub.shape[0] < 30:
            continue  # not enough history

        # Indicators
        sub['EMA20'] = ema(sub['Close'], 20)
        sub['EMA50'] = ema(sub['Close'], 50)
        sub['RSI14'] = rsi(sub['Close'], 14)
        sub['ATR14'] = atr(sub, 14)
        sub[['Pivot', 'BC', 'TC', 'CPR_WidthPct']] = sub.apply(pivots_cpr, axis=1)

        # Helper columns
        sub['Range'] = sub['High'] - sub['Low']
        sub['VolAvg20'] = sub['Volume'].rolling(20).mean()
        sub['VolRatio'] = sub['Volume'] / (sub['VolAvg20'] + 1e-9)
        sub['TwentyDayHigh'] = sub['High'].rolling(20).max()
        sub['TwentyDayLow'] = sub['Low'].rolling(20).min()

        last = sub.iloc[-1]
        prev = sub.iloc[-2]

        # Setups
        nr7 = last['Range'] == sub['Range'].rolling(7).min().iloc[-1]
        inside_day = (last['High'] <= prev['High']) and (last['Low'] >= prev['Low'])
        vol_surge = last['VolRatio'] >= 1.3 and last['Volume'] > 1_000_000  # Liquidity + surge
        trend_long = (last['Close'] > last['EMA20'] > last['EMA50']) and (last['RSI14'] >= 55)
        trend_short = (last['Close'] < last['EMA20'] < last['EMA50']) and (last['RSI14'] <= 45)
        twenty_high_break = last['Close'] > prev['TwentyDayHigh']
        twenty_low_break = last['Close'] < prev['TwentyDayLow']
        narrow_cpr = last['CPR_WidthPct'] <= sub['CPR_WidthPct'].rolling(20).quantile(0.2).iloc[-1]

        flags = SetupFlags(
            nr7=bool(nr7),
            inside_day=bool(inside_day),
            vol_surge=bool(vol_surge),
            trend_long=bool(trend_long),
            trend_short=bool(trend_short),
            twenty_high_break=bool(twenty_high_break),
            twenty_low_break=bool(twenty_low_break),
            narrow_cpr=bool(narrow_cpr),
        )

        # Scoring (tune to taste)
        score_long = 0
        score_short = 0

        # Momentum continuation bias
        if flags.trend_long: score_long += 2
        if flags.trend_short: score_short += 2

        # Breakouts
        if flags.twenty_high_break: score_long += 2
        if flags.twenty_low_break: score_short += 2

        # Volatility contraction (NR7 + narrow CPR) as potential expansion
        if flags.nr7: score_long += 1; score_short += 1
        if flags.narrow_cpr: score_long += 1; score_short += 1

        # Volume confirmation
        if flags.vol_surge: score_long += 1; score_short += 1

        # Simple sentiment tilt from RSI
        if last['RSI14'] >= 60: score_long += 1
        if last['RSI14'] <= 40: score_short += 1

        # Build row
        rows.append({
            'Symbol': t.replace('.NS', ''),
            'Close': round(float(last['Close']), 2),
            'EMA20': round(float(last['EMA20']), 2),
            'EMA50': round(float(last['EMA50']), 2),
            'RSI14': round(float(last['RSI14']), 1),
            'ATR14': round(float(last['ATR14']), 2),
            'VolRatio': round(float(last['VolRatio']), 2),
            'CPR_WidthPct': round(float(last['CPR_WidthPct']), 2),
            'NR7': flags.nr7,
            'InsideDay': flags.inside_day,
            'VolSurge': flags.vol_surge,
            'TrendLong': flags.trend_long,
            'TrendShort': flags.trend_short,
            'HighBreak20': flags.twenty_high_break,
            'LowBreak20': flags.twenty_low_break,
            'NarrowCPR': flags.narrow_cpr,
            'ScoreLong': int(score_long),
            'ScoreShort': int(score_short),
        })

    return pd.DataFrame(rows)


def fetch_history(tickers: List[str], period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    # yfinance bulk download
    data = yf.download(tickers, period=period, interval=interval, auto_adjust=True, threads=True, progress=False)
    # Ensure consistent column order
    data = data[['Open','High','Low','Close','Volume']]
    return data.dropna(how='all')


def main():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = dt.datetime.now(ist)
    print(f"[INFO] Running EOD scan at {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Build yfinance tickers
    tickers = [yf_symbol(s) for s in NIFTY50]

    # Download last ~6 months daily bars
    print(f"[INFO] Fetching OHLCV for {len(tickers)} tickers...")
    df = fetch_history(tickers, period="6mo", interval="1d")
    if df.empty:
        raise SystemExit("No data fetched. Check your internet or ticker list.")

    print("[INFO] Computing setups...")
    results = compute_setups(df)
    if results.empty:
        raise SystemExit("No results computed. Possibly insufficient data.")

    # Rank
    long_cands = results.sort_values(["ScoreLong", "VolRatio"], ascending=[False, False]).head(20)
    short_cands = results.sort_values(["ScoreShort", "VolRatio"], ascending=[False, False]).head(20)

    # Save
    out_dir = "eod_scanner_output"
    os.makedirs(out_dir, exist_ok=True)
    date_tag = now_ist.strftime("%Y-%m-%d")
    long_path = os.path.join(out_dir, f"long_candidates_{date_tag}.csv")
    short_path = os.path.join(out_dir, f"short_candidates_{date_tag}.csv")
    all_path = os.path.join(out_dir, f"all_signals_{date_tag}.csv")

    results.to_csv(all_path, index=False)
    long_cands.to_csv(long_path, index=False)
    short_cands.to_csv(short_path, index=False)

    # Pretty print a small summary
    def format_list(df):
        rows = []
        for _, r in df.iterrows():
            notes = []
            if r['TrendLong']: notes.append("trend↑")
            if r['TrendShort']: notes.append("trend↓")
            if r['HighBreak20']: notes.append("20D↑")
            if r['LowBreak20']: notes.append("20D↓")
            if r['NR7']: notes.append("NR7")
            if r['InsideDay']: notes.append("Inside")
            if r['NarrowCPR']: notes.append("NarrowCPR")
            if r['VolSurge']: notes.append("Vol↑")
            rows.append(f"{r['Symbol']:>12} | ScoreL={r['ScoreLong']} ScoreS={r['ScoreShort']} | "
                        f"RSI={r['RSI14']:.1f} | ATR={r['ATR14']:.2f} | {'/'.join(notes)}")
        return "\n".join(rows)

    print("\n========== LONG CANDIDATES (Top 20) ==========")
    print(format_list(long_cands))
    print("\n========== SHORT CANDIDATES (Top 20) ==========")
    print(format_list(short_cands))

    print("\n[INFO] Files saved:")
    print(f" - {all_path}")
    print(f" - {long_path}")
    print(f" - {short_path}")

    print("\n[HINT] Next-day prep: For each candidate, pre-mark levels:")
    print(" - Yesterday High/Low, Pivot/BC/TC (CPR), and 20D High/Low")
    print(" - Plan entries on break/reject at these levels with risk defined by ATR (e.g., 0.5–1.0× ATR).")
    print(" - Avoid trades around major news/earnings or if liquidity is thin intraday.")


if __name__ == "__main__":
    main()
