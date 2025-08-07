@echo off
echo 🚀 Setting up GitHub repository for Aastha Homoeo Clinic...

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not found. Please restart your computer or open a new command prompt.
    echo Git was installed but needs a system restart to be available.
    pause
    exit /b 1
)

echo ✅ Git found! Setting up repository...

REM Initialize git repository
echo 📁 Initializing Git repository...
git init

REM Add all files
echo 📝 Adding files to repository...
git add .

REM Create initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit - Aastha Homoeo Clinic Hospital Management System"

REM Add remote origin
echo 🔗 Adding GitHub remote...
git remote add origin https://github.com/jayantheede/Hey_Doc_Web.git

REM Set main branch
echo 🌿 Setting main branch...
git branch -M main

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git push -u origin main

echo ✅ Successfully pushed to GitHub!
echo 📱 Your repository is now available at: https://github.com/jayantheede/Hey_Doc_Web
echo.
echo 🎉 Your Aastha Homoeo Clinic project is now on GitHub!
echo.
echo Next steps:
echo 1. Visit your repository: https://github.com/jayantheede/Hey_Doc_Web
echo 2. Set up deployment using the deployment guide
echo 3. Share your repository with others
pause 