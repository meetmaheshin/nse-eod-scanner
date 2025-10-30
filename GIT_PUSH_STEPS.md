# Quick Git Setup and Push to GitHub

## Step-by-step commands to run in PowerShell

**Run these commands one by one:**

```powershell
# 1. Add Git to PATH (run this first in every new PowerShell)
$env:Path += ";C:\Program Files\Git\cmd"

# 2. Go to scanner folder
cd d:\scanner\scanner

# 3. Configure Git (replace with YOUR name and email)
git config --global user.name "Your Name Here"
git config --global user.email "your.email@example.com"

# 4. Initialize Git repository
git init

# 5. Add all files
git add .

# 6. Commit files
git commit -m "Initial commit: NSE EOD Scanner"

# 7. Connect to GitHub (replace with YOUR GitHub repository URL)
# You'll get this URL from GitHub after creating the repository
git remote add origin https://github.com/YOURUSERNAME/nse-eod-scanner.git

# 8. Rename branch to main
git branch -M main

# 9. Push to GitHub
git push -u origin main
```

## If you get authentication error:

You may need a Personal Access Token instead of password.

**Create token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "NSE Scanner"
4. Select scope: `repo` (check the box)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when Git asks

## After successful push:

Go back to Render.com and click "Manual Deploy" → "Deploy latest commit"

Your code will be there and deployment will start! 🚀
