# 🚀 NSE Stock Scanner - Quick Start

## ⚡ ONE COMMAND TO RUN EVERYTHING

```powershell
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

This starts **BOTH web interfaces:**
- 📊 **Port 5000**: Today's Live Signals → http://127.0.0.1:5000/
- 🔮 **Port 5001**: Tomorrow's Predictions → http://127.0.0.1:5001/

**Press Ctrl+C to stop both servers**

---

## 📁 CLEAN FOLDER STRUCTURE

```
d:\scanner\scanner\
│
├── 📄 START_BOTH_VIEWS.py              ⭐ RUN THIS!
├── 📄 eod_scanner_nse_improved.py      📊 Main scanner (run after market)
├── 📄 scanner_config.json              ⚙️ Configuration
├── 📄 scanner_utils.py                 🔧 Utilities
├── 📄 requirements.txt                 📦 Python packages
├── 📄 README.md                        📖 This file
│
├── 📂 web_views/                       🌐 Web interfaces
│   ├── live_view_new.py                (Port 5000)
│   ├── prediction_view_simple.py       (Port 5001)
│   ├── live_view.py                    (Old backup)
│   └── start_predictions.py            (Alternative launcher)
│
├── 📂 eod_scanner_output/              💾 Scanner results (CSV files)
│   ├── all_signals_*.csv
│   ├── long_candidates_*.csv
│   └── short_candidates_*.csv
│
├── 📂 docs/                            📚 Documentation & guides
│   ├── QUICK_REFERENCE.md              (Command reference)
│   ├── FILE_ORGANIZATION.md            (File guide)
│   └── ... (other docs)
│
├── 📂 ml_prediction/                   🤖 Advanced ML (optional)
│   ├── prediction_engine.py            (Train ML model)
│   ├── prediction_view.py              (ML prediction view)
│   └── test_prediction_setup.py        (Setup tester)
│
├── 📂 pine_scripts/                    📈 TradingView indicators
│   ├── Elite_Scalping_System.pine
│   └── Professional_Scalping_System.pine
│
├── 📂 logs/                            📋 Log files
│   ├── scanner.log
│   └── prediction_engine.log
│
├── 📂 ml_models/                       🧠 Trained ML models
│   ├── prediction_model.pkl
│   └── scaler.pkl
│
└── 📂 .venv/                           🐍 Python virtual environment
```

---

## 🕐 DAILY WORKFLOW

### After Market Close (3:30 PM):
```powershell
# Step 1: Run EOD Scanner
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py

# Step 2: View Predictions
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
# Open: http://127.0.0.1:5001/
```

### During Market Hours (9:15 AM):
```powershell
# Watch Live Signals
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
# Open: http://127.0.0.1:5000/
```

---

## 🌐 WEB INTERFACES

### Port 5000 - Today's Live Signals
- **Views**: Combined / Long / Short
- **Updates**: Every 15 seconds
- **Shows**: Live prices, RSI, IBS, Sector

### Port 5001 - Tomorrow's Predictions
- **Tabs**: All / Long / Short / High Confidence
- **Updates**: Every 30 seconds
- **Shows**: Direction, Confidence, Expected Return

---

## 🆘 QUICK HELP

### Problem: Port already in use
```powershell
Stop-Process -Name python -Force
```

### Problem: No data showing
Run the scanner first:
```powershell
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py
```

### Need more info?
Check: `docs/QUICK_REFERENCE.md`

---

## 📚 DOCUMENTATION

All detailed guides are in the **`docs/`** folder:
- `QUICK_REFERENCE.md` - All commands
- `FILE_ORGANIZATION.md` - What each file does
- `PREDICTION_SYSTEM_GUIDE.md` - ML prediction guide
- `PHASE1_ENHANCEMENTS.md` - Scanner features

---

## 🎯 THAT'S IT!

**One file to run:** `START_BOTH_VIEWS.py`  
**Two URLs to open:** Port 5000 & Port 5001  
**Simple!** 📊✨

---

**Happy Trading! 🚀**
