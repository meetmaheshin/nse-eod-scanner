# 🤖 FULL AUTOMATION SETUP GUIDE

## Current Status: SEMI-AUTOMATED

### What Works Automatically:
- ✅ **Render.com deployment** - Web app runs 24/7
- ✅ **Live prices** - Fetched from Yahoo Finance in real-time
- ✅ **Auto-refresh** - Page updates every 15 seconds
- ✅ **Auto-deploy** - Render redeploys when you push to GitHub

### What's Still Manual:
- ❌ **Scanner execution** - You need to run it manually
- ❌ **Data push to GitHub** - You need to commit and push manually

---

## 🎯 TO MAKE IT 100% AUTOMATED

You need **TWO** automations:

### Automation 1: Auto-run Scanner Daily ⏰
### Automation 2: Auto-push to GitHub 📤

---

## 🔧 AUTOMATION 1: AUTO-RUN SCANNER (15 minutes)

### Option A: Windows Task Scheduler (Recommended)

**Step 1: Open Task Scheduler**
```
Press Win + R
Type: taskschd.msc
Press Enter
```

**Step 2: Create Basic Task**
1. Click "Create Basic Task"
2. Name: `EOD Scanner Auto Run`
3. Description: `Runs NSE scanner at 3:35 PM daily`
4. Click Next

**Step 3: Set Trigger**
1. Select: **Daily**
2. Click Next
3. Start date: Today
4. Time: **15:35** (3:35 PM)
5. Recur every: **1 days**
6. Click Next

**Step 4: Set Action**
1. Select: **Start a program**
2. Click Next
3. Program/script: `d:\scanner\scanner\run_scanner.bat`
4. Click Next
5. Click Finish

**Step 5: Test It**
1. In Task Scheduler, find "EOD Scanner Auto Run"
2. Right-click → **Run**
3. Check `eod_scanner_output/` folder for new CSV files

✅ **Scanner now runs automatically at 3:35 PM every day!**

---

## 🔧 AUTOMATION 2: AUTO-PUSH TO GITHUB (Optional)

### Two Approaches:

#### Approach A: Modify the Scanner Script (Recommended)

Update `run_scanner.bat` to also push to GitHub:

```batch
@echo off
echo ========================================
echo NSE EOD Scanner - Auto Run with Git Push
echo ========================================
echo.

REM Add Git to PATH
set PATH=%PATH%;C:\Program Files\Git\cmd

REM Change to scanner directory
cd /d d:\scanner\scanner

REM Run the scanner
echo [1/3] Running scanner at %date% %time%
D:\scanner\.venv\Scripts\python.exe eod_scanner_nse_improved.py

echo.
echo [2/3] Adding files to Git...
git add eod_scanner_output/*.csv

echo.
echo [3/3] Committing and pushing to GitHub...
git commit -m "Auto-update: Scanner data %date% %time%"
git push origin main

echo.
echo ========================================
echo ✅ Scanner completed and pushed to GitHub!
echo ========================================
echo.

timeout /t 5
```

Save this and the Task Scheduler will run it daily!

**Result:**
- 3:35 PM: Scanner runs
- 3:36 PM: New CSV files created
- 3:37 PM: Automatically pushed to GitHub
- 3:40 PM: Render.com auto-deploys
- 3:42 PM: Your web app shows latest data! 🎉

---

#### Approach B: Separate Git Push Task

Create another batch file: `auto_push_git.bat`

```batch
@echo off
set PATH=%PATH%;C:\Program Files\Git\cmd
cd /d d:\scanner\scanner

git add eod_scanner_output/*.csv
git commit -m "Auto-update: Scanner data %date% %time%"
git push origin main
```

Then create **another** Task Scheduler task:
- Name: `Auto Push Scanner Data`
- Time: **15:40** (5 minutes after scanner)
- Action: Run `auto_push_git.bat`

---

## ⚠️ IMPORTANT: GitHub Authentication

For auto-push to work unattended, you need to save GitHub credentials:

### Option 1: Use Git Credential Manager (Recommended)

```powershell
# First time, run this and enter credentials
git push

# Windows will save credentials automatically
# Future pushes work without asking!
```

### Option 2: Use Personal Access Token in URL

```powershell
git remote set-url origin https://YOUR_TOKEN@github.com/meetmaheshin/nse-eod-scanner.git
```

Replace `YOUR_TOKEN` with GitHub Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Copy token
5. Use in command above

---

## 🎯 FULLY AUTOMATED WORKFLOW

After setup, here's what happens **automatically every day**:

```
3:30 PM → Market closes (NSE)
         ↓
3:35 PM → Task Scheduler triggers
         → Scanner runs automatically
         → Analyzes NIFTY 50 stocks
         → Generates CSV files
         ↓
3:36 PM → Script commits to Git
         → Pushes to GitHub
         ↓
3:38 PM → Render.com detects new commit
         → Starts auto-deployment
         ↓
3:42 PM → New data live on web app! 🎉
         → Accessible from anywhere
         → Live prices updating
```

**You do NOTHING!** ✨

---

## 📱 WHAT YOU'LL SEE

### On Your Phone/Computer (anywhere):
1. Open: `https://nse-scanner.onrender.com` (your URL)
2. See latest signals (from today's 3:35 PM run)
3. See live prices (updating in real-time)
4. Auto-refreshes every 15 seconds

### No Manual Work Needed:
- ❌ No need to run scanner manually
- ❌ No need to push to GitHub
- ❌ No need to deploy to Render
- ✅ Everything happens automatically!

---

## 🚀 QUICK START AUTOMATION

**Easiest way to set this up RIGHT NOW:**

### Step 1: Update run_scanner.bat (2 minutes)

Replace contents of `d:\scanner\scanner\run_scanner.bat` with:

```batch
@echo off
echo ========================================
echo NSE EOD Scanner - Auto Run with Git Push
echo ========================================

set PATH=%PATH%;C:\Program Files\Git\cmd
cd /d d:\scanner\scanner

echo [1/3] Running scanner...
D:\scanner\.venv\Scripts\python.exe eod_scanner_nse_improved.py

echo [2/3] Committing to Git...
git add eod_scanner_output/*.csv
git commit -m "Auto-update: Scanner data %date% %time%"

echo [3/3] Pushing to GitHub...
git push origin main

echo ✅ Done! Check Render.com in 5 minutes!
timeout /t 5
```

### Step 2: Test It (1 minute)

```powershell
cd d:\scanner\scanner
.\run_scanner.bat
```

Should run scanner AND push to GitHub!

### Step 3: Set up Task Scheduler (5 minutes)

Follow "Automation 1" steps above.

**DONE!** Fully automated! 🎉

---

## 🆘 TROUBLESHOOTING

### Git push asks for credentials
- Run `git push` manually once
- Enter credentials
- Windows saves them
- Future auto-pushes work!

### Scanner runs but doesn't push
- Check Git is in PATH: `set PATH=%PATH%;C:\Program Files\Git\cmd`
- Test Git: `git --version`
- Make sure you're in correct folder: `cd /d d:\scanner\scanner`

### Render.com doesn't update
- Check GitHub - are new commits showing?
- Check Render.com logs
- Verify "Auto-Deploy" is ON in Render settings

---

## ✅ AUTOMATION CHECKLIST

- [ ] Update `run_scanner.bat` with Git push commands
- [ ] Test batch file manually
- [ ] Set up Task Scheduler (3:35 PM daily)
- [ ] Test Task Scheduler (right-click → Run)
- [ ] Verify GitHub gets updated
- [ ] Verify Render.com auto-deploys
- [ ] Check web app shows new data
- [ ] 🎉 Fully automated!

---

## 📊 RESULT

**After setup:**
- Scanner runs automatically at 3:35 PM daily
- Data pushed to GitHub automatically
- Render.com updates automatically
- Web app always shows latest data
- Accessible from anywhere, anytime!

**Your only job:** Open the URL and trade! 📈

---

**Want me to help you set this up now?** Let me know! 🚀
