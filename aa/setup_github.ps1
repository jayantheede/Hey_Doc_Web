Write-Host "🚀 Setting up GitHub repository for Aastha Homoeo Clinic..." -ForegroundColor Green

# Check if git is available
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not found. Please restart your computer or open a new command prompt." -ForegroundColor Red
    Write-Host "Git was installed but needs a system restart to be available." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📁 Initializing Git repository..." -ForegroundColor Cyan
git init

Write-Host "📝 Adding files to repository..." -ForegroundColor Cyan
git add .

Write-Host "💾 Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit - Aastha Homoeo Clinic Hospital Management System"

Write-Host "🔗 Adding GitHub remote..." -ForegroundColor Cyan
git remote add origin https://github.com/jayantheede/Hey_Doc_Web.git

Write-Host "🌿 Setting main branch..." -ForegroundColor Cyan
git branch -M main

Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "📱 Your repository is now available at: https://github.com/jayantheede/Hey_Doc_Web" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Your Aastha Homoeo Clinic project is now on GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your repository: https://github.com/jayantheede/Hey_Doc_Web" -ForegroundColor White
Write-Host "2. Set up deployment using the deployment guide" -ForegroundColor White
Write-Host "3. Share your repository with others" -ForegroundColor White

Read-Host "Press Enter to continue" 