# Telegram Bot Knowledge Base - Vercel Deployment

This directory contains the Vercel-ready deployment of the Telegram Bot Knowledge Base system.

## Quick Deploy to Vercel

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub

1. **Push to GitHub**
   - Create a new repository on GitHub
   - Push this directory to the repository

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically detect and deploy

### Option 3: Deploy via Vercel Dashboard

1. **Zip the deployment directory**
   ```bash
   zip -r telegram-bot-vercel.zip .
   ```

2. **Upload to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Upload the zip file

## Environment Variables

Set these environment variables in your Vercel project settings:

- `SECRET_KEY`: A secure secret key for Flask sessions
- `DATABASE_URL`: (Optional) PostgreSQL database URL for production
- `ENCRYPTION_KEY`: Key for encrypting bot tokens

## Post-Deployment Setup

1. **Access your deployed application**
   - Vercel will provide a URL like `https://your-project.vercel.app`

2. **Create your first bot**
   - Open the dashboard
   - Click "Create New Bot"
   - Enter your Telegram bot token from @BotFather

3. **Upload knowledge base documents**
   - Go to Knowledge Base section
   - Create a knowledge base
   - Upload PDF, TXT, DOCX, or MD files

## Features

- ✅ Serverless deployment on Vercel
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Zero-config deployment
- ✅ Automatic scaling

## File Structure

```
vercel-deployment/
├── api/
│   ├── index.py          # Vercel entry point
│   └── src/              # Application source code
│       ├── main.py       # Flask application
│       ├── models/       # Database models
│       ├── routes/       # API routes
│       ├── services/     # Business logic
│       └── static/       # Frontend files
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all imports use relative paths
   - Check that all dependencies are in requirements.txt

2. **Database Issues**
   - SQLite is used by default (stored in /tmp)
   - For production, set DATABASE_URL to a PostgreSQL database

3. **File Upload Issues**
   - Vercel has a 50MB limit for serverless functions
   - Consider using external storage for large files

### Support

For deployment issues:
- Check Vercel deployment logs
- Verify environment variables are set
- Ensure all files are included in the deployment

## Production Considerations

1. **Database**: Use PostgreSQL for production (set DATABASE_URL)
2. **File Storage**: Consider using AWS S3 or similar for file uploads
3. **Monitoring**: Set up error tracking and monitoring
4. **Security**: Ensure all environment variables are properly set

Your Telegram Bot Knowledge Base is now ready for deployment on Vercel!

