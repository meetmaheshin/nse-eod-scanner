# 📁 FILE ORGANIZATION GUIDE

## ⭐ IMPORTANT FILES (What You Actually Need)

### 🚀 TO RUN:
```
START_BOTH_VIEWS.py          ← RUN THIS! Starts both views at once
```

### 📊 CORE SCANNER:
```
eod_scanner_nse_improved.py  ← Main scanner (run after market close)
scanner_config.json          ← Configuration
scanner_utils.py             ← Utilities
```

### 🌐 WEB VIEWS:
```
live_view_new.py             ← Port 5000 (Today's live signals)
prediction_view_simple.py    ← Port 5001 (Tomorrow's predictions)
```

### 📖 DOCUMENTATION:
```
QUICK_REFERENCE.md           ← Quick commands guide
README.md                    ← Main documentation
```

---

## 🗑️ FILES YOU CAN IGNORE

### Old/Backup Files:
```
live_view.py                 ← Old version (use live_view_new.py instead)
eod_scanner_nse.py           ← Old scanner (use eod_scanner_nse_improved.py)
```

### Advanced ML (Use Later):
```
prediction_engine.py         ← ML training (needs 10+ days data)
prediction_view.py           ← ML prediction view
test_prediction_setup.py     ← Setup tester
```

### Documentation (Reference Only):
```
START_HERE.md
PHASE1_ENHANCEMENTS.md
PREDICTION_SYSTEM_GUIDE.md
Pine_Script_Instructions.md
```

### TradingView Scripts (Optional):
```
Elite_Scalping_System.pine
Professional_Scalping_System.pine
```

### Support Files:
```
start_predictions.py         ← Alternative launcher
```

---

## 📂 FOLDERS

### 📁 eod_scanner_output/
**Purpose:** Stores scanner results (CSV files)  
**Files:** all_signals_*.csv, long_candidates_*.csv, short_candidates_*.csv  
**Keep:** YES - Contains your trading signals!

### 📁 ml_models/
**Purpose:** Stores trained ML models  
**Keep:** YES (if you train ML model)  
**Can delete:** If you want to retrain from scratch

### 📁 .venv/
**Purpose:** Python virtual environment  
**Keep:** YES - Required to run everything!

### 📁 __pycache__/
**Purpose:** Python cache files  
**Can delete:** YES - Regenerates automatically

### 📁 docs/
**Purpose:** Documentation files moved here  
**Can delete:** NO - Keep for reference

### 📁 web_views/
**Purpose:** Web interface files moved here  
**Currently:** Empty (files weren't moved successfully)

### 📁 ml_prediction/
**Purpose:** ML prediction files moved here  
**Currently:** Empty (files weren't moved successfully)

### 📁 pine_scripts/
**Purpose:** TradingView Pine Scripts moved here  
**Currently:** Empty (files weren't moved successfully)

---

## 🎯 SIMPLIFIED STRUCTURE (What Matters)

```
d:\scanner\scanner\
│
├── ⭐ START_BOTH_VIEWS.py           # RUN THIS!
│
├── 📊 CORE FILES (Main Scanner)
│   ├── eod_scanner_nse_improved.py
│   ├── scanner_config.json
│   └── scanner_utils.py
│
├── 🌐 WEB FILES (Views)
│   ├── live_view_new.py             # Port 5000
│   └── prediction_view_simple.py    # Port 5001
│
├── 📖 DOCS (Read These)
│   ├── QUICK_REFERENCE.md           # Commands
│   └── README.md                    # Full guide
│
└── 📂 OUTPUT (Scanner Results)
    └── eod_scanner_output/
```

---

## 🧹 CLEANUP SUGGESTION

Want to clean up? You can DELETE these files (optional):

```powershell
# Backup/old files
Remove-Item live_view.py
Remove-Item eod_scanner_nse.py

# Duplicate docs (keep in main folder for now)
# Remove-Item START_HERE.md
# Remove-Item PHASE1_ENHANCEMENTS.md
# Remove-Item PREDICTION_SYSTEM_GUIDE.md

# Advanced ML (keep for later use)
# Remove-Item prediction_engine.py
# Remove-Item prediction_view.py
# Remove-Item test_prediction_setup.py
```

**But honestly:** Just ignore them! Focus on using `START_BOTH_VIEWS.py` 🎯

---

## ✅ BOTTOM LINE

**Files to remember:**
1. `START_BOTH_VIEWS.py` → Run this
2. `eod_scanner_nse_improved.py` → Run after market
3. `QUICK_REFERENCE.md` → Read this for commands

**Everything else:** Support files, documentation, or backup.

**Don't worry about organizing!** The system works as-is. 📊✨
