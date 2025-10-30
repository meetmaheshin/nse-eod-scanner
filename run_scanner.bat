@echo off
REM EOD Scanner Auto-Run Script
REM This file is used by Windows Task Scheduler to run scanner daily

echo ========================================
echo NSE EOD Scanner - Auto Run
echo ========================================
echo.

REM Change to scanner directory
cd /d d:\scanner\scanner

REM Run the scanner
echo Running scanner at %date% %time%
D:\scanner\.venv\Scripts\python.exe eod_scanner_nse_improved.py

echo.
echo ========================================
echo Scanner completed at %date% %time%
echo ========================================
echo.

REM Keep window open for 5 seconds to see results
timeout /t 5
