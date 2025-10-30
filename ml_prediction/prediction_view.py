"""Live Prediction View - ML-Based Tomorrow's Forecast

Flask web interface showing:
- Today's signals (current view)
- Tomorrow's ML predictions with confidence scores
- Side-by-side comparison

Run with: python prediction_view.py
"""
from flask import Flask, render_template_string, jsonify, Response
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# Import prediction engine
from prediction_engine import PredictionEngine

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('prediction_view')

OUTPUT_DIR = Path('eod_scanner_output')
POLL_INTERVAL = 15  # seconds

# Initialize prediction engine
prediction_engine = PredictionEngine()
if not prediction_engine.load_model():
    logger.warning("⚠️  No ML model found. Predictions will be limited.")
    logger.warning("    Run 'python prediction_engine.py' first to train the model.")


def find_latest_all_signals():
    """Find the most recent all_signals CSV file."""
    files = sorted(OUTPUT_DIR.glob('all_signals_*.csv'))
    return files[-1] if files else None


def build_payload():
    """Build data payload with both current signals and predictions"""
    csv_path = find_latest_all_signals()
    if not csv_path:
        return {
            'long_rows': [],
            'short_rows': [],
            'predicted_long': [],
            'predicted_short': [],
            'last_update': 'No data',
            'model_available': False
        }
    
    df = pd.read_csv(csv_path)
    timestamp = datetime.fromtimestamp(csv_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    # Current signals (existing logic)
    cols = ['symbol', 'score_long', 'score_short', 'ltp', 'rsi14', 'ibs', 'sector']
    
    # LONG candidates
    long_df = df.sort_values('score_long', ascending=False).head(25)
    long_rows = []
    for _, r in long_df.iterrows():
        row = {}
        for c in cols:
            if c == 'ltp':
                if 'close' in r and pd.notna(r['close']):
                    row[c] = r['close']
                else:
                    row[c] = ''
            else:
                row[c] = r[c] if c in r and pd.notna(r[c]) else ''
        long_rows.append(row)
    
    # SHORT candidates
    short_df = df.sort_values('score_short', ascending=False).head(25)
    short_rows = []
    for _, r in short_df.iterrows():
        row = {}
        for c in cols:
            if c == 'ltp':
                if 'close' in r and pd.notna(r['close']):
                    row[c] = r['close']
                else:
                    row[c] = ''
            else:
                row[c] = r[c] if c in r and pd.notna(r[c]) else ''
        short_rows.append(row)
    
    # ML Predictions
    predicted_long = []
    predicted_short = []
    model_available = False
    
    if prediction_engine.model is not None:
        try:
            predictions = prediction_engine.predict_tomorrow(csv_path)
            model_available = True
            
            pred_cols = ['symbol', 'prediction_score', 'recommendation', 
                        'expected_return_pct', 'score_long', 'score_short',
                        'ltp', 'rsi14', 'ibs', 'sector']
            
            # Predicted LONG (high confidence + score_long > score_short)
            pred_long_df = predictions[
                (predictions['confidence_profit'] >= 0.6) & 
                (predictions['score_long'] >= predictions['score_short'])
            ].sort_values('prediction_score', ascending=False).head(25)
            
            for _, r in pred_long_df.iterrows():
                row = {}
                for c in pred_cols:
                    if c == 'ltp':
                        row[c] = r.get('close', '')
                    else:
                        row[c] = r.get(c, '')
                predicted_long.append(row)
            
            # Predicted SHORT (high confidence + score_short > score_long)
            pred_short_df = predictions[
                (predictions['confidence_profit'] >= 0.6) & 
                (predictions['score_short'] >= predictions['score_long'])
            ].sort_values('prediction_score', ascending=False).head(25)
            
            for _, r in pred_short_df.iterrows():
                row = {}
                for c in pred_cols:
                    if c == 'ltp':
                        row[c] = r.get('close', '')
                    else:
                        row[c] = r.get(c, '')
                predicted_short.append(row)
                
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
    
    return {
        'long_rows': long_rows,
        'short_rows': short_rows,
        'predicted_long': predicted_long,
        'predicted_short': predicted_short,
        'last_update': timestamp,
        'model_available': model_available
    }


# HTML Template for Prediction View
PREDICTION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tomorrow's Predictions - ML Forecast</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 1800px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 20px;
            opacity: 0.9;
        }
        .nav-links {
            text-align: center;
            margin-bottom: 20px;
        }
        .nav-links a {
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            margin: 0 5px;
            display: inline-block;
            transition: background 0.3s;
        }
        .nav-links a:hover { background: rgba(255,255,255,0.3); }
        .info-banner {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .model-status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }
        .model-active { background: #10b981; }
        .model-inactive { background: #ef4444; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .section {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }
        .today-section .section-header { color: #4f46e5; border-color: #4f46e5; }
        .prediction-section .section-header { color: #059669; border-color: #059669; }
        .long-section .section-header { color: #10b981; border-color: #10b981; }
        .short-section .section-header { color: #ef4444; border-color: #ef4444; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        th {
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }
        tbody tr {
            border-bottom: 1px solid #e5e7eb;
            color: #1f2937;
        }
        tbody tr:hover { background: #f3f4f6; }
        td {
            padding: 10px 8px;
        }
        .symbol { font-weight: bold; color: #1f2937; }
        .score { font-weight: bold; font-size: 1.1rem; }
        .score-high { color: #059669; }
        .score-med { color: #d97706; }
        .score-low { color: #dc2626; }
        .prediction-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
        }
        .badge-strong-buy { background: #059669; }
        .badge-buy { background: #10b981; }
        .badge-hold { background: #f59e0b; }
        .badge-avoid { background: #ef4444; }
        .confidence {
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .conf-high { background: #d1fae5; color: #065f46; }
        .conf-med { background: #fed7aa; color: #92400e; }
        .conf-low { background: #fee2e2; color: #991b1b; }
        .update-time {
            text-align: center;
            margin-top: 15px;
            font-size: 0.9rem;
            color: #6b7280;
        }
        .refresh-btn {
            background: #4f46e5;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            margin: 10px 0;
        }
        .refresh-btn:hover { background: #4338ca; }
        @media (max-width: 1200px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 Tomorrow's Stock Predictions</h1>
        <p class="subtitle">ML-Powered Forecast vs Today's Signals</p>
        
        <div class="nav-links">
            <a href="/">📊 Combined View</a>
            <a href="/long">🟢 Long Only</a>
            <a href="/short">🔴 Short Only</a>
            <a href="/predictions">🔮 Predictions (Current)</a>
        </div>
        
        <div class="info-banner">
            <div id="modelStatus" class="model-status">
                ⏳ Loading model status...
            </div>
            <div style="margin-top:10px;">
                ⏱️ <strong>Updates:</strong> Page refreshes every 15 seconds
            </div>
            <button class="refresh-btn" id="refreshBtn">🔄 Refresh Now</button>
        </div>
        
        <div class="grid">
            <!-- Today's Long Signals -->
            <div class="section today-section">
                <div class="section-header">📈 TODAY'S LONG SIGNALS</div>
                <table id="todayLongTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Score</th>
                            <th>Price</th>
                            <th>RSI</th>
                            <th>IBS</th>
                            <th>Sector</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <!-- Tomorrow's Predicted Long -->
            <div class="section prediction-section long-section">
                <div class="section-header">🎯 TOMORROW'S PREDICTED LONG</div>
                <table id="predLongTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Confidence</th>
                            <th>Action</th>
                            <th>Expected</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <!-- Today's Short Signals -->
            <div class="section today-section">
                <div class="section-header">📉 TODAY'S SHORT SIGNALS</div>
                <table id="todayShortTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Score</th>
                            <th>Price</th>
                            <th>RSI</th>
                            <th>IBS</th>
                            <th>Sector</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <!-- Tomorrow's Predicted Short -->
            <div class="section prediction-section short-section">
                <div class="section-header">🎯 TOMORROW'S PREDICTED SHORT</div>
                <table id="predShortTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Confidence</th>
                            <th>Action</th>
                            <th>Expected</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div class="update-time" id="updateTime">Last update: --</div>
    </div>
    
    <script>
        function getScoreClass(score) {
            if (score >= 8) return 'score-high';
            if (score >= 5) return 'score-med';
            return 'score-low';
        }
        
        function getConfidenceClass(conf) {
            if (conf >= 75) return 'conf-high';
            if (conf >= 60) return 'conf-med';
            return 'conf-low';
        }
        
        function getBadgeClass(rec) {
            if (rec === 'STRONG BUY') return 'badge-strong-buy';
            if (rec === 'BUY') return 'badge-buy';
            if (rec === 'HOLD') return 'badge-hold';
            return 'badge-avoid';
        }
        
        function renderTodayLong(data) {
            const tbody = document.querySelector('#todayLongTable tbody');
            tbody.innerHTML = '';
            
            data.forEach((row, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td class="symbol">${row.symbol || ''}</td>
                    <td class="score ${getScoreClass(row.score_long)}">${row.score_long || 0}</td>
                    <td>${row.ltp || ''}</td>
                    <td>${row.rsi14 ? row.rsi14.toFixed(1) : ''}</td>
                    <td>${row.ibs ? row.ibs.toFixed(2) : ''}</td>
                    <td>${row.sector || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function renderPredictedLong(data) {
            const tbody = document.querySelector('#predLongTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No predictions available</td></tr>';
                return;
            }
            
            data.forEach((row, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td class="symbol">${row.symbol || ''}</td>
                    <td><span class="confidence ${getConfidenceClass(row.prediction_score)}">${row.prediction_score?.toFixed(1) || 0}%</span></td>
                    <td><span class="prediction-badge ${getBadgeClass(row.recommendation)}">${row.recommendation || 'N/A'}</span></td>
                    <td style="color:#059669; font-weight:bold;">+${row.expected_return_pct?.toFixed(2) || 0}%</td>
                    <td class="score ${getScoreClass(row.score_long)}">${row.score_long || 0}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function renderTodayShort(data) {
            const tbody = document.querySelector('#todayShortTable tbody');
            tbody.innerHTML = '';
            
            data.forEach((row, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td class="symbol">${row.symbol || ''}</td>
                    <td class="score ${getScoreClass(row.score_short)}">${row.score_short || 0}</td>
                    <td>${row.ltp || ''}</td>
                    <td>${row.rsi14 ? row.rsi14.toFixed(1) : ''}</td>
                    <td>${row.ibs ? row.ibs.toFixed(2) : ''}</td>
                    <td>${row.sector || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        function renderPredictedShort(data) {
            const tbody = document.querySelector('#predShortTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No predictions available</td></tr>';
                return;
            }
            
            data.forEach((row, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${idx + 1}</td>
                    <td class="symbol">${row.symbol || ''}</td>
                    <td><span class="confidence ${getConfidenceClass(row.prediction_score)}">${row.prediction_score?.toFixed(1) || 0}%</span></td>
                    <td><span class="prediction-badge ${getBadgeClass(row.recommendation)}">${row.recommendation || 'N/A'}</span></td>
                    <td style="color:#059669; font-weight:bold;">+${row.expected_return_pct?.toFixed(2) || 0}%</td>
                    <td class="score ${getScoreClass(row.score_short)}">${row.score_short || 0}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        async function fetchAndRender() {
            try {
                const response = await fetch('/api/predictions?t=' + Date.now());
                const data = await response.json();
                
                renderTodayLong(data.long_rows || []);
                renderTodayShort(data.short_rows || []);
                renderPredictedLong(data.predicted_long || []);
                renderPredictedShort(data.predicted_short || []);
                
                // Update model status
                const statusDiv = document.getElementById('modelStatus');
                if (data.model_available) {
                    statusDiv.className = 'model-status model-active';
                    statusDiv.innerHTML = '✅ ML Model Active - Predictions Enabled';
                } else {
                    statusDiv.className = 'model-status model-inactive';
                    statusDiv.innerHTML = '⚠️ ML Model Not Trained - Run prediction_engine.py first';
                }
                
                document.getElementById('updateTime').textContent = 
                    'Last update: ' + (data.last_update || 'Unknown');
            } catch (err) {
                console.error('Fetch error:', err);
                document.getElementById('updateTime').textContent = 'Last update: Error';
            }
        }
        
        document.getElementById('refreshBtn').addEventListener('click', fetchAndRender);
        fetchAndRender();
        setInterval(fetchAndRender, 15000); // 15 seconds
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Show prediction comparison view"""
    return render_template_string(PREDICTION_TEMPLATE)


@app.route('/predictions')
def predictions_view():
    """Alias for main view"""
    return render_template_string(PREDICTION_TEMPLATE)


@app.route('/api/predictions')
def api_predictions():
    """API endpoint for prediction data"""
    payload = build_payload()
    
    resp = jsonify(payload)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    
    return resp


@app.route('/long')
def long_only():
    """Redirect to live_view_new.py long view"""
    from flask import redirect
    return redirect('http://127.0.0.1:5000/long')


@app.route('/short')
def short_only():
    """Redirect to live_view_new.py short view"""
    from flask import redirect
    return redirect('http://127.0.0.1:5000/short')


if __name__ == '__main__':
    logger.info("Starting Prediction View server on port 5001...")
    logger.info("Access at: http://127.0.0.1:5001/")
    logger.info("Make sure live_view_new.py is also running on port 5000")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
