#!/bin/bash

# Aastha Homoeo Clinic - Deployment Script
echo "🚀 Starting deployment of Aastha Homoeo Clinic..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "⚠️  Heroku CLI is not installed. Installing..."
    # For Windows, download from https://devcenter.heroku.com/articles/heroku-cli
    echo "Please download and install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - Aastha Homoeo Clinic"
fi

# Create Heroku app
echo "🔧 Creating Heroku app..."
read -p "Enter your Heroku app name (or press Enter for auto-generated name): " app_name

if [ -z "$app_name" ]; then
    heroku create
else
    heroku create $app_name
fi

# Get the app name from Heroku
APP_NAME=$(heroku apps:info --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
echo "✅ Heroku app created: $APP_NAME"

# Set environment variables
echo "🔐 Setting environment variables..."
read -p "Enter your MongoDB connection string: " mongodb_uri
read -p "Enter a strong secret key for Flask: " secret_key

heroku config:set MONGODB_URI="$mongodb_uri"
heroku config:set SECRET_KEY="$secret_key"

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy Aastha Homoeo Clinic"
git push heroku main

# Open the app
echo "🌐 Opening your deployed application..."
heroku open

echo "✅ Deployment completed successfully!"
echo "📱 Your app is now live at: https://$APP_NAME.herokuapp.com"
echo "🔑 Default login credentials:"
echo "   Username: drpriya"
echo "   Password: password123"
echo ""
echo "⚠️  IMPORTANT: Change the default credentials in production!" 