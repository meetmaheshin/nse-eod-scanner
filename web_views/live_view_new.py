"""Simple live web view for EOD scanner using Flask.

- Shows LONG and SHORT signals in separate dedicated views
- Auto-refreshes every 15 seconds with LIVE LTP data
- Implements price caching to avoid Yahoo Finance rate limits
- Minimal dependencies: Flask, pandas, yfinance

Run with: python live_view_new.py
"""
from flask import Flask, Response, render_template_string, jsonify
import time
import json
from pathlib import Path
import glob
import pandas as pd
import logging
import yfinance as yf
from datetime import datetime

# Path handling for both local and deployed environments
BASE_DIR = Path(__file__).parent.parent  # Go up from web_views/ to scanner/
OUTPUT_DIR = BASE_DIR / 'eod_scanner_output'
POLL_INTERVAL = 15  # seconds - increased to avoid Yahoo Finance rate limits

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('live_view')

# Cache for live prices to reduce API calls
price_cache = {}
last_fetch_time = 0
CACHE_DURATION = 10  # seconds - cache prices for 10 seconds


def find_latest_all_signals():
    files = sorted(OUTPUT_DIR.glob('all_signals_*.csv'))
    return files[-1] if files else None


def get_live_prices(symbols):
    """Fetch live prices for a list of symbols from Yahoo Finance with caching"""
    global price_cache, last_fetch_time
    
    current_time = time.time()
    
    # Return cached prices if still valid
    if current_time - last_fetch_time < CACHE_DURATION and price_cache:
        logger.info(f"Using cached prices ({len(price_cache)} symbols)")
        return price_cache
    
    live_prices = {}
    if not symbols:
        return live_prices
    
    try:
        # Add .NS suffix for NSE stocks
        yf_symbols = [f"{sym}.NS" for sym in symbols]
        # Batch fetch - limit to avoid rate limits
        batch_size = 10
        
        logger.info(f"Fetching live prices for {len(symbols)} symbols in batches of {batch_size}...")
        
        for i in range(0, len(yf_symbols), batch_size):
            batch = yf_symbols[i:i+batch_size]
            batch_symbols = symbols[i:i+batch_size]
            
            try:
                # Small delay between batches to avoid rate limiting
                if i > 0:
                    time.sleep(0.5)
                
                tickers = yf.Tickers(' '.join(batch))
                
                for j, sym in enumerate(batch_symbols):
                    try:
                        yf_sym = batch[j]
                        ticker = tickers.tickers[yf_sym]
                        info = ticker.fast_info
                        # Get the current price (last price)
                        if hasattr(info, 'last_price') and info.last_price:
                            live_prices[sym] = round(info.last_price, 2)
                        else:
                            live_prices[sym] = None
                    except Exception as e:
                        logger.debug(f"Could not fetch price for {sym}: {e}")
                        live_prices[sym] = None
            except Exception as e:
                logger.warning(f"Error fetching batch {i//batch_size + 1}: {e}")
                # Mark all symbols in this batch as None
                for sym in batch_symbols:
                    live_prices[sym] = None
                    
        successful_fetches = len([p for p in live_prices.values() if p is not None])
        logger.info(f"Fetched {successful_fetches}/{len(symbols)} live prices successfully")
        
        # Update cache
        price_cache = live_prices
        last_fetch_time = current_time
        
    except Exception as e:
        logger.error(f"Error fetching live prices: {e}")
    
    return live_prices


def build_payload():
    """Read latest CSV and return (payload_dict, mtime)"""
    latest = find_latest_all_signals()
    if latest is None:
        return ({'long': [], 'short': []}, None)
    try:
        mtime = latest.stat().st_mtime
        df = pd.read_csv(latest)
        # Include LTP column if it exists, otherwise use close as LTP
        cols = ['symbol', 'score_long', 'score_short', 'ltp', 'rsi14', 'ibs', 'sector']

        long_df = df.sort_values(['score_long', 'vol_ratio'] if 'vol_ratio' in df.columns else ['score_long'],
                                ascending=[False, False] if 'vol_ratio' in df.columns else [False]).head(25)
        short_df = df.sort_values(['score_short', 'vol_ratio'] if 'vol_ratio' in df.columns else ['score_short'],
                                 ascending=[False, False] if 'vol_ratio' in df.columns else [False]).head(25)

        # Get unique symbols for live price fetch
        all_symbols = list(set(long_df['symbol'].tolist() + short_df['symbol'].tolist()))
        logger.info(f"Fetching live prices for {len(all_symbols)} symbols...")
        live_prices = get_live_prices(all_symbols)
        logger.info(f"Fetched {len([p for p in live_prices.values() if p is not None])} live prices")

        long_rows = []
        for _, r in long_df.iterrows():
            row = {}
            symbol = r.get('symbol', '')
            for c in cols:
                if c == 'ltp':
                    # Priority: 1. Live price, 2. CSV ltp, 3. Close price
                    live_price = live_prices.get(symbol)
                    if live_price:
                        row[c] = live_price
                    elif 'ltp' in r and pd.notna(r['ltp']):
                        row[c] = r['ltp']
                    elif 'close' in r and pd.notna(r['close']):
                        row[c] = r['close']
                    else:
                        row[c] = ''
                else:
                    row[c] = r[c] if c in r and pd.notna(r[c]) else ''
            long_rows.append(row)

        short_rows = []
        for _, r in short_df.iterrows():
            row = {}
            symbol = r.get('symbol', '')
            for c in cols:
                if c == 'ltp':
                    # Priority: 1. Live price, 2. CSV ltp, 3. Close price
                    live_price = live_prices.get(symbol)
                    if live_price:
                        row[c] = live_price
                    elif 'ltp' in r and pd.notna(r['ltp']):
                        row[c] = r['ltp']
                    elif 'close' in r and pd.notna(r['close']):
                        row[c] = r['close']
                    else:
                        row[c] = ''
                else:
                    row[c] = r[c] if c in r and pd.notna(r[c]) else ''
            short_rows.append(row)

        payload = {'long': long_rows, 'short': short_rows}
        return (payload, mtime)
    except Exception as e:
        logger.error(f"build_payload error: {e}")
        return ({'long': [], 'short': []}, None)


@app.route('/latest')
def latest():
    payload, mtime = build_payload()
    meta = {'long_count': len(payload.get('long', [])), 'short_count': len(payload.get('short', []))}
    resp = {'payload': payload, 'meta': meta}
    logger.info(f"/latest called - long={meta['long_count']} short={meta['short_count']}")
    # Disable caching
    response = jsonify(resp)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# LONG VIEW TEMPLATE
LONG_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>LONG Signals - Live View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; 
               background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                  box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { margin: 0 0 10px 0; color: #28a745; font-size: 32px; }
        .status-bar { display: flex; align-items: center; gap: 15px; margin-top: 10px; }
        #status { padding: 8px 15px; background: #e8f5e9; border-radius: 5px; font-weight: bold; color: #2e7d32; }
        button { padding: 8px 20px; background: #28a745; color: white; border: none; border-radius: 5px; 
                 cursor: pointer; font-size: 14px; font-weight: bold; }
        button:hover { background: #218838; }
        .nav-links { margin-top: 10px; }
        .nav-links a { margin-right: 15px; color: #007bff; text-decoration: none; font-weight: bold; }
        .nav-links a:hover { text-decoration: underline; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { border: 1px solid #ddd; padding: 12px; font-size: 14px; text-align: left; }
        th { background: #28a745; color: white; font-weight: bold; }
        tbody tr:hover { background: #f1f9f1; }
        tbody tr:nth-child(even) { background: #f9f9f9; }
        .no-data { text-align: center; color: #666; padding: 40px; }
        .update-time { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 LONG Signals - Live View</h1>
        <div class="status-bar">
            <div id="status">Connecting...</div>
            <button id="refreshBtn">🔄 Refresh Now</button>
            <div class="update-time" id="updateTime">Last update: Never</div>
        </div>
        <div class="nav-links">
            <a href="/">📊 Combined View</a>
            <a href="/long">📈 Long Signals</a>
            <a href="/short">📉 Short Signals</a>
        </div>
        <div style="margin-top:10px; padding:8px; background:#fff3cd; border-radius:5px; font-size:12px;">
            ⚡ <strong>Live LTP:</strong> Prices update every 15 seconds from market data
        </div>
    </div>
    <div class="container">
        <h2 style="margin-top:0; color: #28a745;">Top Long Candidates</h2>
        <table>
            <thead>
                <tr><th>#</th><th>Symbol</th><th>Long Score</th><th>LTP</th><th>RSI</th><th>IBS</th><th>Sector</th></tr>
            </thead>
            <tbody id="tbody"></tbody>
        </table>
    </div>
    <script>
        const tbody = document.getElementById('tbody');
        const status = document.getElementById('status');
        const updateTime = document.getElementById('updateTime');

        function renderRows(rows) {
            tbody.innerHTML = '';
            if (!rows || rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="no-data">No long signals available</td></tr>';
                return;
            }
            rows.forEach((r, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td style="font-weight:bold">${r.symbol || ''}</td>
                    <td style="color:#28a745; font-weight:bold">${r.score_long || ''}</td>
                    <td style="font-weight:bold; color:#1976d2;">${r.ltp || ''}</td>
                    <td>${r.rsi14 || ''}</td>
                    <td>${r.ibs || ''}</td>
                    <td>${r.sector || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function fetchAndRender() {
            try {
                // Add timestamp to prevent caching
                const res = await fetch('/latest?t=' + Date.now());
                if (!res.ok) throw new Error('Network error');
                const json = await res.json();
                const longList = json.payload?.long || [];
                renderRows(longList);
                status.textContent = `✅ Connected (${longList.length} signals)`;
                updateTime.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
            } catch (e) {
                status.textContent = '❌ Connection error';
                updateTime.textContent = 'Last update: Error';
            }
        }

        document.getElementById('refreshBtn').addEventListener('click', fetchAndRender);
        fetchAndRender();
        setInterval(fetchAndRender, 15000) // 15 seconds;
    </script>
</body>
</html>
"""


# SHORT VIEW TEMPLATE
SHORT_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>SHORT Signals - Live View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; 
               background: linear-gradient(135deg, #c62828 0%, #d32f2f 100%); min-height: 100vh; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                  box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { margin: 0 0 10px 0; color: #dc3545; font-size: 32px; }
        .status-bar { display: flex; align-items: center; gap: 15px; margin-top: 10px; }
        #status { padding: 8px 15px; background: #ffebee; border-radius: 5px; font-weight: bold; color: #c62828; }
        button { padding: 8px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; 
                 cursor: pointer; font-size: 14px; font-weight: bold; }
        button:hover { background: #c82333; }
        .nav-links { margin-top: 10px; }
        .nav-links a { margin-right: 15px; color: #007bff; text-decoration: none; font-weight: bold; }
        .nav-links a:hover { text-decoration: underline; }
        .container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { border: 1px solid #ddd; padding: 12px; font-size: 14px; text-align: left; }
        th { background: #dc3545; color: white; font-weight: bold; }
        tbody tr:hover { background: #fff5f5; }
        tbody tr:nth-child(even) { background: #f9f9f9; }
        .no-data { text-align: center; color: #666; padding: 40px; }
        .update-time { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📉 SHORT Signals - Live View</h1>
        <div class="status-bar">
            <div id="status">Connecting...</div>
            <button id="refreshBtn">🔄 Refresh Now</button>
            <div class="update-time" id="updateTime">Last update: Never</div>
        </div>
        <div class="nav-links">
            <a href="/">📊 Combined View</a>
            <a href="/long">📈 Long Signals</a>
            <a href="/short">📉 Short Signals</a>
        </div>
        <div style="margin-top:10px; padding:8px; background:#fff3cd; border-radius:5px; font-size:12px;">
            ⚡ <strong>Live LTP:</strong> Prices update every 15 seconds from market data
        </div>
    </div>
    <div class="container">
        <h2 style="margin-top:0; color: #dc3545;">Top Short Candidates</h2>
        <table>
            <thead>
                <tr><th>#</th><th>Symbol</th><th>Short Score</th><th>LTP</th><th>RSI</th><th>IBS</th><th>Sector</th></tr>
            </thead>
            <tbody id="tbody"></tbody>
        </table>
    </div>
    <script>
        const tbody = document.getElementById('tbody');
        const status = document.getElementById('status');
        const updateTime = document.getElementById('updateTime');

        function renderRows(rows) {
            tbody.innerHTML = '';
            if (!rows || rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="no-data">No short signals available</td></tr>';
                return;
            }
            rows.forEach((r, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td style="font-weight:bold">${r.symbol || ''}</td>
                    <td style="color:#dc3545; font-weight:bold">${r.score_short || ''}</td>
                    <td style="font-weight:bold; color:#1976d2;">${r.ltp || ''}</td>
                    <td>${r.rsi14 || ''}</td>
                    <td>${r.ibs || ''}</td>
                    <td>${r.sector || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function fetchAndRender() {
            try {
                // Add timestamp to prevent caching
                const res = await fetch('/latest?t=' + Date.now());
                if (!res.ok) throw new Error('Network error');
                const json = await res.json();
                const shortList = json.payload?.short || [];
                renderRows(shortList);
                status.textContent = `✅ Connected (${shortList.length} signals)`;
                updateTime.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
            } catch (e) {
                status.textContent = '❌ Connection error';
                updateTime.textContent = 'Last update: Error';
            }
        }

        document.getElementById('refreshBtn').addEventListener('click', fetchAndRender);
        fetchAndRender();
        setInterval(fetchAndRender, 15000) // 15 seconds;
    </script>
</body>
</html>
"""


# COMBINED VIEW TEMPLATE
COMBINED_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>EOD Scanner - Combined View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; 
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                  box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { margin: 0 0 10px 0; color: #333; font-size: 28px; }
        .status-bar { display: flex; align-items: center; gap: 15px; margin-top: 10px; }
        #status { padding: 8px 15px; background: #e3f2fd; border-radius: 5px; font-weight: bold; color: #1976d2; }
        button { padding: 8px 20px; background: #667eea; color: white; border: none; border-radius: 5px; 
                 cursor: pointer; font-size: 14px; font-weight: bold; }
        button:hover { background: #5568d3; }
        .nav-links { margin-top: 10px; }
        .nav-links a { margin-right: 15px; color: #007bff; text-decoration: none; font-weight: bold; }
        .nav-links a:hover { text-decoration: underline; }
        .container { display: flex; gap: 20px; flex-wrap: wrap; }
        .panel { flex: 1; min-width: 400px; background: white; padding: 20px; border-radius: 10px; 
                 box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 10px; font-size: 13px; text-align: left; }
        th { font-weight: bold; }
        .panel:nth-child(1) th { background: #28a745; color: white; }
        .panel:nth-child(2) th { background: #dc3545; color: white; }
        tbody tr:hover { background: #f9f9f9; }
        tbody tr:nth-child(even) { background: #fafafa; }
        .panel h3 { margin-top: 0; }
        .update-time { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>📊 EOD Scanner - Combined Live View</h2>
        <div class="status-bar">
            <div id="status">Loading...</div>
            <button id="refreshBtn">🔄 Refresh Now</button>
            <div class="update-time" id="updateTime">Last update: Never</div>
        </div>
        <div class="nav-links">
            <a href="/">📊 Combined View</a>
            <a href="/long">📈 Long Signals</a>
            <a href="/short">📉 Short Signals</a>
        </div>
        <div style="margin-top:10px; padding:8px; background:#fff3cd; border-radius:5px; font-size:12px;">
            ⚡ <strong>Live LTP:</strong> Prices update every 15 seconds from market data
        </div>
    </div>
    <div class="container">
        <div class="panel">
            <h3 style="color:#28a745;">🚀 Long Candidates</h3>
            <table>
                <thead><tr><th>#</th><th>Symbol</th><th>ScoreL</th><th>LTP</th><th>RSI</th><th>IBS</th><th>Sector</th></tr></thead>
                <tbody id="longBody"></tbody>
            </table>
        </div>
        <div class="panel">
            <h3 style="color:#dc3545;">📉 Short Candidates</h3>
            <table>
                <thead><tr><th>#</th><th>Symbol</th><th>ScoreS</th><th>LTP</th><th>RSI</th><th>IBS</th><th>Sector</th></tr></thead>
                <tbody id="shortBody"></tbody>
            </table>
        </div>
    </div>
    <script>
        const longBody = document.getElementById('longBody');
        const shortBody = document.getElementById('shortBody');
        const status = document.getElementById('status');
        const updateTime = document.getElementById('updateTime');

        function renderRows(body, rows, scoreKey) {
            body.innerHTML = '';
            if (!rows || rows.length === 0) {
                body.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#666;">No data</td></tr>';
                return;
            }
            rows.forEach((r, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td style="font-weight:bold">${r.symbol || ''}</td>
                    <td>${r[scoreKey] || ''}</td>
                    <td style="font-weight:bold; color:#1976d2;">${r.ltp || ''}</td>
                    <td>${r.rsi14 || ''}</td>
                    <td>${r.ibs || ''}</td>
                    <td>${r.sector || ''}</td>
                `;
                body.appendChild(tr);
            });
        }

        async function fetchAndRender() {
            try {
                // Add timestamp to prevent caching
                const res = await fetch('/latest?t=' + Date.now());
                const json = await res.json();
                const payload = json.payload || { long: [], short: [] };
                renderRows(longBody, payload.long, 'score_long');
                renderRows(shortBody, payload.short, 'score_short');
                status.textContent = `✅ Updated: Long=${payload.long.length} Short=${payload.short.length}`;
                updateTime.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
            } catch (e) {
                status.textContent = '❌ Error fetching data';
                updateTime.textContent = 'Last update: Error';
            }
        }

        document.getElementById('refreshBtn').addEventListener('click', fetchAndRender);
        fetchAndRender();
        setInterval(fetchAndRender, 15000) // 15 seconds;
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    logger.info("/ index requested - serving combined view")
    return render_template_string(COMBINED_TEMPLATE)


@app.route('/long')
def long_view():
    logger.info('/long view requested')
    return render_template_string(LONG_TEMPLATE)


@app.route('/short')
def short_view():
    logger.info('/short view requested')
    return render_template_string(SHORT_TEMPLATE)


if __name__ == '__main__':
    logger.info("Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
