# 🚀 IntelliMail Deployment Guide

## Deployment Architecture
- **Frontend**: Vercel (React.js)
- **Backend**: Render (FastAPI)

## 🐍 Backend Deployment (Render)

### 1. Sign Up & Connect
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 2. Create Web Service
1. Click "New +" → "Web Service"
2. Connect your IntelliMail repository
3. Configure:
   - **Name**: `intellimail-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon` (free tier)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables (Critical!)
Add these in Render dashboard:

```env
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
GOOGLE_CLIENT_ID=your-google-client-id.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret
JWT_SECRET_KEY=your-jwt-secret-key-here
ENVIRONMENT=production
GOOGLE_REDIRECT_URI=https://intellimail-backend.onrender.com/auth/callback
PORT=10000
```

### 4. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Note your URL: `https://intellimail-backend.onrender.com`
- Test: Visit `https://intellimail-backend.onrender.com/health`

## ⚡ Frontend Deployment (Vercel)

### 1. Sign Up & Import
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your IntelliMail repository

### 2. Configure Project
- **Framework Preset**: Create React App
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 3. Environment Variables
Add in Vercel dashboard:

```env
REACT_APP_API_URL=https://intellimail-backend.onrender.com
NODE_ENV=production
```

### 4. Deploy
- Click "Deploy"
- Wait 3-5 minutes
- Note your URL: `https://intellimail-abc123.vercel.app`

## 🔐 Update Google OAuth

### Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add Authorized Redirect URIs:
   ```
   https://intellimail-backend.onrender.com/auth/callback
   ```
4. Update OAuth Consent Screen:
   - Authorized domains: `vercel.app`, `onrender.com`

## 🔄 Update CORS After Deployment

Once you have your Vercel URL, update `backend/main.py`:

```python
allowed_origins = [
    "https://your-actual-vercel-url.vercel.app",  # Replace with real URL
    "https://*.vercel.app",  # All Vercel previews
]
```

Commit and push to redeploy.

## ✅ Testing Checklist

- [ ] Backend health: `https://your-backend.onrender.com/health`
- [ ] Frontend loads: `https://your-frontend.vercel.app`
- [ ] API docs: `https://your-backend.onrender.com/docs`
- [ ] Google login works
- [ ] Email features work

## 💰 Free Tier Limits

### Render Free:
- 750 hours/month
- Spins down after 15 min inactivity
- 512MB RAM

### Vercel Free:
- 100GB bandwidth/month
- Unlimited deployments
- Global CDN

## 🚨 Troubleshooting

### Build Errors on Render:
If you see "metadata-generation-failed" errors:
1. Use the updated requirements.txt with compatible versions
2. Try the alternative requirements-render.txt file
3. Set Python version to 3.9.18 in environment variables
4. Add `PIP_DISABLE_PIP_VERSION_CHECK=1` environment variable

### CORS Errors:
- Check exact frontend URL in backend CORS config
- Ensure no trailing slashes

### Cold Starts:
- First request may take 10-30 seconds
- Consider keep-alive pings

### Environment Variables:
- Double-check all keys are set correctly
- Restart services after updating

---

**Total Deployment Time**: ~15-20 minutes
**Difficulty**: ⭐⭐ Easy
