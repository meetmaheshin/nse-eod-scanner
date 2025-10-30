# 🎯 SIMPLE START GUIDE - Just 2 Commands!

## What You Have Now

✅ **Live View** - Shows today's signals with live prices  
✅ **Prediction View** - Shows tomorrow's predictions

---

## 🚀 START HERE (2 Commands Only!)

### Command 1: Today's Live Signals
```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe live_view_new.py
```
**Open**: http://127.0.0.1:5000/  
**Shows**: Today's Long/Short signals with live prices updating every 15 seconds

---

### Command 2: Tomorrow's Predictions  
**Open a NEW terminal**, then:
```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe prediction_view_simple.py
```
**Open**: http://127.0.0.1:5001/  
**Shows**: Tomorrow's predictions based on today's scanner scores

---

## 📊 What Each Port Shows

| Port | What | When to Use |
|------|------|-------------|
| **5000** | Today's signals + Live prices | During market hours |
| **5001** | Tomorrow's predictions | After market close (plan next day) |

---

## 🎬 Quick Demo

1. **Run Command 1** → Shows TODAY's trading signals
2. **Run Command 2** → Shows TOMORROW's predicted trades
3. **Open both URLs** → Compare side-by-side!

---

## ❓ Confused About All The Files?

### You Only Need These 2:
1. **`live_view_new.py`** - Port 5000 (today)
2. **`prediction_view_simple.py`** - Port 5001 (tomorrow)

### Other Files (Ignore for Now):
- `prediction_engine.py` - Advanced ML (use later)
- `prediction_view.py` - Advanced ML view (use later)
- `test_*.py` - Testing files
- `*.md` - Documentation

---

## 🔄 Daily Workflow

### After Market Close (3:30 PM):
```powershell
# Step 1: Run scanner
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py

# Step 2: View tomorrow's predictions
D:/scanner/.venv/Scripts/python.exe prediction_view_simple.py
# Open: http://127.0.0.1:5001/
```

### Next Morning (9:00 AM):
```powershell
# View live signals
D:/scanner/.venv/Scripts/python.exe live_view_new.py
# Open: http://127.0.0.1:5000/
```

---

## 🆘 Help! Something's Not Working

### Port 5000 not showing data?
```powershell
# Kill any old Python processes
Stop-Process -Name python -Force

# Restart
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe live_view_new.py
```

### Port 5001 shows no predictions?
**Make sure you ran the scanner first!**
```powershell
D:/scanner/.venv/Scripts/python.exe eod_scanner_nse_improved.py
```

---

## 📈 Want REAL ML Predictions? (Later)

Once you have 10+ days of scanner data:
```powershell
# Train ML model
D:/scanner/.venv/Scripts/python.exe prediction_engine.py

# Use ML predictions
D:/scanner/.venv/Scripts/python.exe prediction_view.py
```

---

## ✅ That's It!

**Two commands. Two ports. Simple.**

Port 5000 = Today  
Port 5001 = Tomorrow

**Happy Trading! 📊🚀**
