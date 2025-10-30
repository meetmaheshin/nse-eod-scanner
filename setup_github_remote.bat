@echo off
echo ============================================
echo Connect to GitHub and Push Code
echo ============================================
echo.

cd /d d:\scanner\scanner

set /p GITHUB_URL="Enter your GitHub repository URL (e.g., https://github.com/yourusername/nse-eod-scanner.git): "

echo.
echo Connecting to GitHub...
git remote add origin %GITHUB_URL%

echo.
echo Renaming branch to main...
git branch -M main

echo.
echo Pushing code to GitHub...
echo (You may be asked for GitHub username and password/token)
git push -u origin main

echo.
echo ============================================
echo ✅ CODE PUSHED TO GITHUB!
echo ============================================
echo.
echo NEXT STEP:
echo Go to https://render.com and deploy your app!
echo.
pause
