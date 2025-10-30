# 🎯 RENDER.COM - COMPLETE ACCESS GUIDE

## ✅ WHAT YOU HAVE NOW

**Your URL:** https://your-app.onrender.com (whatever Render gave you)

---

## 📊 CURRENT DEPLOYMENT

### What's Deployed:
- ✅ **Live View** (Port 5000 locally)
- ❌ **Prediction View** (Port 5001) - NOT deployed yet

### Why Only One View?
Render.com deploys **ONE** service at a time. To get both views, you have **two options**:

---

## 🎯 OPTION 1: Access Different Views on Same URL

Your current deployment has **3 views built-in**:

### Available URLs:

1. **Combined View (Long + Short):**
   ```
   https://your-app.onrender.com/
   ```

2. **Long Signals Only:**
   ```
   https://your-app.onrender.com/long
   ```

3. **Short Signals Only:**
   ```
   https://your-app.onrender.com/short
   ```

**Just add `/long` or `/short` to your URL!** ✅

---

## 🚀 OPTION 2: Deploy Prediction View Separately

To get the **Tomorrow's Predictions** view online:

### Step 1: Create Second Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Select **"nse-eod-scanner"** repository again
4. Settings:
   - **Name:** `nse-scanner-predictions`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:**
     ```
     cd web_views && gunicorn prediction_view_simple:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
     ```
   - **Plan:** Free

5. Click **"Create Web Service"**

### Step 2: Wait for Deployment

After 5-10 minutes, you'll get a second URL:
```
https://nse-scanner-predictions.onrender.com
```

### Result:
- **URL 1:** https://nse-scanner.onrender.com → Live signals
- **URL 2:** https://nse-scanner-predictions.onrender.com → Tomorrow's predictions

---

## 📱 RECOMMENDED SETUP

**For now, use Option 1** (different URLs on same deployment):

### Your Access Guide:

| View | URL | What It Shows |
|------|-----|---------------|
| **Combined** | `https://your-app.onrender.com/` | Top 25 Long + Top 25 Short |
| **Long Only** | `https://your-app.onrender.com/long` | All Long signals |
| **Short Only** | `https://your-app.onrender.com/short` | All Short signals |

**All with live prices!** 📈

---

## 🔄 DATA UPDATE STATUS

### After I pushed CSV files:

1. ✅ CSV files pushed to GitHub
2. ⏳ Render.com is auto-deploying (takes 5-10 min)
3. 🎉 Your URL will show data soon!

**Check your Render.com dashboard:**
- Look for "Deploying..." status
- When it shows "Live", refresh your URL
- Data should appear! 📊

---

## 🆘 TROUBLESHOOTING

### Still No Data After 10 Minutes?

**Check Render.com Logs:**
1. Go to your service on Render dashboard
2. Click **"Logs"** tab
3. Look for errors

**Force Manual Deploy:**
1. Click **"Manual Deploy"**
2. Select **"Clear build cache & deploy"**

---

## 💡 FULL URL STRUCTURE

After deployment completes, test these:

```
Main URL: https://YOUR-APP-NAME.onrender.com/

Available Views:
├── /                    → Combined view (Long + Short)
├── /long                → Long signals only
├── /short               → Short signals only
└── /latest              → JSON API (raw data)
```

---

## 📊 WHAT DATA SHOWS

### Current Data Available:
- **Date:** 2025-10-29
- **Time:** 07:52 AM
- **Stocks:** NIFTY 50 with scores

### Live Updates:
- **Stock Prices:** Real-time from Yahoo Finance ✅
- **Page Refresh:** Every 15 seconds ✅
- **Scanner Data:** From CSV (updates when you push new files)

---

## 🎯 NEXT STEPS

### After Data Shows Up:

1. ✅ **Bookmark all URLs:**
   - Combined: `https://your-app.onrender.com/`
   - Long: `https://your-app.onrender.com/long`
   - Short: `https://your-app.onrender.com/short`

2. ✅ **Test on phone:**
   - Open same URLs on mobile
   - Should work perfectly!

3. ✅ **Set up automation:**
   - Follow `FULL_AUTOMATION_GUIDE.md`
   - Scanner runs daily at 3:35 PM
   - Pushes new data automatically
   - Render auto-deploys

---

## 🚀 TOMORROW'S PREDICTIONS (Optional)

If you want the **Prediction View** online:

**Quick Deploy:**
1. Go to Render dashboard
2. Create **New Web Service**
3. Use same repo: `nse-eod-scanner`
4. Start command: `cd web_views && gunicorn prediction_view_simple:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Get second URL for predictions!

---

## ✅ SUMMARY

### What You Have:
- ✅ **Live View deployed** on Render.com
- ✅ **3 different views** (/, /long, /short)
- ✅ **CSV data pushed** to GitHub
- ✅ **Auto-deploy enabled**

### What's Happening Now:
- ⏳ Render.com is deploying with new CSV files
- ⏳ Wait 5-10 minutes
- 🎉 Data will appear!

### Check Status:
1. Go to https://dashboard.render.com
2. Look at your service
3. Status should change: Deploying... → Live

**Refresh your URL after it shows "Live"!** 🎯

---

**Your main URL works from anywhere - just add `/long` or `/short` for different views!** 📱🌍
