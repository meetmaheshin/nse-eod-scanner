@echo off
REM EOD Scanner Auto-Run Script with GitHub Push
REM This file is used by Windows Task Scheduler to run scanner daily

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
echo Scanner completed and pushed to GitHub!
echo Render.com will auto-deploy in ~5 minutes
echo ========================================
echo Time: %date% %time%
echo.

REM Keep window open for 5 seconds to see results
timeout /t 5
