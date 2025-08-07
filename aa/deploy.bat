@echo off
echo 🚀 Starting deployment of Aastha Homoeo Clinic...

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if Heroku CLI is installed
heroku --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Heroku CLI is not installed.
    echo Please download and install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Initialize git repository if not already done
if not exist ".git" (
    echo 📁 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - Aastha Homoeo Clinic"
)

REM Create Heroku app
echo 🔧 Creating Heroku app...
set /p app_name="Enter your Heroku app name (or press Enter for auto-generated name): "

if "%app_name%"=="" (
    heroku create
) else (
    heroku create %app_name%
)

REM Set environment variables
echo 🔐 Setting environment variables...
set /p mongodb_uri="Enter your MongoDB connection string: "
set /p secret_key="Enter a strong secret key for Flask: "

heroku config:set MONGODB_URI="%mongodb_uri%"
heroku config:set SECRET_KEY="%secret_key%"

REM Deploy to Heroku
echo 🚀 Deploying to Heroku...
git add .
git commit -m "Deploy Aastha Homoeo Clinic"
git push heroku main

REM Open the app
echo 🌐 Opening your deployed application...
heroku open

echo ✅ Deployment completed successfully!
echo 📱 Your app is now live!
echo 🔑 Default login credentials:
echo    Username: drpriya
echo    Password: password123
echo.
echo ⚠️  IMPORTANT: Change the default credentials in production!
pause 