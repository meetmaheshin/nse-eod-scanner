# 📖 QUICK REFERENCE - What to Run & When

## 🎯 ONE COMMAND TO RULE THEM ALL

### ⭐ Run Both Views at Once (RECOMMENDED):
```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

**This opens:**
- 📊 Port 5000: Today's Live Signals → http://127.0.0.1:5000/
- 🔮 Port 5001: Tomorrow's Predictions → http://127.0.0.1:5001/

**Press Ctrl+C to stop both servers**

---

## 📁 FOLDER STRUCTURE (Organized!)

```
d:\scanner\scanner\
│
├── 📄 START_BOTH_VIEWS.py         ⭐ RUN THIS! (Starts both views)
├── 📄 eod_scanner_nse_improved.py  (Main scanner - run after market)
├── 📄 scanner_config.json          (Configuration)
├── 📄 scanner_utils.py             (Helper utilities)
├── 📄 README.md                    (Main documentation)
│
├── 📂 web_views/                   (All web interfaces)
│   ├── live_view_new.py            (Port 5000 - Today's signals)
│   ├── prediction_view_simple.py   (Port 5001 - Tomorrow's predictions)
│   ├── live_view.py                (Old version - ignore)
│   └── start_predictions.py        (Alternative starter)
│
├── 📂 ml_prediction/               (Advanced ML - use later)
│   ├── prediction_engine.py        (ML training engine)
│   ├── prediction_view.py          (ML prediction view)
│   └── test_prediction_setup.py    (Setup tester)
│
├── 📂 docs/                        (All documentation)
│   ├── START_HERE.md               (Getting started guide)
│   ├── PHASE1_ENHANCEMENTS.md      (Scanner enhancements doc)
│   ├── PREDICTION_SYSTEM_GUIDE.md  (ML prediction guide)
│   └── Pine_Script_Instructions.md (TradingView scripts)
│
├── 📂 pine_scripts/                (TradingView indicators)
│   ├── Elite_Scalping_System.pine
│   └── Professional_Scalping_System.pine
│
├── 📂 eod_scanner_output/          (Scanner results - CSV files)
│   ├── all_signals_*.csv
│   ├── long_candidates_*.csv
│   └── short_candidates_*.csv
│
└── 📂 ml_models/                   (ML models - created when trained)
    ├── prediction_model.pkl
    └── scaler.pkl
```

---

## 🕐 DAILY WORKFLOW

### After Market Close (3:30 PM):
```powershell
cd d:\scanner\scanner

# Step 1: Run EOD Scanner
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py

# Step 2: View Results
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

**Then:**
- Open http://127.0.0.1:5001/ → See tomorrow's predictions
- Plan your trades for next day

---

### During Market Hours (9:15 AM - 3:30 PM):
```powershell
cd d:\scanner\scanner

# Start live view
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

**Then:**
- Open http://127.0.0.1:5000/ → Watch live signals
- Monitor your positions

---

## 🌐 WHAT EACH VIEW SHOWS

### Port 5000 - Today's Live Signals
**File:** `web_views/live_view_new.py`

**3 Views:**
- `/` → Combined (Long + Short together)
- `/long` → Long signals only (green theme)
- `/short` → Short signals only (red theme)

**Features:**
- ✅ Live prices (updates every 15 seconds)
- ✅ Top 25 Long + Top 25 Short
- ✅ Columns: Symbol, Score, LTP, RSI, IBS, Sector
- ✅ Automatic cache busting

---

### Port 5001 - Tomorrow's Predictions
**File:** `web_views/prediction_view_simple.py`

**4 Tabs:**
1. **📊 All Predictions** - Every stock with direction
2. **🟢 Long Only** - Buy predictions
3. **🔴 Short Only** - Sell predictions
4. **⭐ High Confidence** - Confidence ≥ 60%

**Features:**
- ✅ Direction: LONG/SHORT/NEUTRAL
- ✅ Confidence: 0-100% score
- ✅ Recommendation: STRONG BUY/BUY/HOLD/AVOID
- ✅ Expected Return: Estimated % profit
- ✅ Auto-updates every 30 seconds

**Understanding Confidence:**
- **75%+** → 🟢 High (Strong signal)
- **60-75%** → 🟠 Medium (Good signal)
- **<60%** → 🔴 Low (Weak signal)

---

## ❓ COMMON QUESTIONS

### Q: Can I run both ports at the same time?
**A:** YES! Use `START_BOTH_VIEWS.py` - it runs both automatically.

### Q: Which file do I need to run?
**A:** Just ONE file: `START_BOTH_VIEWS.py`

### Q: Why is High Confidence tab empty?
**A:** Fixed! Now shows predictions with 60%+ confidence (was 70% before)

### Q: How do I stop the servers?
**A:** Press `Ctrl+C` in the terminal

### Q: Which view should I use during market hours?
**A:** Port 5000 (live signals with real-time prices)

### Q: Which view for planning next day?
**A:** Port 5001 (tomorrow's predictions)

---

## 🆘 TROUBLESHOOTING

### Problem: Port already in use
```powershell
# Kill all Python processes
Stop-Process -Name python -Force

# Restart
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

### Problem: No data showing
```powershell
# Run scanner first!
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py
```

### Problem: High Confidence tab blank
**Solution:** Server auto-reloaded with fix. Just refresh browser (Ctrl+F5)

### Problem: Too many files, confused
**Solution:** ONLY run `START_BOTH_VIEWS.py` - ignore everything else!

---

## 🎓 ADVANCED (Later)

### Want REAL ML Predictions?
After 10+ days of scanner data:
```powershell
cd d:\scanner\scanner

# Train ML model
D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_engine.py

# Use ML view (port 5001)
D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_view.py
```

---

## 📝 SUMMARY - THE ONLY COMMAND YOU NEED

```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

**That's it!** 🎉

Open both URLs:
- http://127.0.0.1:5000/ (Today)
- http://127.0.0.1:5001/ (Tomorrow)

**Happy Trading! 📊🚀**
