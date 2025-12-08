# 🚀 Quick Deployment Guide

## Current Status
✅ Frontend: Deployed to Vercel (environment variable not set yet)
⏳ Backend: Ready to deploy (needs PostgreSQL database)

## Next Steps

### 1. Deploy Backend First (Required)

**Why?** You need the backend URL before setting the frontend environment variable.

#### Quick Setup:

1. **Get a free PostgreSQL database:**
   - Go to [Neon.tech](https://neon.tech) (recommended - easiest)
   - Sign up (free)
   - Create database
   - Copy connection string

2. **Deploy backend to Vercel:**
   ```bash
   cd backend
   vercel login
   vercel
   ```
   - When asked for root directory: `.` (current)
   - Add environment variables:
     - `DATABASE_URL` = your PostgreSQL connection string
     - `DEEPSEEK_API_KEY` = your DeepSeek key
     - `CORS_ORIGINS` = `https://your-frontend.vercel.app`
     - `ENVIRONMENT` = `production`

3. **Get your backend URL:**
   - After deployment, you'll get: `https://your-backend.vercel.app`
   - Test it: `https://your-backend.vercel.app/api/health`

### 2. Set Frontend Environment Variable

1. Go to Vercel Dashboard → Your Frontend Project
2. Settings → Environment Variables
3. Add: `VITE_API_BASE_URL` = `https://your-backend.vercel.app`
4. Redeploy frontend

### 3. Test Everything

- Frontend: `https://your-frontend.vercel.app`
- Backend API: `https://your-backend.vercel.app/api/docs`
- Health check: `https://your-backend.vercel.app/api/health`

## ⚠️ Important Notes

1. **Database Required:** SQLite won't work in serverless. You MUST use PostgreSQL.
2. **Two Separate Projects:** Frontend and backend are separate Vercel projects.
3. **Environment Variables:** Set them in Vercel Dashboard, not in code.

## 📚 Full Documentation

- Backend deployment: See `backend/VERCEL_DEPLOYMENT.md`
- Frontend is already configured in root `vercel.json`

## 🆘 Common Issues

**Backend won't deploy?**
- Make sure you're in the `backend` directory
- Check that `api/index.py` exists
- Verify `vercel.json` is in backend folder

**Database connection fails?**
- Verify PostgreSQL connection string is correct
- Check if database allows external connections
- Some free databases need IP whitelisting

**CORS errors?**
- Make sure `CORS_ORIGINS` includes your frontend URL
- URLs must match exactly (including https://)
