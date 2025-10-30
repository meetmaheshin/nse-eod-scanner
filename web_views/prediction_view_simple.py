"""
SIMPLE Prediction View - No ML Required!
Shows today's signals as "tomorrow's predictions" based on scanner scores.
Once you have more data, upgrade to full ML version.

Version: 1.1 - High Confidence threshold updated to 60%

Run: python prediction_view_simple.py
"""
from flask import Flask, render_template_string, jsonify
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('simple_predictions')

OUTPUT_DIR = Path('eod_scanner_output')

def find_latest_signals():
    """Find latest signal file"""
    files = sorted(OUTPUT_DIR.glob('all_signals_*.csv'))
    return files[-1] if files else None

def generate_simple_predictions():
    """Generate predictions based on scanner scores (no ML needed)"""
    csv_path = find_latest_signals()
    if not csv_path:
        return {
            'predictions': [],
            'last_update': 'No data',
            'prediction_date': 'N/A'
        }
    
    df = pd.read_csv(csv_path)
    timestamp = datetime.fromtimestamp(csv_path.stat().st_mtime)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Simple prediction logic based on scores
    predictions = []
    
    for _, row in df.iterrows():
        # Calculate confidence based on score
        long_score = row.get('score_long', 0)
        short_score = row.get('score_short', 0)
        
        # Predict direction based on higher score
        if long_score > short_score:
            direction = 'LONG'
            confidence = min(95, long_score * 10 + 20)  # Scale to 0-100%
            expected_return = round(long_score * 0.3, 2)  # Rough estimate
        elif short_score > long_score:
            direction = 'SHORT'
            confidence = min(95, short_score * 10 + 20)
            expected_return = round(short_score * 0.3, 2)
        else:
            direction = 'NEUTRAL'
            confidence = max(20, max(long_score, short_score) * 10)  # At least use the score
            expected_return = 0
        
        # Recommendation based on confidence
        if confidence >= 75:
            recommendation = 'STRONG BUY' if direction == 'LONG' else 'STRONG SELL'
        elif confidence >= 60:
            recommendation = 'BUY' if direction == 'LONG' else 'SELL'
        elif confidence >= 50:
            recommendation = 'HOLD'
        else:
            recommendation = 'AVOID'
        
        predictions.append({
            'symbol': row.get('symbol', ''),
            'direction': direction,
            'confidence': confidence,
            'recommendation': recommendation,
            'expected_return': expected_return,
            'score_long': long_score,
            'score_short': short_score,
            'ltp': row.get('close', 0),
            'rsi14': row.get('rsi14', 0),
            'ibs': row.get('ibs', 0),
            'sector': row.get('sector', ''),
            'risk_level': row.get('risk_level', 'Medium')
        })
    
    # Sort by confidence
    predictions.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'predictions': predictions,
        'last_update': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'prediction_date': tomorrow
    }


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tomorrow's Predictions</title>
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
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
        .prediction-date {
            text-align: center;
            font-size: 1.5rem;
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
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
        }
        .nav-links a:hover { background: rgba(255,255,255,0.3); }
        .info-box {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }
        .tab {
            padding: 15px 30px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px 10px 0 0;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: bold;
        }
        .tab.active { background: rgba(255,255,255,0.95); color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .section {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
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
        td { padding: 10px 8px; }
        .symbol { font-weight: bold; font-size: 1.1rem; }
        .badge {
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 0.85rem;
            font-weight: bold;
            color: white;
            display: inline-block;
        }
        .badge-strong-buy { background: #059669; }
        .badge-buy { background: #10b981; }
        .badge-strong-sell { background: #dc2626; }
        .badge-sell { background: #ef4444; }
        .badge-hold { background: #f59e0b; }
        .badge-avoid { background: #6b7280; }
        .confidence {
            font-weight: bold;
            font-size: 1.1rem;
        }
        .conf-high { color: #059669; }
        .conf-med { color: #f59e0b; }
        .conf-low { color: #dc2626; }
        .direction-long { color: #059669; font-weight: bold; }
        .direction-short { color: #dc2626; font-weight: bold; }
        .expected-return {
            font-weight: bold;
            color: #059669;
        }
        .update-time {
            text-align: center;
            margin-top: 20px;
            color: #6b7280;
        }
        .refresh-btn {
            background: #4f46e5;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            display: block;
            margin: 20px auto;
        }
        .refresh-btn:hover { background: #4338ca; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 Tomorrow's Stock Predictions</h1>
        <p class="subtitle">Score-Based Forecast System</p>
        
        <div class="prediction-date" id="predictionDate">
            📅 Predictions for: <span id="tomorrowDate">Loading...</span>
        </div>
        
        <div class="nav-links">
            <a href="http://127.0.0.1:5000/">📊 Today's Signals</a>
            <a href="http://127.0.0.1:5000/long">🟢 Long View</a>
            <a href="http://127.0.0.1:5000/short">🔴 Short View</a>
        </div>
        
        <div class="info-box">
            <div style="text-align:center;">
                ℹ️ <strong>How it works:</strong> Predictions based on scanner scores and technical indicators.<br>
                Higher confidence = stronger signal. Always use stop losses!
            </div>
            <button class="refresh-btn" id="refreshBtn">🔄 Refresh Predictions</button>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('all')">📊 All Predictions</div>
            <div class="tab" onclick="showTab('long')">🟢 Long Only</div>
            <div class="tab" onclick="showTab('short')">🔴 Short Only</div>
            <div class="tab" onclick="showTab('high-conf')">⭐ High Confidence (60%+)</div>
        </div>
        
        <div id="allTab" class="tab-content active">
            <div class="section">
                <table id="allTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Direction</th>
                            <th>Confidence</th>
                            <th>Recommendation</th>
                            <th>Expected Return</th>
                            <th>Score (L/S)</th>
                            <th>Price</th>
                            <th>RSI</th>
                            <th>Risk</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="longTab" class="tab-content">
            <div class="section">
                <table id="longTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Confidence</th>
                            <th>Recommendation</th>
                            <th>Expected Return</th>
                            <th>Score</th>
                            <th>Price</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="shortTab" class="tab-content">
            <div class="section">
                <table id="shortTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Confidence</th>
                            <th>Recommendation</th>
                            <th>Expected Return</th>
                            <th>Score</th>
                            <th>Price</th>
                            <th>RSI</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div id="highConfTab" class="tab-content">
            <div class="section">
                <table id="highConfTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Symbol</th>
                            <th>Direction</th>
                            <th>Confidence</th>
                            <th>Recommendation</th>
                            <th>Expected Return</th>
                            <th>Score (L/S)</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
        
        <div class="update-time" id="updateTime">Last update: --</div>
    </div>
    
    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + 'Tab').classList.add('active');
        }
        
        function getConfClass(conf) {
            if (conf >= 75) return 'conf-high';
            if (conf >= 60) return 'conf-med';
            return 'conf-low';
        }
        
        function getBadgeClass(rec) {
            const classes = {
                'STRONG BUY': 'badge-strong-buy',
                'BUY': 'badge-buy',
                'STRONG SELL': 'badge-strong-sell',
                'SELL': 'badge-sell',
                'HOLD': 'badge-hold',
                'AVOID': 'badge-avoid'
            };
            return classes[rec] || 'badge-hold';
        }
        
        function renderTable(tableId, data, columns) {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = '';
            
            data.forEach((row, idx) => {
                const tr = document.createElement('tr');
                let html = `<td>${idx + 1}</td>`;
                
                if (columns.includes('symbol')) html += `<td class="symbol">${row.symbol}</td>`;
                if (columns.includes('direction')) html += `<td class="direction-${row.direction.toLowerCase()}">${row.direction}</td>`;
                if (columns.includes('confidence')) html += `<td class="confidence ${getConfClass(row.confidence)}">${row.confidence.toFixed(0)}%</td>`;
                if (columns.includes('recommendation')) html += `<td><span class="badge ${getBadgeClass(row.recommendation)}">${row.recommendation}</span></td>`;
                if (columns.includes('expected_return')) html += `<td class="expected-return">+${row.expected_return}%</td>`;
                if (columns.includes('scores')) html += `<td>${row.score_long}/${row.score_short}</td>`;
                if (columns.includes('score_long')) html += `<td>${row.score_long}</td>`;
                if (columns.includes('price')) html += `<td>₹${row.ltp.toFixed(2)}</td>`;
                if (columns.includes('rsi')) html += `<td>${row.rsi14.toFixed(1)}</td>`;
                if (columns.includes('risk')) html += `<td>${row.risk_level}</td>`;
                
                tr.innerHTML = html;
                tbody.appendChild(tr);
            });
        }
        
        async function fetchAndRender() {
            try {
                const response = await fetch('/api/predictions?t=' + Date.now());
                const data = await response.json();
                
                const predictions = data.predictions || [];
                
                // All predictions
                renderTable('allTable', predictions, 
                    ['symbol', 'direction', 'confidence', 'recommendation', 'expected_return', 'scores', 'price', 'rsi', 'risk']);
                
                // Long only
                const longPreds = predictions.filter(p => p.direction === 'LONG');
                renderTable('longTable', longPreds,
                    ['symbol', 'confidence', 'recommendation', 'expected_return', 'score_long', 'price', 'rsi']);
                
                // Short only
                const shortPreds = predictions.filter(p => p.direction === 'SHORT');
                renderTable('shortTable', shortPreds,
                    ['symbol', 'confidence', 'recommendation', 'expected_return', 'score_long', 'price', 'rsi']);
                
                // High confidence only (60% threshold - anything above average)
                const highConf = predictions.filter(p => p.confidence >= 60);
                renderTable('highConfTable', highConf,
                    ['symbol', 'direction', 'confidence', 'recommendation', 'expected_return', 'scores']);
                
                document.getElementById('tomorrowDate').textContent = data.prediction_date;
                document.getElementById('updateTime').textContent = 'Last update: ' + data.last_update;
                
            } catch (err) {
                console.error('Fetch error:', err);
            }
        }
        
        document.getElementById('refreshBtn').addEventListener('click', fetchAndRender);
        fetchAndRender();
        setInterval(fetchAndRender, 30000); // 30 seconds
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/api/predictions')
def api_predictions():
    data = generate_simple_predictions()
    resp = jsonify(data)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("🔮 SIMPLE PREDICTION VIEW - Starting...")
    logger.info("=" * 80)
    logger.info("\n📊 This is a SIMPLIFIED prediction system")
    logger.info("   (No ML training required - uses scanner scores)")
    logger.info(f"\n🌐 Open: http://127.0.0.1:5001/")
    logger.info("\n💡 To upgrade to REAL ML predictions:")
    logger.info("   1. Run scanner daily for 10+ days")
    logger.info("   2. Run: python prediction_engine.py")
    logger.info("   3. Run: python prediction_view.py")
    logger.info("\n" + "=" * 80 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
