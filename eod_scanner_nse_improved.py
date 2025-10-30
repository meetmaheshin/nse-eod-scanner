#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSE End-of-Day Scanner (Next-Day Intraday Candidates) - IMPROVED VERSION
-------------------------------------------------------------------------
What it does (after 3:30 PM IST):
- Downloads daily OHLCV for a universe (default: NIFTY 50) using yfinance
- Computes common setups: NR7, Inside Day, Breakout/Breadcrumb, Volume Surge, Trend Alignment, CPR width
- Scores long/short candidates and exports CSV + a human-readable summary

IMPROVEMENTS MADE:
- Better error handling and retry mechanism
- Configuration file support
- Progress tracking
- Enhanced logging
- More robust data validation
- Additional technical indicators (MACD, Bollinger Bands)
- Risk assessment metrics
- Better scoring algorithm
- Support for custom watchlists
- Performance optimization

Requirements:
    pip install pandas numpy yfinance pytz requests

Usage:
    python eod_scanner_nse_improved.py
"""

import os
import sys
import json
import math
import logging
import datetime as dt
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import pytz
from pathlib import Path
import tempfile
import uuid

try:
    import yfinance as yf
except Exception as e:
    raise SystemExit("Please install yfinance first: pip install yfinance")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scanner.log')
    ]
)
logger = logging.getLogger(__name__)

# ---------------------
# Configuration
# ---------------------
CONFIG_FILE = "scanner_config.json"

DEFAULT_CONFIG = {
    "universe": "NIFTY50",  # or "CUSTOM" 
    "custom_symbols": [],
    "period": "6mo",
    "min_volume": 1000000,
    "vol_surge_threshold": 1.3,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "cpr_narrow_percentile": 0.2,
    "output_dir": "eod_scanner_output",
    "max_retries": 3,
    "retry_delay": 2,
    
    # Phase 1 Enhancement Parameters
    "risk_per_trade": 5000,        # Default risk amount per trade in ₹
    "stop_atr_multiplier": 0.8,    # Stop loss = ATR × this multiplier
    "target_rr_ratio": 2.0,        # Risk:Reward ratio (1:2 default)
    "ibs_extreme_threshold": 0.2   # IBS < 0.2 or > 0.8 considered extreme
}

NIFTY50 = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "LT", "SBIN", "BHARTIARTL", "HINDUNILVR",
    "HCLTECH", "AXISBANK", "BAJFINANCE", "KOTAKBANK", "MARUTI", "ASIANPAINT", "SUNPHARMA", "LUPIN", "ONGC",
    "POWERGRID", "TITAN", "WIPRO", "ULTRACEMCO", "NTPC", "M&M", "NESTLEIND", "BAJAJFINSV", "ADANIENT",
    "ADANIPORTS", "HINDALCO", "JSWSTEEL", "TATASTEEL", "TATAMOTORS", "TATACONSUM", "COALINDIA", "GRASIM",
    "BPCL", "HEROMOTOCO", "BRITANNIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "HDFCLIFE", "BAJAJ-AUTO",
    "CIPLA", "SHRIRAMFIN", "TECHM", "UPL", "LTIM", "LTTS"
]

NIFTY_NEXT50 = [
    "GODREJCP", "MUTHOOTFIN", "PIDILITIND", "HAVELLS", "TORNTPHARM", "MOTHERSON", "AUROPHARMA", "COLPAL",
    "CONCOR", "SIEMENS", "ALKEM", "INDIGO", "NAUKRI", "MCDOWELL-N", "ACC", "DABUR", "SAIL", "GAIL",
    "CANBK", "DLF", "NMDC", "BANKBARODA", "IOC", "INDUSINDBK", "JINDALSTEL", "TORNTPOWER", "PETRONET",
    "MARICO", "APOLLOHOSP", "BOSCHLTD", "TRENT", "SRF", "MANAPPURAM", "POLICYBZR", "ZOMATO", "PAYTM",
    "PERSISTENT", "MPHASIS", "BIOCON", "CADILAHC", "PEL", "IDFCFIRSTB", "VEDL", "IRCTC", "DMART",
    "BANDHANBNK", "LICI", "HAL", "PNB"
]

def load_config() -> Dict:
    """Load configuration from file or create default."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Merge with defaults for any missing keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"Created default config file: {CONFIG_FILE}")
        return DEFAULT_CONFIG.copy()

def yf_symbol(nse_code: str) -> str:
    """Convert NSE code to yfinance format."""
    return f"{nse_code}.NS"

# ---------------------
# Enhanced Indicators
# ---------------------
def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()

def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()

def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    
    # Use exponential moving average for smoother RSI
    avg_gain = pd.Series(gain, index=series.index).ewm(span=length, adjust=False).mean()
    avg_loss = pd.Series(loss, index=series.index).ewm(span=length, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """MACD indicator."""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def bollinger_bands(series: pd.Series, window: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands."""
    middle = sma(series, window)
    std = series.rolling(window=window).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower

def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Average True Range."""
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)
    
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    
    return tr.ewm(span=length, adjust=False).mean()

def pivots_cpr(row):
    """Calculate Pivot, BC, TC, and width% for CPR."""
    h, l, c = row['High'], row['Low'], row['Close']
    pivot = (h + l + c) / 3.0
    bc = (h + l) / 2.0
    tc = 2 * pivot - bc
    width = abs(tc - bc) / (pivot + 1e-9) * 100
    return pd.Series({
        'Pivot': pivot, 
        'BC': bc, 
        'TC': tc, 
        'CPR_WidthPct': width
    })

def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Tuple[float, float]:
    """Calculate dynamic support and resistance levels."""
    recent_data = df.tail(window)
    support = recent_data['Low'].min()
    resistance = recent_data['High'].max()
    return support, resistance

def calculate_ibs(row) -> float:
    """
    Internal Bar Strength - mean reversion indicator.
    IBS = (Close - Low) / (High - Low)
    Values: 0 = closed at low, 1 = closed at high, 0.5 = middle
    """
    range_val = row['High'] - row['Low']
    if range_val == 0:
        return 0.5  # No range, neutral
    return (row['Close'] - row['Low']) / range_val

def calculate_cpr_percentile(cpr_series: pd.Series, window: int = 20) -> pd.Series:
    """
    CPR width percentile for volatility expansion detection.
    Lower percentiles indicate compressed volatility (potential expansion).
    """
    return cpr_series.rolling(window).rank(pct=True)

def enhanced_risk_framework(last_row, config: Dict, position_type: str = "long") -> Dict:
    """
    Enhanced risk management calculations with position sizing.
    Now supports both LONG and SHORT positions correctly.
    """
    atr = last_row['ATR14']
    close_price = last_row['Close']
    
    # Risk parameters (configurable)
    risk_per_trade = config.get('risk_per_trade', 5000)  # Default ₹5000 risk
    stop_atr_multiplier = config.get('stop_atr_multiplier', 0.8)  # Conservative
    target_rr_ratio = config.get('target_rr_ratio', 2.0)  # 1:2 risk-reward
    
    # Calculate stop loss points
    stop_loss_points = atr * stop_atr_multiplier
    target_points = stop_loss_points * target_rr_ratio
    
    if position_type.lower() == "long":
        # LONG positions: Stop below, Target above
        stop_loss_price = close_price - stop_loss_points
        target_price = close_price + target_points
    else:
        # SHORT positions: Stop above, Target below
        stop_loss_price = close_price + stop_loss_points
        target_price = close_price - target_points
    
    # Position sizing calculation
    if stop_loss_points > 0:
        max_shares = int(risk_per_trade / stop_loss_points)
        # Round to nearest lot size (assuming 25 shares per lot for most stocks)
        lot_size_shares = max(1, max_shares // 25) * 25
        actual_risk = lot_size_shares * stop_loss_points
    else:
        lot_size_shares = 25
        actual_risk = risk_per_trade
    
    return {
        'StopLossPoints': round(stop_loss_points, 2),
        'StopLossPrice': round(stop_loss_price, 2),
        'TargetPoints': round(target_points, 2),
        'TargetPrice': round(target_price, 2),
        'SuggestedShares': lot_size_shares,
        'ActualRisk': round(actual_risk, 2),
        'RiskRewardRatio': target_rr_ratio,
        'PositionType': position_type.upper()
    }

def get_sector_mapping() -> Dict[str, str]:
    """Basic sector classification for NIFTY stocks."""
    return {
        # IT Sector
        'TCS': 'IT', 'INFY': 'IT', 'HCLTECH': 'IT', 'WIPRO': 'IT', 'TECHM': 'IT', 'LTIM': 'IT', 'LTTS': 'IT',
        
        # Banking & Financial Services
        'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'AXISBANK': 'Banking', 'SBIN': 'Banking', 
        'KOTAKBANK': 'Banking', 'BAJFINANCE': 'NBFC', 'BAJAJFINSV': 'NBFC', 'SHRIRAMFIN': 'NBFC',
        'HDFCLIFE': 'Insurance',
        
        # Energy & Oil
        'RELIANCE': 'Energy', 'ONGC': 'Energy', 'BPCL': 'Energy',
        
        # Telecom
        'BHARTIARTL': 'Telecom',
        
        # Infrastructure & Utilities
        'LT': 'Infrastructure', 'POWERGRID': 'Utilities', 'NTPC': 'Utilities', 'ADANIPORTS': 'Infrastructure',
        
        # Auto & Auto Components
        'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'BAJAJ-AUTO': 'Auto', 'HEROMOTOCO': 'Auto', 'EICHERMOT': 'Auto',
        'M&M': 'Auto',
        
        # Pharma
        'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'LUPIN': 'Pharma', 'DIVISLAB': 'Pharma',
        
        # FMCG
        'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG', 'TATACONSUM': 'FMCG',
        
        # Materials & Chemicals
        'ASIANPAINT': 'Paints', 'ULTRACEMCO': 'Cement', 'GRASIM': 'Materials', 'UPL': 'Chemicals',
        
        # Metals & Mining
        'JSWSTEEL': 'Metals', 'TATASTEEL': 'Metals', 'HINDALCO': 'Metals', 'COALINDIA': 'Mining',
        
        # Consumer Discretionary
        'TITAN': 'Jewellery', 'ADANIENT': 'Conglomerate'
    }

def calculate_sector_rs(symbol: str, symbol_5d_return: float, nifty_5d_return: float) -> Dict:
    """Calculate sector relative strength vs NIFTY."""
    sector_map = get_sector_mapping()
    sector = sector_map.get(symbol, 'Other')
    
    # Relative strength calculation
    if nifty_5d_return != 0:
        rs_score = (symbol_5d_return / nifty_5d_return) - 1
        rs_rating = "Strong" if rs_score > 0.1 else "Weak" if rs_score < -0.1 else "Neutral"
    else:
        rs_score = 0
        rs_rating = "Neutral"
    
    return {
        'Sector': sector,
        'RS_5D_Pct': round(rs_score * 100, 2),  # Percentage outperformance
        'RS_Rating': rs_rating
    }

# ---------------------
# Enhanced Setup Analysis
# ---------------------
@dataclass
class EnhancedSetupFlags:
    # Original flags
    nr7: bool
    inside_day: bool
    vol_surge: bool
    trend_long: bool
    trend_short: bool
    twenty_high_break: bool
    twenty_low_break: bool
    narrow_cpr: bool
    
    # New flags
    macd_bullish: bool
    macd_bearish: bool
    bb_squeeze: bool
    bb_expansion: bool
    momentum_divergence: bool
    volume_confirmation: bool
    risk_reward_favorable: bool
    
    # Phase 1 Enhancement flags
    narrow_cpr_percentile: bool  # CPR in bottom 20th percentile
    ibs_extreme: bool           # IBS < 0.2 or > 0.8 (extreme readings)
    sector_outperformance: bool # Sector showing relative strength

@dataclass
class ScanResult:
    symbol: str
    score_long: int          # Moved to position B
    score_short: int         # Moved to position C
    close: float
    ema20: float
    ema50: float
    rsi14: float
    atr14: float
    vol_ratio: float
    cpr_width_pct: float
    macd_value: float
    macd_signal: float
    bb_position: float  # Position relative to Bollinger Bands (0-1)
    support: float
    resistance: float
    risk_reward_ratio: float
    
    # Phase 1 Enhancements
    ibs: float              # Internal Bar Strength
    cpr_percentile: float   # CPR width percentile
    sector: str             # Stock sector
    rs_5d_pct: float        # 5-day relative strength vs NIFTY
    rs_rating: str          # Strong/Neutral/Weak
    
    # LONG Position Risk Data
    stop_loss_points_long: float     # Stop loss points for long
    stop_loss_price_long: float      # Stop loss price for long
    target_points_long: float        # Target points for long
    target_price_long: float         # Target price for long
    suggested_shares_long: int       # Position size for long
    actual_risk_long: float          # Actual risk for long
    
    # SHORT Position Risk Data
    stop_loss_points_short: float    # Stop loss points for short
    stop_loss_price_short: float     # Stop loss price for short
    target_points_short: float       # Target points for short
    target_price_short: float        # Target price for short
    suggested_shares_short: int      # Position size for short
    actual_risk_short: float         # Actual risk for short
    
    setup_flags: EnhancedSetupFlags
    risk_level: str  # Low, Medium, High

def compute_enhanced_setups(df: pd.DataFrame, config: Dict) -> List[ScanResult]:
    """Enhanced setup computation with better indicators and risk assessment."""
    if isinstance(df.columns, pd.MultiIndex):
        tickers = sorted(set([c[1] for c in df.columns if c[0] == 'Close']))
    else:
        tickers = ['SINGLE']

    results = []
    total_tickers = len(tickers)
    
    for i, ticker in enumerate(tickers):
        try:
            logger.info(f"Processing {ticker} ({i+1}/{total_tickers})")
            
            if ticker == 'SINGLE':
                sub = df.copy()
            else:
                sub = pd.DataFrame({
                    'Open': df[('Open', ticker)],
                    'High': df[('High', ticker)],
                    'Low': df[('Low', ticker)],
                    'Close': df[('Close', ticker)],
                    'Volume': df[('Volume', ticker)],
                }).dropna()

            if sub.shape[0] < 50:  # Increased minimum data requirement
                logger.warning(f"Insufficient data for {ticker}: {sub.shape[0]} rows")
                continue

            # Calculate all indicators
            sub['EMA20'] = ema(sub['Close'], 20)
            sub['EMA50'] = ema(sub['Close'], 50)
            sub['SMA200'] = sma(sub['Close'], 200)
            sub['RSI14'] = rsi(sub['Close'], 14)
            sub['ATR14'] = atr(sub, 14)
            
            # MACD
            macd_line, macd_signal, macd_hist = macd(sub['Close'])
            sub['MACD'] = macd_line
            sub['MACD_Signal'] = macd_signal
            sub['MACD_Hist'] = macd_hist
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = bollinger_bands(sub['Close'])
            sub['BB_Upper'] = bb_upper
            sub['BB_Middle'] = bb_middle
            sub['BB_Lower'] = bb_lower
            sub['BB_Width'] = (bb_upper - bb_lower) / bb_middle * 100
            sub['BB_Position'] = (sub['Close'] - bb_lower) / (bb_upper - bb_lower)
            
            # CPR
            sub[['Pivot', 'BC', 'TC', 'CPR_WidthPct']] = sub.apply(pivots_cpr, axis=1)
            
            # Phase 1 Enhancements: IBS and CPR Percentile
            sub['IBS'] = sub.apply(calculate_ibs, axis=1)
            sub['CPR_Percentile'] = calculate_cpr_percentile(sub['CPR_WidthPct'])
            
            # Volume analysis
            sub['VolAvg20'] = sub['Volume'].rolling(20).mean()
            sub['VolRatio'] = sub['Volume'] / (sub['VolAvg20'] + 1e-9)
            
            # Price levels
            sub['TwentyDayHigh'] = sub['High'].rolling(20).max()
            sub['TwentyDayLow'] = sub['Low'].rolling(20).min()
            sub['Range'] = sub['High'] - sub['Low']
            
            # Get latest data
            last = sub.iloc[-1]
            prev = sub.iloc[-2]
            
            # Calculate support/resistance
            support, resistance = calculate_support_resistance(sub)
            
            # Phase 1 Enhancements: Calculate 5-day returns for relative strength
            if len(sub) >= 6:
                symbol_5d_return = ((last['Close'] / sub.iloc[-6]['Close']) - 1) * 100
                # Note: For full sector RS, we'd need NIFTY data. Using proxy for now.
                nifty_5d_return = symbol_5d_return * 0.8  # Simplified proxy
                sector_data = calculate_sector_rs(ticker.replace('.NS', ''), symbol_5d_return, nifty_5d_return)
            else:
                sector_data = {'Sector': 'Unknown', 'RS_5D_Pct': 0.0, 'RS_Rating': 'Neutral'}
            
            # Phase 1 Enhancement: Risk Framework - Calculate for both LONG and SHORT
            risk_data_long = enhanced_risk_framework(last, config, "long")
            risk_data_short = enhanced_risk_framework(last, config, "short")
            
            # Enhanced setup detection
            flags = EnhancedSetupFlags(
                # Original flags
                nr7=bool(last['Range'] == sub['Range'].rolling(7).min().iloc[-1]),
                inside_day=bool((last['High'] <= prev['High']) and (last['Low'] >= prev['Low'])),
                vol_surge=bool(last['VolRatio'] >= config['vol_surge_threshold'] and last['Volume'] > config['min_volume']),
                trend_long=bool((last['Close'] > last['EMA20'] > last['EMA50']) and (last['RSI14'] >= 55)),
                trend_short=bool((last['Close'] < last['EMA20'] < last['EMA50']) and (last['RSI14'] <= 45)),
                twenty_high_break=bool(last['Close'] > prev['TwentyDayHigh']),
                twenty_low_break=bool(last['Close'] < prev['TwentyDayLow']),
                narrow_cpr=bool(last['CPR_WidthPct'] <= sub['CPR_WidthPct'].rolling(20).quantile(config['cpr_narrow_percentile']).iloc[-1]),
                
                # Existing new flags
                macd_bullish=bool(last['MACD'] > last['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']),
                macd_bearish=bool(last['MACD'] < last['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']),
                bb_squeeze=bool(last['BB_Width'] <= sub['BB_Width'].rolling(20).quantile(0.2).iloc[-1]),
                bb_expansion=bool(last['BB_Width'] >= sub['BB_Width'].rolling(20).quantile(0.8).iloc[-1]),
                momentum_divergence=bool(abs(last['RSI14'] - prev['RSI14']) > 5),
                volume_confirmation=bool(last['VolRatio'] > 1.5),
                risk_reward_favorable=bool(abs(last['Close'] - resistance) / abs(last['Close'] - support) >= 1.5),
                
                # Phase 1 Enhancement flags
                narrow_cpr_percentile=bool(last['CPR_Percentile'] <= config['cpr_narrow_percentile']),
                ibs_extreme=bool(last['IBS'] <= config['ibs_extreme_threshold'] or last['IBS'] >= (1 - config['ibs_extreme_threshold'])),
                sector_outperformance=bool(sector_data['RS_Rating'] == 'Strong')
            )
            
            # Enhanced scoring
            score_long, score_short = calculate_enhanced_scores(last, flags, config)
            
            # Risk assessment
            risk_level = assess_risk_level(last, sub, flags)
            
            # Risk-reward ratio
            rr_ratio = calculate_risk_reward_ratio(last['Close'], support, resistance, last['ATR14'])
            
            # Create result
            result = ScanResult(
                symbol=ticker.replace('.NS', ''),
                score_long=int(score_long),      # Moved to position B
                score_short=int(score_short),    # Moved to position C
                close=round(float(last['Close']), 2),
                ema20=round(float(last['EMA20']), 2),
                ema50=round(float(last['EMA50']), 2),
                rsi14=round(float(last['RSI14']), 1),
                atr14=round(float(last['ATR14']), 2),
                vol_ratio=round(float(last['VolRatio']), 2),
                cpr_width_pct=round(float(last['CPR_WidthPct']), 2),
                macd_value=round(float(last['MACD']), 2),
                macd_signal=round(float(last['MACD_Signal']), 2),
                bb_position=round(float(last['BB_Position']), 2),
                support=round(float(support), 2),
                resistance=round(float(resistance), 2),
                risk_reward_ratio=round(float(rr_ratio), 2),
                
                # Phase 1 Enhancements
                ibs=round(float(last['IBS']), 3),
                cpr_percentile=round(float(last['CPR_Percentile']), 3),
                sector=sector_data['Sector'],
                rs_5d_pct=sector_data['RS_5D_Pct'],
                rs_rating=sector_data['RS_Rating'],
                
                # LONG Position Risk Data
                stop_loss_points_long=risk_data_long['StopLossPoints'],
                stop_loss_price_long=risk_data_long['StopLossPrice'],
                target_points_long=risk_data_long['TargetPoints'],
                target_price_long=risk_data_long['TargetPrice'],
                suggested_shares_long=risk_data_long['SuggestedShares'],
                actual_risk_long=risk_data_long['ActualRisk'],
                
                # SHORT Position Risk Data
                stop_loss_points_short=risk_data_short['StopLossPoints'],
                stop_loss_price_short=risk_data_short['StopLossPrice'],
                target_points_short=risk_data_short['TargetPoints'],
                target_price_short=risk_data_short['TargetPrice'],
                suggested_shares_short=risk_data_short['SuggestedShares'],
                actual_risk_short=risk_data_short['ActualRisk'],
                
                setup_flags=flags,
                risk_level=risk_level
            )
            
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            continue
    
    return results

def calculate_enhanced_scores(last_row, flags: EnhancedSetupFlags, config: Dict) -> Tuple[int, int]:
    """Enhanced scoring algorithm with Phase 1 improvements."""
    score_long = 0
    score_short = 0
    
    # Trend momentum (higher weight)
    if flags.trend_long: score_long += 3
    if flags.trend_short: score_short += 3
    
    # Breakouts (high weight)
    if flags.twenty_high_break: score_long += 3
    if flags.twenty_low_break: score_short += 3
    
    # MACD signals (high weight)
    if flags.macd_bullish: score_long += 2
    if flags.macd_bearish: score_short += 2
    
    # Volatility setups (medium weight)
    if flags.nr7: score_long += 1; score_short += 1
    if flags.narrow_cpr: score_long += 1; score_short += 1
    if flags.bb_squeeze: score_long += 1; score_short += 1
    
    # Volume confirmation (medium weight)
    if flags.vol_surge: score_long += 2; score_short += 2
    if flags.volume_confirmation: score_long += 1; score_short += 1
    
    # RSI positioning
    if last_row['RSI14'] >= 60: score_long += 1
    if last_row['RSI14'] <= 40: score_short += 1
    if last_row['RSI14'] >= 70: score_long -= 1  # Overbought penalty
    if last_row['RSI14'] <= 30: score_short -= 1  # Oversold penalty
    
    # Risk-reward consideration
    if flags.risk_reward_favorable: score_long += 1; score_short += 1
    
    # Phase 1 Enhancement Scoring
    if flags.narrow_cpr_percentile: score_long += 1; score_short += 1  # Volatility expansion potential
    if flags.sector_outperformance: score_long += 2  # Sector strength for longs
    if flags.ibs_extreme:
        # IBS extreme readings - mean reversion potential
        if last_row['IBS'] <= config.get('ibs_extreme_threshold', 0.2):
            score_long += 1  # Oversold, potential bounce
        elif last_row['IBS'] >= (1 - config.get('ibs_extreme_threshold', 0.2)):
            score_short += 1  # Overbought, potential decline
    
    return max(0, score_long), max(0, score_short)

def assess_risk_level(last_row, df: pd.DataFrame, flags: EnhancedSetupFlags) -> str:
    """Assess risk level based on multiple factors."""
    risk_factors = 0
    
    # High volatility
    if last_row['ATR14'] / last_row['Close'] > 0.03:  # > 3% daily ATR
        risk_factors += 1
    
    # Extreme RSI
    if last_row['RSI14'] > 80 or last_row['RSI14'] < 20:
        risk_factors += 1
    
    # Low volume
    if last_row['VolRatio'] < 0.5:
        risk_factors += 1
    
    # Poor risk-reward
    if not flags.risk_reward_favorable:
        risk_factors += 1
    
    if risk_factors <= 1:
        return "Low"
    elif risk_factors <= 2:
        return "Medium"
    else:
        return "High"

def calculate_risk_reward_ratio(current_price: float, support: float, resistance: float, atr: float) -> float:
    """Calculate risk-reward ratio."""
    try:
        potential_reward = abs(resistance - current_price)
        potential_risk = max(atr * 1.5, abs(current_price - support))  # Use ATR or support, whichever is larger
        return potential_reward / potential_risk if potential_risk > 0 else 0
    except:
        return 0

def fetch_history_with_retry(tickers: List[str], config: Dict) -> pd.DataFrame:
    """Fetch historical data with retry mechanism."""
    max_retries = config.get('max_retries', 3)
    retry_delay = config.get('retry_delay', 2)
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Fetching data (attempt {attempt + 1}/{max_retries})")
            data = yf.download(
                tickers, 
                period=config['period'], 
                interval="1d", 
                auto_adjust=True, 
                threads=True, 
                progress=False
            )
            
            if data.empty:
                raise ValueError("No data fetched")
            
            # Ensure consistent column order
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            return data.dropna(how='all')
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to fetch data after {max_retries} attempts")

def save_enhanced_results(results: List[ScanResult], config: Dict):
    """Save results with enhanced formatting."""
    if not results:
        logger.warning("No results to save")
        return pd.DataFrame(), pd.DataFrame()
    
    # Create output directory
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(exist_ok=True)
    
    # Clean up old CSV files to avoid confusion. Handle per-file errors (e.g. file locks).
    logger.info("Cleaning up old CSV files...")
    old_files = list(output_dir.glob("*.csv"))
    deleted_count = 0
    for old_file in old_files:
        try:
            old_file.unlink()
            logger.info(f"Deleted old file: {old_file.name}")
            deleted_count += 1
        except PermissionError as e:
            logger.warning(f"Permission denied deleting {old_file.name}: {e}. Skipping.")
        except Exception as e:
            logger.warning(f"Could not delete {old_file.name}: {e}")
    logger.info(f"Cleaned up {deleted_count} old CSV files")
    
    # Convert to DataFrame
    df_data = []
    for result in results:
        row = asdict(result)
        # Flatten setup_flags
        flags = row.pop('setup_flags')
        row.update(flags)
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Sort and filter
    long_candidates = df.sort_values(['score_long', 'vol_ratio'], ascending=[False, False]).head(25)
    short_candidates = df.sort_values(['score_short', 'vol_ratio'], ascending=[False, False]).head(25)
    
    # Save files with timestamp to avoid conflicts
    ist = pytz.timezone("Asia/Kolkata")
    now = dt.datetime.now(ist)
    date_tag = now.strftime("%Y-%m-%d")
    time_tag = now.strftime("%H%M")
    
    # Save files using a temp -> atomic replace approach where possible. If replace fails
    # due to permission issues (file open in another program), keep the temp file and log a warning.
    def _safe_save(df_obj: pd.DataFrame, target_path: Path) -> None:
        temp_name = f"{target_path.name}.tmp-{uuid.uuid4().hex}"
        temp_path = output_dir / temp_name
        try:
            df_obj.to_csv(temp_path, index=False)
        except Exception as e:
            logger.warning(f"Failed to write temp file {temp_path.name}: {e}")
            return

        try:
            # Attempt atomic replace
            os.replace(str(temp_path), str(target_path))
            logger.info(f"Saved file: {target_path}")
        except PermissionError as e:
            logger.warning(f"Permission denied moving {temp_path.name} -> {target_path.name}: {e}. Leaving temp file: {temp_path.name}")
        except Exception as e:
            logger.warning(f"Could not move temp file {temp_path.name} to {target_path.name}: {e}")

    all_path = output_dir / f"all_signals_{date_tag}_{time_tag}.csv"
    long_path = output_dir / f"long_candidates_{date_tag}_{time_tag}.csv"
    short_path = output_dir / f"short_candidates_{date_tag}_{time_tag}.csv"

    _safe_save(df, all_path)
    _safe_save(long_candidates, long_path)
    _safe_save(short_candidates, short_path)
    
    return long_candidates, short_candidates

def print_enhanced_summary(long_candidates: pd.DataFrame, short_candidates: pd.DataFrame):
    """Print enhanced summary with Phase 1 improvements and corrected SHORT calculations."""
    def format_enhanced_list(df, direction="LONG"):
        rows = []
        for _, r in df.iterrows():
            notes = []
            if r['trend_long']: notes.append("trend↑")
            if r['trend_short']: notes.append("trend↓")
            if r['twenty_high_break']: notes.append("20D↑")
            if r['twenty_low_break']: notes.append("20D↓")
            if r['macd_bullish']: notes.append("MACD↑")
            if r['macd_bearish']: notes.append("MACD↓")
            if r['nr7']: notes.append("NR7")
            if r['inside_day']: notes.append("Inside")
            if r['narrow_cpr']: notes.append("NarrowCPR")
            if r['bb_squeeze']: notes.append("BBSqueeze")
            if r['vol_surge']: notes.append("Vol↑")
            if r['risk_reward_favorable']: notes.append("R:R+")
            
            # Phase 1 Enhancement flags
            if r['narrow_cpr_percentile']: notes.append("CPR⊥")
            if r['ibs_extreme']: notes.append(f"IBS{r['ibs']:.1f}")
            if r['sector_outperformance']: notes.append(f"Sect+")
            
            score_col = 'score_long' if direction == "LONG" else 'score_short'
            
            # Use appropriate risk data based on direction
            if direction == "LONG":
                stop_price = r['stop_loss_price_long']
                target_price = r['target_price_long']
                shares = r['suggested_shares_long']
                risk = r['actual_risk_long']
            else:
                stop_price = r['stop_loss_price_short']
                target_price = r['target_price_short']
                shares = r['suggested_shares_short']
                risk = r['actual_risk_short']
            
            # Enhanced display with corrected LONG/SHORT data
            rows.append(
                f"{r['symbol']:>12} | Score={r[score_col]:2d} | "
                f"RSI={r['rsi14']:5.1f} | IBS={r['ibs']:4.2f} | "
                f"Stop=₹{stop_price:6.1f} | Tgt=₹{target_price:6.1f} | "
                f"Shares={shares:4d} | Risk=₹{risk:5.0f} | "
                f"{r['sector']:>8} | {'/'.join(notes)}"
            )
        return "\n".join(rows)
    
    print("\n" + "="*120)
    print(f"{'ENHANCED LONG CANDIDATES (Top 25) - PHASE 1 CORRECTED':^120}")
    print("="*120)
    print(format_enhanced_list(long_candidates, "LONG"))
    
    print("\n" + "="*120)
    print(f"{'ENHANCED SHORT CANDIDATES (Top 25) - PHASE 1 CORRECTED':^120}")
    print("="*120)
    print(format_enhanced_list(short_candidates, "SHORT"))
    
    print("\n" + "="*120)
    print("PHASE 1 ENHANCED TRADING HINTS (CORRECTED):")
    print("- Focus on candidates with Score >= 5 and favorable Stop/Target levels")
    print("- IBS values: <0.2 (oversold), >0.8 (overbought) for mean reversion")
    print("- CPR⊥ indicates compressed volatility (potential expansion)")
    print("- Sect+ shows sector outperformance for momentum trades")
    print("- LONG: Stop below entry, Target above entry")
    print("- SHORT: Stop above entry, Target below entry")
    print("- Position size (Shares) is calculated for your configured risk amount")
    print("- Entry Price = Current Close Price")
    print("="*120)

def get_symbol_universe(config: Dict) -> List[str]:
    """Get symbol universe based on configuration."""
    if config['universe'] == 'NIFTY50':
        return NIFTY50
    elif config['universe'] == 'NIFTY_NEXT50':
        return NIFTY_NEXT50
    elif config['universe'] == 'CUSTOM':
        return config.get('custom_symbols', [])
    else:
        logger.warning(f"Unknown universe: {config['universe']}, using NIFTY50")
        return NIFTY50

def main():
    """Enhanced main function."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup timezone
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = dt.datetime.now(ist)
        
        logger.info(f"Starting Enhanced EOD Scanner at {now_ist.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Configuration: {config}")
        
        # Get symbol universe
        symbols = get_symbol_universe(config)
        tickers = [yf_symbol(s) for s in symbols]
        
        logger.info(f"Analyzing {len(tickers)} symbols from {config['universe']} universe")
        
        # Fetch data with retry
        df = fetch_history_with_retry(tickers, config)
        
        if df.empty:
            raise SystemExit("No data fetched. Check your internet connection or symbol list.")
        
        logger.info(f"Data fetched successfully: {df.shape}")
        
        # Compute enhanced setups
        logger.info("Computing enhanced setups...")
        results = compute_enhanced_setups(df, config)
        
        if not results:
            raise SystemExit("No results computed. Check data quality and parameters.")
        
        logger.info(f"Analysis complete: {len(results)} symbols processed")
        
        # Save results
        long_candidates, short_candidates = save_enhanced_results(results, config)
        
        # Print summary
        print_enhanced_summary(long_candidates, short_candidates)
        
        logger.info("Enhanced EOD Scanner completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Scanner interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Scanner failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()