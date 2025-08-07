@echo off
echo 🚀 Pushing Aastha Homoeo Clinic to GitHub...

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not available. Please restart your computer or open a new command prompt.
    echo Alternative: Use GitHub Desktop or web interface
    pause
    exit /b 1
)

echo ✅ Git found! Starting push process...

REM Check if repository is already initialized
if exist ".git" (
    echo 📁 Git repository already exists
) else (
    echo 📁 Initializing Git repository...
    git init
)

REM Add all files
echo 📝 Adding files to repository...
git add .

REM Create commit
echo 💾 Creating commit...
git commit -m "Update Aastha Homoeo Clinic - Hospital Management System"

REM Add remote origin if not exists
git remote -v | findstr "origin" >nul
if errorlevel 1 (
    echo 🔗 Adding GitHub remote...
    git remote add origin https://github.com/jayantheede/Hey_Doc_Web.git
) else (
    echo 🔗 Remote origin already exists
)

REM Set main branch
echo 🌿 Setting main branch...
git branch -M main

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo ❌ Error pushing to GitHub. Please check your credentials.
    echo 💡 You may need to authenticate with GitHub first.
) else (
    echo ✅ Successfully pushed to GitHub!
    echo 📱 Your repository: https://github.com/jayantheede/Hey_Doc_Web
)

echo.
echo 🎉 Your Aastha Homoeo Clinic project is now on GitHub!
echo Next steps:
echo 1. Visit: https://github.com/jayantheede/Hey_Doc_Web
echo 2. Set up deployment using DEPLOYMENT_GUIDE.md
echo 3. Deploy your website to a live server
pause 