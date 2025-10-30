@echo off
echo ============================================
echo Git Configuration and Repository Setup
echo ============================================
echo.

cd /d d:\scanner\scanner

echo Step 1: Configure Git with your details
echo ============================================
echo.

set /p USERNAME="Enter your name (e.g., John Doe): "
set /p EMAIL="Enter your email (e.g., john@example.com): "

git config --global user.name "%USERNAME%"
git config --global user.email "%EMAIL%"

echo.
echo ✅ Git configured successfully!
echo.

echo Step 2: Initialize Git Repository
echo ============================================
echo.

git init

echo.
echo Step 3: Add all files
echo ============================================
echo.

git add .

echo.
echo Step 4: Commit files
echo ============================================
echo.

git commit -m "Initial commit: NSE EOD Scanner"

echo.
echo ============================================
echo ✅ LOCAL GIT REPOSITORY CREATED!
echo ============================================
echo.
echo NEXT STEPS:
echo 1. Go to https://github.com and sign up/login
echo 2. Create a new repository named: nse-eod-scanner
echo 3. Run: setup_github_remote.bat
echo.
pause
