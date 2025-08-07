# 🚀 Deployment Guide - Aastha Homoeo Clinic

Your Flask application is ready for deployment! Here are the steps to get your website live on the internet.

## 📋 Prerequisites

1. **Git** - Download from https://git-scm.com/
2. **Heroku CLI** - Download from https://devcenter.heroku.com/articles/heroku-cli
3. **MongoDB Atlas Account** - Free tier available at https://www.mongodb.com/atlas

## 🎯 Quick Deployment Options

### Option 1: Automated Deployment (Recommended)

**For Windows users:**
```bash
# Run the automated deployment script
deploy.bat
```

**For Mac/Linux users:**
```bash
# Make the script executable and run it
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Deployment

#### Step 1: Prepare Your Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit - Aastha Homoeo Clinic"
```

#### Step 2: Create Heroku App
```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name
```

#### Step 3: Set Environment Variables
```bash
# Set MongoDB connection string
heroku config:set MONGODB_URI="your-mongodb-connection-string"

# Set Flask secret key
heroku config:set SECRET_KEY="your-strong-secret-key"
```

#### Step 4: Deploy
```bash
# Deploy to Heroku
git push heroku main

# Open your app
heroku open
```

## 🔧 Alternative Deployment Platforms

### Railway (Recommended Alternative)
1. Go to https://railway.app/
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy automatically

### Render
1. Go to https://render.com/
2. Create a new Web Service
3. Connect your GitHub repository
4. Set environment variables
5. Deploy

### Vercel
1. Go to https://vercel.com/
2. Import your GitHub repository
3. Configure build settings
4. Deploy

## 🔐 Security Setup

### 1. Generate Strong Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Update MongoDB Connection
- Use MongoDB Atlas with proper authentication
- Enable IP whitelist for security
- Use strong passwords

### 3. Change Default Credentials
After deployment, update the default doctor credentials in your database:
- Username: `drpriya`
- Password: `password123`

## 📱 Your Application Features

Once deployed, your website will have:

✅ **Public Homepage** - Professional clinic information
✅ **Doctor Dashboard** - Appointment and prescription management
✅ **Patient Management** - Add, edit, and search patients
✅ **Prescription System** - Create and print prescriptions
✅ **Time Slot Booking** - Intelligent appointment scheduling
✅ **Mobile Responsive** - Works on all devices

## 🌐 Access Your Live Website

After deployment, your website will be available at:
- **Heroku**: `https://your-app-name.herokuapp.com`
- **Railway**: `https://your-app-name.railway.app`
- **Render**: `https://your-app-name.onrender.com`

## 🔍 Testing Your Deployment

1. **Visit your homepage** - Should show clinic information
2. **Test doctor login** - Use default credentials
3. **Create an appointment** - Test the booking system
4. **Add a prescription** - Test the prescription feature
5. **Print a prescription** - Test the print functionality

## 🆘 Troubleshooting

### Common Issues:

1. **Build fails**: Check your `requirements.txt` file
2. **Database connection error**: Verify MongoDB URI
3. **App crashes**: Check Heroku logs with `heroku logs --tail`
4. **Static files not loading**: Ensure all files are committed to git

### Get Help:
- Check Heroku logs: `heroku logs --tail`
- View app status: `heroku ps`
- Restart app: `heroku restart`

## 🎉 Congratulations!

Your Aastha Homoeo Clinic website is now live and ready to serve patients!

**Next Steps:**
1. Update the clinic information on the homepage
2. Change default login credentials
3. Add your clinic's contact information
4. Customize the design if needed
5. Set up a custom domain (optional)

---

**Need help?** Check the main README.md file for detailed documentation. 