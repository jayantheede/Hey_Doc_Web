# Push to GitHub Script for Aastha Homoeo Clinic
Write-Host "🚀 Pushing Aastha Homoeo Clinic to GitHub..." -ForegroundColor Green

# Check if git is available
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not available. Please restart your computer or open a new command prompt." -ForegroundColor Red
    Write-Host "Alternative: Use GitHub Desktop or web interface" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if repository is already initialized
if (Test-Path ".git") {
    Write-Host "📁 Git repository already exists" -ForegroundColor Cyan
} else {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Cyan
    git init
}

# Add all files
Write-Host "📝 Adding files to repository..." -ForegroundColor Cyan
git add .

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    Write-Host "💾 Creating commit..." -ForegroundColor Cyan
    git commit -m "Update Aastha Homoeo Clinic - Hospital Management System"
} else {
    Write-Host "ℹ️  No changes to commit" -ForegroundColor Yellow
}

# Check if remote origin exists
$remotes = git remote -v
if ($remotes -match "origin") {
    Write-Host "🔗 Remote origin already exists" -ForegroundColor Cyan
} else {
    Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Cyan
    git remote add origin https://github.com/jayantheede/Hey_Doc_Web.git
}

# Set main branch
Write-Host "🌿 Setting main branch..." -ForegroundColor Cyan
git branch -M main

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
try {
    git push -u origin main
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "📱 Your repository: https://github.com/jayantheede/Hey_Doc_Web" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error pushing to GitHub. Please check your credentials." -ForegroundColor Red
    Write-Host "💡 You may need to authenticate with GitHub first." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Your Aastha Homoeo Clinic project is now on GitHub!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit: https://github.com/jayantheede/Hey_Doc_Web" -ForegroundColor White
Write-Host "2. Set up deployment using DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host "3. Deploy your website to a live server" -ForegroundColor White

Read-Host "Press Enter to continue" 