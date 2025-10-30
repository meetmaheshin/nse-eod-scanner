# 🚀 QUICK START - Get Your Scanner Online in 15 Minutes

## ✅ WHAT YOU HAVE NOW

- ✅ Scanner works locally
- ✅ Two web views (Live signals + Predictions)
- ✅ Both accessible at http://127.0.0.1:5000 and http://127.0.0.1:5001
- ❌ Only works on your PC
- ❌ Need to run scanner manually

## 🎯 WHAT YOU WANT

- 🌐 Access from anywhere (phone, office, etc.)
- ⏰ Scanner runs automatically every day
- 📱 Share URL with others

---

## ⚡ FASTEST SOLUTION: NGROK (15 Minutes)

### Step 1: Download ngrok
1. Go to https://ngrok.com/download
2. Download Windows version
3. Extract to any folder (e.g., `C:\ngrok\`)

### Step 2: Start Your Scanner
```powershell
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py
```

Leave this running!

### Step 3: Open Another PowerShell
```powershell
cd C:\ngrok  # or wherever you extracted ngrok
.\ngrok.exe http 5000
```

### Step 4: Copy Your URL
You'll see something like:
```
Forwarding: https://abc123-def-456.ngrok-free.app -> http://localhost:5000
```

**This URL works from ANYWHERE!** 🌍
- Share with friends
- Open on phone
- Access from office

### Limitations:
- URL changes when you restart ngrok
- Need to keep PC running
- Free tier has connection limits

**Perfect for testing!** ✅

---

## 🏆 BEST SOLUTION: RENDER.COM (30 Minutes)

### Step 1: Install Git (if not installed)
Download from: https://git-scm.com/download/win

### Step 2: Initialize Git Repository
```powershell
cd d:\scanner\scanner

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: NSE Scanner"
```

### Step 3: Create GitHub Account
1. Go to https://github.com
2. Sign up (free)
3. Create new repository: "nse-eod-scanner"
4. Don't initialize with README

### Step 4: Push to GitHub
```powershell
# Replace 'yourusername' with your GitHub username
git remote add origin https://github.com/yourusername/nse-eod-scanner.git
git branch -M main
git push -u origin main
```

### Step 5: Deploy on Render.com
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your `nse-eod-scanner` repository
5. Settings:
   - **Name:** nse-scanner
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd web_views && gunicorn live_view_new:app`
6. Click "Create Web Service"

### Step 6: Get Your URL
After 5-10 minutes deployment, you'll get:
```
https://nse-scanner.onrender.com
```

**This URL is PERMANENT!** 🎉
- Works 24/7
- No need to keep PC running
- Free tier available

---

## ⏰ AUTO-RUN SCANNER DAILY

### Option 1: Windows Task Scheduler (Recommended)

#### Step 1: Test the Batch File
```powershell
cd d:\scanner\scanner
.\run_scanner.bat
```

Should run the scanner successfully!

#### Step 2: Create Scheduled Task
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter
4. Click "Create Basic Task"
5. Fill in:
   - **Name:** EOD Scanner Daily
   - **Description:** Runs NSE EOD scanner at 3:35 PM
   - **Trigger:** Daily
   - **Time:** 3:35 PM (15:35)
   - **Action:** Start a program
   - **Program:** `d:\scanner\scanner\run_scanner.bat`
6. Click Finish

#### Step 3: Test It
- In Task Scheduler, find "EOD Scanner Daily"
- Right-click → "Run"
- Should execute successfully!

**Done!** Scanner runs every day at 3:35 PM automatically! ✅

---

### Option 2: Python Scheduler

```powershell
# Install schedule library
pip install schedule

# Run the scheduler (keeps running)
D:/scanner/.venv/Scripts/python.exe scheduler.py
```

Runs at 3:35 PM daily, but need to keep this script running.

---

## 📱 COMPLETE WORKFLOW AFTER SETUP

### Daily Flow:
```
3:30 PM → Market closes
3:35 PM → Scanner runs automatically (Task Scheduler)
3:36 PM → New CSV files created
3:37 PM → Web views refresh, show latest signals
```

### Access:
```
From anywhere → https://your-app.onrender.com
From phone → Same URL
Share with friends → Same URL
```

---

## 🆘 WHICH OPTION TO CHOOSE?

### For Quick Testing (Today):
**Use ngrok** - Get online in 15 minutes
- ✅ Super fast
- ✅ Works immediately
- ❌ URL changes each time
- ❌ Need PC running

### For Production (Best):
**Use Render.com** - Permanent solution
- ✅ Permanent URL
- ✅ Works 24/7
- ✅ No PC needed
- ❌ Takes 30 minutes setup

### For Automation:
**Use Windows Task Scheduler** - Set and forget
- ✅ Runs automatically
- ✅ No monitoring needed
- ✅ Native to Windows

---

## 📊 ML MODEL - WHY EMPTY?

### Current Status:
- **ML models folder:** Empty ❌
- **Reason:** Need 10+ days of data
- **Current data:** Only 2 days
- **Using:** Simple score-based predictions ✅

### What to Do:
1. **Keep running scanner daily** (use Task Scheduler)
2. **After 10 days**, train ML model:
   ```powershell
   D:/scanner/.venv/Scripts/python.exe ml_prediction/prediction_engine.py
   ```
3. **Switch to ML predictions** for better accuracy

**For now, simple predictions work great!** 📈

---

## 🎯 RECOMMENDED PLAN

### This Week:
1. ✅ Set up Windows Task Scheduler (auto-run daily)
2. ✅ Test with ngrok (see it working remotely)

### Next Week:
1. ✅ Deploy to Render.com (permanent URL)
2. ✅ Share URL with friends/colleagues

### After 10 Days:
1. ✅ Train ML model
2. ✅ Get even better predictions

---

## 🚀 START NOW!

### Easiest First Step:

```powershell
# 1. Start your scanner
cd d:\scanner\scanner
D:/scanner/.venv/Scripts/python.exe START_BOTH_VIEWS.py

# 2. Download ngrok from https://ngrok.com/download
# 3. In new terminal, run:
C:\path\to\ngrok.exe http 5000

# 4. Copy the URL and open from phone!
```

**That's it! You're live! 🎉**

---

## 📞 NEED HELP?

Check the detailed guide: `DEPLOYMENT_GUIDE.md`

**Happy Trading! 📊📈**
