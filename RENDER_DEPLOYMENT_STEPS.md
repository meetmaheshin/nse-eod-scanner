# 🚀 RENDER.COM DEPLOYMENT - Step-by-Step Guide

**Follow these steps exactly to deploy your scanner to Render.com**

---

## ✅ PREREQUISITES

Before starting, make sure:
- ✅ Your scanner works locally (both web views running)
- ✅ You have an email address for GitHub/Render accounts
- ✅ You're ready to spend 30 minutes

---

## 📋 STEP 1: INSTALL GIT (5 minutes)

### 1.1 Download Git
1. Open browser: https://git-scm.com/download/win
2. Click **"Click here to download"** (64-bit version)
3. Run the installer (`Git-2.xx.x-64-bit.exe`)

### 1.2 Install Git
During installation:
- ✅ Accept all default settings
- ✅ Click "Next" through all screens
- ✅ Click "Install"
- ✅ Click "Finish"

### 1.3 Verify Installation
Open **NEW PowerShell** window (important - new window!):
```powershell
git --version
```

Should show: `git version 2.xx.x`

✅ **Git installed successfully!**

---

## 📋 STEP 2: CREATE GITHUB ACCOUNT (5 minutes)

### 2.1 Sign Up
1. Go to: https://github.com
2. Click **"Sign up"**
3. Enter your email address
4. Create a password
5. Choose a username (e.g., `yourname-trading`)
6. Verify you're not a robot
7. Click **"Create account"**

### 2.2 Verify Email
1. Check your email inbox
2. Click the verification link from GitHub
3. Verify your account

✅ **GitHub account created!**

---

## 📋 STEP 3: CONFIGURE GIT (2 minutes)

Open PowerShell in your scanner folder:
```powershell
cd d:\scanner\scanner

# Set your name (use your real name)
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"
```

✅ **Git configured!**

---

## 📋 STEP 4: INITIALIZE GIT REPOSITORY (3 minutes)

Still in PowerShell (`d:\scanner\scanner`):

```powershell
# Initialize Git repository
git init

# Check status (should show many untracked files)
git status

# Add all files to Git
git add .

# Commit the files
git commit -m "Initial commit: NSE EOD Scanner"
```

You should see:
```
[main (root-commit) xxxxxxx] Initial commit: NSE EOD Scanner
 XX files changed, XXXX insertions(+)
```

✅ **Local Git repository created!**

---

## 📋 STEP 5: CREATE GITHUB REPOSITORY (3 minutes)

### 5.1 Create New Repository
1. Go to: https://github.com
2. Click the **"+"** icon (top right)
3. Click **"New repository"**

### 5.2 Repository Settings
Fill in:
- **Repository name:** `nse-eod-scanner`
- **Description:** `NSE End-of-Day Scanner with Live Predictions`
- **Visibility:** Public (or Private if you prefer)
- ❌ **DO NOT** check "Add a README file"
- ❌ **DO NOT** check "Add .gitignore"
- ❌ **DO NOT** select a license

### 5.3 Create Repository
Click **"Create repository"**

You'll see a page with instructions. **Keep this page open!**

✅ **GitHub repository created!**

---

## 📋 STEP 6: PUSH CODE TO GITHUB (3 minutes)

### 6.1 Copy Your Repository URL
On the GitHub page, you'll see a URL like:
```
https://github.com/yourusername/nse-eod-scanner.git
```

**Copy this URL!**

### 6.2 Link Local Repository to GitHub
In PowerShell (`d:\scanner\scanner`):

```powershell
# Link to GitHub (replace with YOUR URL)
git remote add origin https://github.com/YOURUSERNAME/nse-eod-scanner.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### 6.3 Enter GitHub Credentials
When prompted:
- **Username:** Your GitHub username
- **Password:** Your GitHub password (or Personal Access Token)

**Note:** If password doesn't work, you need a Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select "repo" scope
4. Copy the token and use it as password

### 6.4 Verify Upload
Refresh your GitHub repository page. You should see all your files!

✅ **Code pushed to GitHub!**

---

## 📋 STEP 7: CREATE RENDER.COM ACCOUNT (2 minutes)

### 7.1 Sign Up with GitHub
1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. Click **"GitHub"** (easiest - uses your GitHub account)
4. Authorize Render to access GitHub
5. Complete your profile

✅ **Render.com account created!**

---

## 📋 STEP 8: DEPLOY ON RENDER.COM (5 minutes)

### 8.1 Create New Web Service
1. In Render dashboard, click **"New +"**
2. Click **"Web Service"**

### 8.2 Connect Repository
1. Find `nse-eod-scanner` in the list
2. Click **"Connect"**

(If you don't see it, click "Configure account" and grant access)

### 8.3 Configure Web Service

Fill in these **EXACT** settings:

**Basic Settings:**
- **Name:** `nse-scanner` (or any name you like)
- **Region:** Choose closest to India (e.g., Singapore)
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```

- **Start Command:**
  ```
  cd web_views && gunicorn live_view_new:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

**Instance Type:**
- **Plan:** `Free` (select this!)

### 8.4 Advanced Settings (Optional)
Click **"Advanced"** and add:
- **Environment Variables:** (none needed for now)

### 8.5 Create Web Service
Click **"Create Web Service"** button at the bottom

✅ **Deployment started!**

---

## 📋 STEP 9: WAIT FOR DEPLOYMENT (5-10 minutes)

### 9.1 Monitor Deployment
You'll see the deployment logs in real-time:
- Building...
- Installing dependencies...
- Starting server...

**This takes 5-10 minutes.** Be patient! ☕

### 9.2 Deployment Success
When you see:
```
==> Your service is live 🎉
https://nse-scanner.onrender.com
```

✅ **Deployment successful!**

---

## 📋 STEP 10: ACCESS YOUR SCANNER (1 minute)

### 10.1 Get Your URL
At the top of the Render page, you'll see your URL:
```
https://nse-scanner.onrender.com
```

Or something like:
```
https://nse-scanner-abc123.onrender.com
```

### 10.2 Open in Browser
Click the URL or copy it to your browser

**You should see your Live Scanner!** 📊

### 10.3 Test from Phone
1. Open phone browser
2. Paste the same URL
3. Scanner works from anywhere! 🌍

✅ **Scanner is now LIVE!**

---

## 🎉 SUCCESS! YOU'RE DONE!

### What You Have Now:
- ✅ Scanner accessible from **anywhere** in the world
- ✅ **Permanent URL** that works 24/7
- ✅ **No PC needed** - runs on Render's servers
- ✅ Code on **GitHub** (version controlled)
- ✅ **Free tier** (no credit card needed)

### Your URLs:
- **Live Scanner:** https://your-app.onrender.com
- **GitHub Repo:** https://github.com/yourusername/nse-eod-scanner

### Share with Friends:
Just send them your Render URL! 📱

---

## ⚠️ IMPORTANT NOTES

### Free Tier Limitations:
- Service **sleeps** after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (wakes up server)
- 750 hours/month free (plenty for testing)

### Scanner Data:
- Currently deployed scanner shows **live view only**
- Scanner still runs on **your PC** to generate new data
- To update data, run scanner locally and it updates CSV files
- Consider setting up **automated scanner** (see next steps)

---

## 🚀 NEXT STEPS

### Option 1: Set Up Automated Scanner
Even though scanner is live, you still need to run it on your PC to generate new data.

**Solution:** Set up Windows Task Scheduler
- See: `QUICK_DEPLOY.md` → Auto-Run Scanner
- Scanner runs at 3:35 PM daily on your PC
- New CSV files generated
- Render.com will read new data on next refresh

### Option 2: Deploy Prediction View Too
Currently only Live View is deployed. To deploy Prediction View:

1. Update `Procfile` start command to run prediction view on port 5001
2. Or deploy a second web service for predictions

### Option 3: Upgrade to Paid Plan
For better performance:
- No sleep (always awake)
- Faster response times
- More resources
- $7/month

---

## 🆘 TROUBLESHOOTING

### Deployment Failed
**Error:** "Build failed"
- **Fix:** Check `requirements.txt` has all dependencies
- **Verify:** All file paths are correct in Procfile

### Service Won't Start
**Error:** "Service exited"
- **Fix:** Check Start Command is exactly:
  ```
  cd web_views && gunicorn live_view_new:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
  ```

### Can't See Latest Data
**Reason:** CSV files on Render are from your last Git push
- **Fix:** Need to update CSV files or run scanner on Render
- **Better:** Keep running scanner locally, deploy just the web view

### Git Push Failed
**Error:** "Authentication failed"
- **Fix:** Use Personal Access Token instead of password
- **How:** https://github.com/settings/tokens

---

## 📞 HELP RESOURCES

- **Render Docs:** https://render.com/docs
- **GitHub Docs:** https://docs.github.com
- **Git Guide:** https://git-scm.com/book

---

## ✅ DEPLOYMENT CHECKLIST

Use this checklist to track your progress:

- [ ] Step 1: Install Git
- [ ] Step 2: Create GitHub account
- [ ] Step 3: Configure Git
- [ ] Step 4: Initialize Git repository
- [ ] Step 5: Create GitHub repository
- [ ] Step 6: Push code to GitHub
- [ ] Step 7: Create Render.com account
- [ ] Step 8: Deploy on Render.com
- [ ] Step 9: Wait for deployment (5-10 min)
- [ ] Step 10: Test your live URL
- [ ] ✅ Scanner is LIVE! 🎉

---

**Estimated Total Time:** 30 minutes

**Difficulty:** Easy (just follow steps!)

**Cost:** FREE

**Result:** Scanner accessible from anywhere! 🌍

---

## 🎯 AFTER DEPLOYMENT

### Keep Your Scanner Updated:

Whenever you make changes to your code:

```powershell
cd d:\scanner\scanner

# Add changes
git add .

# Commit changes
git commit -m "Updated scanner features"

# Push to GitHub
git push origin main
```

Render.com will **automatically redeploy** your changes! 🚀

---

**Happy Trading from the Cloud! ☁️📊📈**
