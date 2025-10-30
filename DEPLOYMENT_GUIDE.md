# 🌐 DEPLOYMENT GUIDE - Make Scanner Accessible Anywhere

## 📋 TABLE OF CONTENTS
1. [ML Models Explanation](#ml-models)
2. [Auto-Run Scanner Daily](#auto-run)
3. [Deploy Online (Access from Anywhere)](#deploy-online)
4. [GitHub Setup](#github)
5. [Cloud Deployment Options](#cloud-options)

---

## 🤖 ML MODELS - Why Empty?

### Current Status: ❌ Not Trained Yet

**Why `ml_models/` folder is empty:**
- You're using **Simple Prediction View** (score-based)
- ML model requires **10+ days** of historical scanner data
- You currently have only **2 days** of data

### Two Prediction Systems:

| System | File | Status | Data Needed |
|--------|------|--------|-------------|
| **Simple** | `prediction_view_simple.py` | ✅ Running | None (uses scores) |
| **ML-Based** | `prediction_view.py` | ❌ Not trained | 10+ days |

### When to Use ML:

**After 10+ days, train the ML model:**
```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_engine.py
```

This will:
- Analyze historical performance
- Train Random Forest model
- Create `ml_models/prediction_model.pkl`
- Create `ml_models/scaler.pkl`

**Then switch to ML predictions:**
```powershell
# Stop simple view, use ML view instead
D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_view.py
```

---

## ⏰ AUTO-RUN SCANNER DAILY

### Option 1: Windows Task Scheduler (Recommended)

**Step-by-step:**

1. **Create a batch file** to run scanner:

```batch
@echo off
REM File: run_scanner.bat
cd /d d:\scanner\scanner
D:\scanner\.venv\Scripts\python.exe eod_scanner_nse_improved.py
pause
```

Save as: `d:\scanner\scanner\run_scanner.bat`

2. **Open Task Scheduler:**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

3. **Create Task:**
   - Click "Create Basic Task"
   - Name: "EOD Scanner"
   - Trigger: Daily at **3:35 PM** (after market close)
   - Action: Start a program
   - Program: `d:\scanner\scanner\run_scanner.bat`
   - Finish

**Done!** Scanner runs automatically every day at 3:35 PM.

---

### Option 2: Python Script with Scheduler

Create `scheduler.py`:

```python
import schedule
import time
import subprocess
from pathlib import Path

def run_scanner():
    print("Running EOD Scanner...")
    base_dir = Path(__file__).parent
    python_exe = base_dir / '.venv' / 'Scripts' / 'python.exe'
    scanner = base_dir / 'eod_scanner_nse_improved.py'
    
    subprocess.run([str(python_exe), str(scanner)])
    print("Scanner completed!")

# Schedule for 3:35 PM daily (after market close)
schedule.every().day.at("15:35").do(run_scanner)

print("Scheduler started. Waiting for 3:35 PM daily...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**Install scheduler:**
```powershell
pip install schedule
```

**Run continuously:**
```powershell
D:/scanner/.venv/Scripts/python.exe scheduler.py
```

---

## 🌐 DEPLOY ONLINE - Access from Anywhere

### Option A: Deploy to Render.com (FREE & Easy) ⭐ RECOMMENDED

**Steps:**

1. **Prepare for deployment:**

Create `requirements.txt`:
```
flask
pandas
numpy
yfinance
gunicorn
```

Create `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --chdir web_views live_view_new:app
```

2. **Push to GitHub** (see GitHub section below)

3. **Deploy on Render.com:**
   - Go to https://render.com
   - Sign up (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn --bind 0.0.0.0:$PORT live_view_new:app`
   - Deploy!

**You'll get a URL like:**
`https://nse-scanner-abc123.onrender.com`

Access from anywhere! 🌍

---

### Option B: Deploy to Heroku (FREE Tier Available)

**Steps:**

1. **Install Heroku CLI:**
   - Download from https://devcenter.heroku.com/articles/heroku-cli

2. **Prepare files:**

Create `runtime.txt`:
```
python-3.11.5
```

Create `Procfile`:
```
web: cd web_views && gunicorn live_view_new:app
```

3. **Deploy:**
```bash
heroku login
heroku create nse-scanner-yourname
git push heroku main
heroku open
```

**You'll get:**
`https://nse-scanner-yourname.herokuapp.com`

---

### Option C: Deploy to PythonAnywhere (FREE)

**Steps:**

1. Go to https://www.pythonanywhere.com
2. Sign up (free tier: 1 web app)
3. Upload your files
4. Configure web app:
   - Framework: Flask
   - Python version: 3.10
   - Source code: `/home/yourusername/scanner/web_views/live_view_new.py`
5. Install packages in bash console:
```bash
pip install --user flask pandas yfinance
```

**You'll get:**
`https://yourusername.pythonanywhere.com`

---

### Option D: Use Ngrok (Quick Testing) ⚡ FASTEST

**For temporary public access:**

1. **Download ngrok:**
   - https://ngrok.com/download

2. **Run your scanner locally:**
```powershell
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

3. **In another terminal, run ngrok:**
```powershell
ngrok http 5000
```

**You'll get URLs like:**
```
http://abc123.ngrok.io → Port 5000 (Live View)
```

Share this URL with anyone! Works from anywhere! 🌍

**Limitations:**
- Free tier: URL changes every restart
- Need to keep your PC running
- Good for testing, not permanent

---

## 🐙 GITHUB SETUP

### Initialize Git Repository

```powershell
cd d:\scanner\scanner

# Initialize git
git init

# Create .gitignore
@"
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.venv/
venv/
env/

# Scanner specific
*.log
ml_models/*.pkl
logs/*.log
eod_scanner_output/*.csv

# OS
.DS_Store
Thumbs.db
desktop.ini
"@ | Out-File -FilePath .gitignore -Encoding UTF8

# Add files
git add .

# Commit
git commit -m "Initial commit: NSE EOD Scanner"

# Create repo on GitHub (do this manually):
# 1. Go to github.com
# 2. Click "New repository"
# 3. Name: "nse-eod-scanner"
# 4. Don't initialize with README
# 5. Copy the remote URL

# Link to GitHub (replace with your URL)
git remote add origin https://github.com/yourusername/nse-eod-scanner.git

# Push
git branch -M main
git push -u origin main
```

**Your code is now on GitHub!** 🎉

---

## 🚀 RECOMMENDED DEPLOYMENT PLAN

### Phase 1: Local Automation (This Week)
✅ Set up Windows Task Scheduler
✅ Scanner runs daily at 3:35 PM automatically

### Phase 2: Quick Remote Access (Optional)
✅ Use ngrok for temporary access
✅ Share URL with friends/colleagues

### Phase 3: Permanent Deployment (After 10 days)
✅ Train ML model (10+ days data)
✅ Deploy to Render.com or Heroku
✅ Access from anywhere permanently

---

## 📊 COMPLETE AUTO-WORKFLOW

### Daily Automation Flow:

```
3:30 PM → Market closes
3:35 PM → Task Scheduler runs scanner
3:36 PM → CSV files generated in eod_scanner_output/
3:37 PM → Web views auto-refresh, show new data
```

### Access Options:

**Local Access:**
- From your PC: http://127.0.0.1:5000/
- From phone (same WiFi): http://192.168.1.8:5000/

**Remote Access (after deployment):**
- From anywhere: https://your-app.onrender.com/

---

## 💡 QUICK START DEPLOYMENT

### Easiest Way to Get Online (15 minutes):

1. **Install ngrok:**
```powershell
# Download from https://ngrok.com/download
# Extract to any folder
```

2. **Run scanner:**
```powershell
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

3. **In new terminal, run ngrok:**
```powershell
.\ngrok.exe http 5000
```

4. **Share the URL:**
```
Forwarding: https://abc123.ngrok.io → http://localhost:5000
```

**Done!** Access from anywhere: `https://abc123.ngrok.io`

---

## 🎯 ML MODEL TRAINING SCHEDULE

### Current Status:
- **Days of data:** 2
- **Needed for ML:** 10+
- **Status:** Use simple predictions for now

### Training Schedule:

| Day | Action | Model Status |
|-----|--------|--------------|
| 1-9 | Run scanner daily | Collecting data... |
| 10 | Train ML model | ✅ Ready! |
| 11+ | Use ML predictions | Better accuracy |

**Command to train (after day 10):**
```powershell
D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_engine.py
```

---

## 🆘 TROUBLESHOOTING

### Scanner doesn't run automatically
- Check Task Scheduler → "Task Scheduler Library"
- Right-click task → "Run" to test
- Check "Last Run Result" (should be 0x0)

### Ngrok URL doesn't work
- Make sure local server is running first
- Check firewall settings
- Try different ngrok region

### Deployment fails
- Check requirements.txt has all packages
- Verify Python version compatibility
- Check deployment logs for errors

---

## 📚 SUMMARY

### What You Need:

**Auto-Run Daily:**
- ✅ Use Windows Task Scheduler
- ✅ Runs at 3:35 PM automatically

**Access from Anywhere:**
- 🚀 Quick: Use ngrok (temporary)
- 🌐 Permanent: Deploy to Render/Heroku
- 📱 Mobile: Access via public URL

**ML Models:**
- ⏳ Wait 10 days to collect data
- 🤖 Then train ML model
- 📈 Get better predictions

### Next Steps:

1. **Today:** Set up Task Scheduler for auto-run
2. **This week:** Test ngrok for remote access
3. **After 10 days:** Train ML model
4. **Optional:** Deploy to Render.com for permanent URL

---

**Ready to go live! 🚀📊**
