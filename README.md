# 📊 NSE EOD Scanner - Live Trading Signals & Predictions

**Real-time stock scanner for NIFTY 50 with live prices and tomorrow's predictions.**

## 🚀 Quick Start

### Start the Web Views:
```powershell
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

**Access:**
- 📈 **Live Signals:** http://127.0.0.1:5000/
- 🔮 **Predictions:** http://127.0.0.1:5001/

---

## ✨ Features

✅ **Real-time Stock Analysis**
- NIFTY 50 stocks with 19 technical indicators
- Long/Short signals with risk assessment
- Sector-wise analysis

✅ **Live Web Dashboard**
- Real-time prices from Yahoo Finance
- Auto-refresh every 15 seconds
- Separate Long/Short/Combined views
- Mobile-friendly interface

✅ **Tomorrow's Predictions**
- Score-based prediction system
- Confidence percentages & recommendations
- High confidence filter (60%+)
- STRONG BUY / BUY / HOLD / AVOID ratings

✅ **Production Ready**
- Auto-run daily (Task Scheduler)
- Cloud deployment ready (Render/Heroku/ngrok)
- Git repository configured

---

## 📁 Project Structure

```
scanner/
├── START_BOTH_VIEWS.py              # 🚀 Launch both web servers
├── eod_scanner_nse_improved.py      # Main scanner (19 indicators)
├── run_scanner.bat                  # Auto-run script (Task Scheduler)
├── scheduler.py                     # Python-based daily automation
├── requirements.txt                 # All dependencies
│
├── web_views/                       # Web Interfaces
│   ├── live_view_new.py            # Port 5000 - Live signals with real-time prices
│   └── prediction_view_simple.py   # Port 5001 - Tomorrow's predictions
│
├── ml_prediction/                   # ML System (Future Enhancement)
│   ├── prediction_engine.py        # Training engine (needs 10+ days data)
│   └── prediction_view.py          # Advanced ML view (after training)
│
├── docs/                            # 📚 Documentation
│   ├── QUICK_DEPLOY.md             # 👈 START HERE - Deploy in 15 min
│   ├── DEPLOYMENT_GUIDE.md         # Complete deployment reference
│   ├── PROJECT_STATUS.md           # Current status & FAQs
│   └── [7 more guides]
│
├── eod_scanner_output/              # Scanner CSV results
├── ml_models/                       # ML models (empty - needs 10+ days data)
├── logs/                            # Log files
└── pine_scripts/                    # TradingView indicators
```


---

## 🎯 What Do You Want to Do?

### 1️⃣ Run Scanner Automatically Every Day
**Time:** 15 minutes  
**Guide:** `docs/QUICK_DEPLOY.md` → Auto-Run Scanner  
**Result:** Scanner runs at 3:35 PM daily without manual work

### 2️⃣ Access from Anywhere (Phone, Office)
**Time:** 15 minutes (ngrok) or 30 minutes (Render.com)  
**Guide:** `docs/QUICK_DEPLOY.md` → Deploy Online  
**Result:** Public URL to access from anywhere

### 3️⃣ Deploy to Cloud (24/7 Availability)
**Time:** 30 minutes  
**Guide:** `docs/DEPLOYMENT_GUIDE.md` → Cloud Deployment Options  
**Result:** Permanent URL, no PC needed

### 4️⃣ Understand ML Models (Why Empty?)
**Guide:** `docs/PROJECT_STATUS.md` → Q1  
**Answer:** Need 10+ days data to train (have 2 days now)

---

## ⚡ Quick Commands

### Start Web Views:
```powershell
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

### Run Scanner Manually:
```powershell
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py
```

### Test Auto-Run Script:
```powershell
.\run_scanner.bat
```

---

## 🌐 Deploy Online in 15 Minutes (ngrok)

**Fastest way to access from anywhere:**

```powershell
# 1. Download ngrok from: https://ngrok.com/download
# 2. Start your scanner:
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py

# 3. Open new PowerShell terminal:
C:\path\to\ngrok.exe http 5000

# 4. Copy the URL (e.g., https://abc123.ngrok.io)
# 5. Open from phone/anywhere! 🎉
```

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| Scanner | ✅ Working | NIFTY 50, 19 technical indicators |
| Live View | ✅ Running | Port 5000, real-time Yahoo Finance prices |
| Predictions | ✅ Running | Port 5001, score-based with confidence |
| ML Model | ⏳ Not trained | Need 10+ days data (currently have 2 days) |
| Automation | ⏳ Ready | Files prepared, need Task Scheduler setup |
| Cloud Deploy | ⏳ Ready | Configured for Render/Heroku/ngrok |

---

## 🤖 ML Models - Why Empty?

**Short Answer:** Need more data to train the model.

**Details:**
- ML training requires **10+ days** of historical scanner runs
- Currently have only **2 days** of data
- Using **simple score-based predictions** for now (works great!)
- ML model will provide better accuracy after training
- Continue running scanner daily to collect data

**Full explanation:** See `docs/PROJECT_STATUS.md` → Question 1

---

## 📚 Documentation

| File | Purpose | When to Use |
|------|---------|-------------|
| **QUICK_DEPLOY.md** | Get online in 15 min | 👈 START HERE |
| **DEPLOYMENT_GUIDE.md** | Complete deployment reference | Full deployment details |
| **PROJECT_STATUS.md** | Current status & FAQs | Common questions answered |
| **QUICK_REFERENCE.md** | File locations | Find specific files |
| **FILE_ORGANIZATION.md** | Folder structure | Understand organization |

---

## 🔧 Technical Details

### Scanner (19 Technical Indicators):
- **Trend:** EMA 9/21/50, MACD, ADX
- **Momentum:** RSI, Stochastic, ROC, IBS
- **Volume:** OBV, Volume MA, Spike detection
- **Volatility:** ATR, Bollinger Bands
- **Price Action:** Support/Resistance levels, Breakouts
- **Patterns:** Doji, Hammer, Shooting Star

### Weighted Scoring System:
- Trend signals: Weight 3
- Breakouts: Weight 3  
- MACD: Weight 2
- Momentum: Weight 2
- Volume confirmation: Weight 2
- Risk/Reward ratio consideration

### Risk Assessment:
- **Low:** Strong signals, good volume, favorable R/R
- **Medium:** Mixed signals, average volume
- **High:** Weak signals, low volume, poor R/R

---

## 💡 Next Steps

### Immediate (This Week):
1. ✅ **Set up automation** (15 min)
   - Configure Windows Task Scheduler
   - Scanner runs at 3:35 PM daily automatically
   - See: `docs/QUICK_DEPLOY.md`

2. ✅ **Deploy online** (15-30 min)
   - Quick: Use ngrok for temporary public URL
   - Permanent: Deploy to Render.com
   - See: `docs/DEPLOYMENT_GUIDE.md`

### Future (After 10 Days):
3. ✅ **Train ML model**
   - Collect 10+ days of scanner data
   - Run: `python ml_prediction/prediction_engine.py`
   - Switch to ML-based predictions for better accuracy

---

## 🆘 Need Help?

**Quick Solutions:**
- **How to deploy?** → `docs/QUICK_DEPLOY.md`
- **Automation setup?** → `docs/QUICK_DEPLOY.md` → Auto-Run Scanner
- **Why ML empty?** → `docs/PROJECT_STATUS.md` → Q1
- **Cloud deployment?** → `docs/DEPLOYMENT_GUIDE.md`

---

## 📞 Support Files

### Configuration:
- `scanner_config.json` - Scanner settings
- `requirements.txt` - Python dependencies
- `.gitignore` - Git configuration
- `Procfile` - Deployment configuration
- `runtime.txt` - Python version specification

### Logs & Output:
- `logs/scanner.log` - Scanner execution logs
- `eod_scanner_output/*.csv` - Daily signal CSVs

---

## 🚀 Getting Started Checklist

- [ ] Start both web views: `START_BOTH_VIEWS.py`
- [ ] Access Live View: http://127.0.0.1:5000/
- [ ] Access Predictions: http://127.0.0.1:5001/
- [ ] Set up Task Scheduler for daily auto-run
- [ ] Deploy with ngrok for remote access
- [ ] (Optional) Deploy to Render.com for 24/7 availability
- [ ] Run scanner daily for 10 days
- [ ] Train ML model after 10 days

---

**Built with:** Python 3.13 • Flask • pandas • yfinance • scikit-learn

**Happy Trading! 📈**


**Full explanation:** See `docs/PROJECT_STATUS.md` → Question 1

---

## 📚 Documentation

| File | Purpose | When to Use |
|------|---------|-------------|
| **QUICK_DEPLOY.md** | Get online in 15 min | 👈 START HERE |
| **DEPLOYMENT_GUIDE.md** | Complete deployment reference | Full deployment details |
| **PROJECT_STATUS.md** | Current status & FAQs | Common questions answered |
| **QUICK_REFERENCE.md** | File locations | Find specific files |
| **FILE_ORGANIZATION.md** | Folder structure | Understand organization |

---

## 🔧 Technical Details

### Scanner Features (19 Indicators):
- **Trend:** EMA crossovers, MACD, ADX
- **Momentum:** RSI, Stochastic, ROC, IBS
- **Volume:** OBV, Volume MA, Volume Spike
- **Volatility:** ATR, Bollinger Bands
- **Price Action:** Support/Resistance, Breakouts
- **Pattern:** Doji, Hammer, Shooting Star

### Scoring System:
- Weighted scoring system (trend=3, breakouts=3, MACD=2, etc.)
- Risk-reward ratio consideration
- Momentum divergence detection
- Volume confirmation requirements

### 3. **Risk Assessment**
- Risk levels: Low, Medium, High
- Risk-reward ratio calculation
- Volatility-based risk scoring
- Risk factors consideration

### 4. **Improved Reliability**
- Retry mechanism for data fetching
- Better error handling
- Progress tracking with logging
- File conflict resolution
- Data validation

### 5. **Configuration System**
- JSON-based configuration
- Support for custom watchlists
- Configurable parameters
- Universe selection (NIFTY50, NIFTY_NEXT50, CUSTOM)

### 6. **Enhanced Output**
- More detailed CSV files with 30+ columns
- Better formatted console output
- Risk level indicators
- Enhanced trading hints
- Timestamp-based file naming

## Dependencies Status ✅
All required dependencies are installed:
- pandas (2.3.3)
- numpy (2.3.4)
- yfinance (0.2.66)
- pytz (2025.2)

## Usage

### Basic Usage
```bash
python eod_scanner_nse_improved.py
```

### Using Utilities
```bash
# Analyze historical performance
python scanner_utils.py analyze

# Quick summary of results
python scanner_utils.py summary long_candidates_2025-10-28_1435.csv

# Update custom watchlist
python scanner_utils.py watchlist RELIANCE,TCS,HDFCBANK
```

### Configuration
Edit `scanner_config.json` to customize:
```json
{
  "universe": "NIFTY50",           # NIFTY50, NIFTY_NEXT50, or CUSTOM
  "custom_symbols": [],            # Your custom stock list
  "period": "6mo",                 # Data period
  "min_volume": 1000000,           # Minimum volume filter
  "vol_surge_threshold": 1.3,      # Volume surge multiplier
  "cpr_narrow_percentile": 0.2,    # CPR narrowness threshold
  "max_retries": 3                 # Data fetch retries
}
```

## Sample Output Analysis

### Top Long Candidates (Current Scan)
1. **JSWSTEEL** - Score: 10, Risk: Low, R:R: 0.1
   - Strong uptrend with 20-day high breakout
   - High volume confirmation
   - Low risk profile

2. **TATASTEEL** - Score: 9, Risk: Low, R:R: 0.0
   - Momentum continuation
   - Volume surge
   - Bollinger Band expansion

3. **UPL** - Score: 7, Risk: Low, R:R: 0.1
   - 20-day high breakout
   - Bollinger Band squeeze (potential expansion)
   - Strong volume

### Key Metrics Explained
- **Score**: 0-15 scale (higher is better)
- **Risk Level**: Low/Medium/High (based on volatility, RSI extremes, volume)
- **R:R**: Risk-Reward ratio (higher is better for position sizing)
- **Setup Flags**: Technical patterns detected

## Trading Recommendations

### High-Confidence Setups (Score >= 8)
- Focus on these for higher probability trades
- Use proper position sizing based on risk level
- Confirm with volume on breakouts

### Risk Management
- **Low Risk**: Normal position sizing
- **Medium Risk**: Reduce position size by 50%
- **High Risk**: Avoid or use very small positions

### Entry Strategy
1. Wait for breakout confirmation above resistance
2. Use volume as confirmation
3. Place stop-loss based on support levels or 1.5x ATR
4. Target based on risk-reward ratio

## Performance Notes
- Processing time: ~2-3 seconds for 50 stocks
- Memory efficient with progress tracking
- Robust error handling for market closures
- Automatic file conflict resolution

## Support
- Check `scanner.log` for detailed execution logs
- All errors are logged with timestamps
- Configuration is validated on startup
- Graceful handling of data issues

---
**Last Updated**: October 28, 2025
**Version**: 2.0 Enhanced